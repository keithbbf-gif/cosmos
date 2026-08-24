#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest: VOICE MODE (cosmos_voice over cosmos_convo + cosmos_itc).

The claims under test are the safety claims, because voice is the channel where
a misheard word costs the most:
  * read-only commands auto-run; CONSEQUENTIAL commands NEVER run without the
    confirm round-trip; a wrong/stale confirm_id never executes;
  * destructive verbs are refused (via the commander's fence), never executed;
  * dictation is captured as a note, never approximated into a command;
  * queries return ITC hits WITH provenance (index_hash); unknown keys surface
    NOT_FOUND in-band;
  * and the whole exchange is SESSION-CONTINUOUS: every turn lands in the
    ConvoStore in order - the sid, not the handset, carries the conversation.

Real ConvoStore + real ITC (fake injected fetcher, refreshed) + a FAKE
commander that records calls and returns canned dicts - VoiceMode never needs
the kernel, and this test proves it by never importing it."""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cosmos_ledger import Ledger
from cosmos_convo import ConvoStore
from cosmos_itc import ITC
from cosmos_voice import VoiceMode, VoiceError, _confirm_token

RESULTS = []


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:                                            # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


def expect(label, kind, fn):
    """fn must raise VoiceError with .kind == kind - typed errors ONLY."""
    def _run():
        try:
            fn()
        except VoiceError as e:
            return e.kind == kind
        except Exception:                                             # noqa: BLE001
            return False   # a bare exception escaping the API is a FAIL
        return False       # not raising at all is a FAIL
    check(label, _run)


# ---------------- the fake commander (canned, call-recording) ----------------
class FakeCmdError(RuntimeError):
    """Duck-typed like cosmos_command.CommandError: carries .kind."""

    def __init__(self, kind, detail):
        self.kind = kind
        super().__init__(f"{kind}: {detail}")


FORBIDDEN = {"delete", "remove", "rm", "del", "rmdir", "format", "purge",
             "reset", "drop", "overwrite", "force", "wipe", "erase",
             "destroy", "truncate", "uninstall"}


class FakeCommander:
    """Records every .handle() call; refuses FORBIDDEN verbs exactly like the
    real Commander's fence; returns canned dicts otherwise. `executed` holds
    only the calls that actually RETURNED - the set VoiceMode must keep empty
    for unconfirmed and destructive utterances."""

    def __init__(self):
        self.calls = []        # every text that reached handle()
        self.executed = []     # every text that handle() completed (returned)

    def handle(self, text):
        self.calls.append(text)
        verb = text.split()[0].lower() if text.split() else ""
        if verb in FORBIDDEN:
            raise FakeCmdError("REFUSED",
                               "destructive verbs are not exposed to the "
                               "command seam by design")
        if verb == "submit":
            out = {"ok": True, "job_id": "JOB-FAKE-1"}
        elif verb == "status":
            out = {"ok": True, "ready": True, "root": "V:/A/Ai/COSMOS"}
        elif verb == "events":
            raise FakeCmdError("BAD_ARGS", "'banana' is not a count")
        else:
            out = {"ok": True, "verb": verb}
        self.executed.append(text)
        return out


CSV = (
    "object_key,url,area,type,size_bytes,descriptor\n"
    "00_INDEX/MASTER_FILE_MANIFEST.csv,https://ai.dchambers.com/00_INDEX/"
    "MASTER_FILE_MANIFEST.csv,index,csv,120000,master manifest of every published file\n"
    "00_INDEX/manifest_UPS_DATA_XY.csv,https://ai.dchambers.com/00_INDEX/"
    "manifest_UPS_DATA_XY.csv,index,csv,9000,per-directory manifest UPS DATA XY\n"
    "figures/fig1.png,https://ai.dchambers.com/figures/fig1.png,figures,png,"
    "51234,chapter four calibration figure one\n"
)


def main() -> int:
    td = Path(tempfile.mkdtemp(prefix="cosmos_voice_"))
    KEY = b"k"
    fake_t = [5000.0]
    clock = lambda: fake_t[0]                                         # noqa: E731

    convo = ConvoStore(Ledger(td / "convo.jsonl", KEY, "voice", clock=clock),
                       clock=clock)
    itc = ITC(Ledger(td / "itc.jsonl", KEY, "voice", clock=clock),
              fetcher=lambda url: CSV, clock=clock)
    itc.refresh()
    itc.register_corpus([r"V:\Research4\Ai\notes\manifest_notes.txt"])
    cmd = FakeCommander()
    vm = VoiceMode(convo, cmd, itc, clock=clock)

    sid = convo.create_session("road session", scope=["itc", "corpus"])

    # ===== read-only command: auto-runs, both turns recorded =====
    r = vm.handle(sid, "status")
    check("read-only 'status' auto-runs (ok, kind=command, no confirm)",
          lambda: r["ok"] and r["kind"] == "command"
          and not r["needs_confirm"] and not r["refused"])
    check("...the fake commander was called exactly once, with the transcript",
          lambda: cmd.executed == ["status"])
    check("...user turn AND assistant turn recorded in the convo (2 turns)",
          lambda: [t["role"] for t in convo.get_session(sid)["turns"]]
          == ["user", "assistant"])
    check("...the user turn carries mode='voice' and the exact transcript",
          lambda: convo.get_session(sid)["turns"][0]["mode"] == "voice"
          and convo.get_session(sid)["turns"][0]["text"] == "status")
    check("...spoken is a concise nonempty string",
          lambda: isinstance(r["spoken"], str) and 0 < len(r["spoken"]) < 120)

    # ===== consequential: needs_confirm first, NO execution =====
    n_exec = len(cmd.executed)
    r2 = vm.handle(sid, "submit high do the thing")
    check("consequential 'submit ...' -> needs_confirm=True, confirm_id minted",
          lambda: r2["needs_confirm"] and isinstance(r2["confirm_id"], str)
          and len(r2["confirm_id"]) == 12)
    check("...and the commander was NOT called (nothing executed on first hearing)",
          lambda: len(cmd.executed) == n_exec and "submit high do the thing"
          not in cmd.calls)
    check("...confirm_id is deterministic (session + normalized utterance)",
          lambda: r2["confirm_id"] == _confirm_token(sid, "submit  high do the thing"))

    # ===== wrong/stale confirm_id: re-prompts, NEVER executes =====
    r3 = vm.handle(sid, "submit high do the thing", confirm_id="deadbeefdead")
    check("WRONG confirm_id -> fresh needs_confirm (re-prompt), not an execution",
          lambda: r3["needs_confirm"] and len(cmd.executed) == n_exec)
    check("...the re-prompt says the mismatch out loud (nothing silent)",
          lambda: "did not match" in r3["reply"])

    # ===== correct confirm_id: NOW it executes, exactly once =====
    r4 = vm.handle(sid, "submit high do the thing", confirm_id=r2["confirm_id"])
    check("re-call WITH the minted confirm_id EXECUTES (commander called once)",
          lambda: not r4["needs_confirm"] and r4["ok"]
          and cmd.executed.count("submit high do the thing") == 1)
    check("...reply names what ran (the action is on the record, not implied)",
          lambda: r4["action"] == "submit high do the thing"
          and "JOB-FAKE-1" in r4["reply"])

    # ===== query: search with provenance =====
    r5 = vm.handle(sid, "search manifest")
    check("'search manifest' -> kind=query, ok, ITC + corpus hits returned",
          lambda: r5["ok"] and r5["kind"] == "query" and len(r5["sources"]) == 3)
    check("...EVERY ITC hit carries index_hash (provenance, measured not assumed)",
          lambda: all(h.get("index_hash") for h in r5["sources"]
                      if h.get("source") == "itc"))
    check("...corpus hits are marked source='corpus' (local file vs ITC object)",
          lambda: [h for h in r5["sources"] if h.get("source") == "corpus"]
          [0]["name"] == "manifest_notes.txt")
    check("...the assistant turn recorded the sources (provenance in the convo)",
          lambda: any("itc:00_INDEX/manifest_UPS_DATA_XY.csv@" in s
                      for s in convo.get_session(sid)["sources"]))
    r5b = vm.handle(sid, "find fig1")
    check("'find' is an alias of search (same read-only path)",
          lambda: r5b["ok"] and r5b["kind"] == "query"
          and r5b["sources"][0]["object_key"] == "figures/fig1.png")

    # ===== query: open resolves; unknown key -> NOT_FOUND in-band =====
    r6 = vm.handle(sid, "open figures/fig1.png")
    check("'open <key>' resolves via itc.get: url + index_hash in the source",
          lambda: r6["ok"] and r6["sources"][0]["url"].endswith("fig1.png")
          and r6["sources"][0]["index_hash"])
    r7 = vm.handle(sid, "open no/such/key.bin")
    check("unknown key -> NOT_FOUND surfaced CLEANLY in-band (no crash, no guess)",
          lambda: (not r7["ok"]) and r7["kind"] == "query"
          and r7.get("error") == "NOT_FOUND" and "NOT_FOUND" in r7["reply"])

    # ===== dictation: captured as a note, never approximated =====
    n_calls = len(cmd.calls)
    r8 = vm.handle(sid, "remember the sky is blue")
    check("dictation -> kind=dictation, acknowledged as captured",
          lambda: r8["ok"] and r8["kind"] == "dictation"
          and "noted" in r8["reply"].lower())
    check("...a mode='note' turn holds the dictation verbatim (session content)",
          lambda: any(t["mode"] == "note"
                      and t["text"] == "remember the sky is blue"
                      for t in convo.get_session(sid)["turns"]))
    check("...NO command ran and none was guessed at (commander untouched)",
          lambda: len(cmd.calls) == n_calls)

    # ===== destructive: refused via the commander path, nothing executes =====
    n_exec2 = len(cmd.executed)
    r9 = vm.handle(sid, "delete everything")
    check("'delete everything' -> kind=refused, refused=True, nothing executed",
          lambda: r9["kind"] == "refused" and r9["refused"]
          and not r9["ok"] and len(cmd.executed) == n_exec2)
    check("...the refusal went THROUGH the commander (its fence + its ledger path)",
          lambda: cmd.calls[-1] == "delete everything"
          and r9.get("error") == "REFUSED")

    # ===== commander's typed refusal on bad args surfaces in-band =====
    r10 = vm.handle(sid, "events banana")
    check("commander BAD_ARGS surfaces in-band, typed, never approximated",
          lambda: (not r10["ok"]) and r10.get("error") == "BAD_ARGS")

    # ===== session continuity: THE POINT - one sid, every turn, in order =====
    turns = convo.get_session(sid)["turns"]
    user_texts = [t["text"] for t in turns if t["role"] == "user"
                  and t["mode"] != "note"]
    check("session continuity: every utterance is in the convo, IN ORDER",
          lambda: user_texts == [
              "status",
              "submit high do the thing",           # first hearing
              "submit high do the thing",           # wrong confirm
              "submit high do the thing",           # confirmed
              "search manifest", "find fig1",
              "open figures/fig1.png", "open no/such/key.bin",
              "remember the sky is blue",
              "delete everything", "events banana"])
    check("...every utterance has an assistant reply turn (user/assistant paired)",
          lambda: sum(1 for t in turns if t["role"] == "assistant") == 11)
    check("...a SECOND ConvoStore on the same ledger sees the same conversation "
          "(reconnect IS resume)",
          lambda: ConvoStore(Ledger(td / "convo.jsonl", KEY, "phone2",
                                    clock=clock), clock=clock)
          .get_session(sid)["turn_count"] == len(turns))

    # ===== typed refusals: BAD_INPUT and NO_SESSION =====
    expect("empty transcript -> BAD_INPUT (typed, before anything is recorded)",
           "BAD_INPUT", lambda: vm.handle(sid, "   "))
    expect("non-string transcript -> BAD_INPUT too",
           "BAD_INPUT", lambda: vm.handle(sid, None))
    expect("bogus session_id -> NO_SESSION (convo's refusal, surfaced typed)",
           "NO_SESSION", lambda: vm.handle("no-such-sid", "status"))
    check("...and the refused calls left NO new turns in the real session",
          lambda: convo.get_session(sid)["turn_count"] == len(turns))

    # ===== the chains verify end-to-end after everything =====
    check("convo ledger chain VERIFIES after the whole exchange",
          lambda: (lambda recs: [r["seq"] for r in recs]
                   == list(range(1, len(recs) + 1)))
          (list(Ledger(td / "convo.jsonl", KEY, "aud", clock=clock).verify())))

    bad = [(l, e) for l, ok, e in RESULTS if not ok]
    for label, ok, err in RESULTS:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label,
                              ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks (voice is session-continuous, misheard "
          "consequential commands NEVER execute silently)"
          % ("PASS" if not bad else "FAIL", len(RESULTS)))
    return 0 if not bad else 1


def test_voice():
    assert main() == 0


if __name__ == "__main__":
    sys.exit(main())
