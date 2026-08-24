#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest: VOICE MODE (cosmos_voice over cosmos_convo + cosmos_itc).

The claims under test are the safety claims, because voice is the channel where
a misheard word costs the most:
  * read-only commands auto-run; CONSEQUENTIAL commands NEVER run without the
    confirm round-trip - and the confirm_id is a SERVER-ISSUED SINGLE-USE
    NONCE: a guessed/derived token (including the old deterministic
    sha256(sid|text)[:12]) never executes, a consumed nonce never executes
    twice, an expired nonce re-prompts, a nonce issued for another session or
    utterance re-prompts;
  * destructive verbs are refused LOCALLY - the commander is NEVER dispatched
    (defense in depth: nothing is sent downstream hoping a fence catches it);
  * dictation is captured as EXACTLY ONE note turn, never approximated into a
    command and never double-recorded;
  * an oversized transcript is BAD_INPUT before anything touches the chain;
  * queries return ITC hits WITH provenance (index_hash); unknown keys surface
    NOT_FOUND in-band;
  * and the whole exchange is SESSION-CONTINUOUS: every turn lands in the
    ConvoStore in order - the sid, not the handset, carries the conversation.

Real ConvoStore + real ITC (fake injected fetcher, refreshed) + a FAKE
commander that records calls and returns canned dicts - VoiceMode never needs
the kernel, and this test proves it by never importing it."""
from __future__ import annotations

import hashlib
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cosmos_ledger import Ledger
from cosmos_convo import ConvoStore
from cosmos_itc import ITC
from cosmos_voice import (VoiceMode, VoiceError, CONFIRM_TTL, MAX_TRANSCRIPT,
                          SPOKEN_MAX, EV_CONFIRM_ISSUED, EV_CONFIRM_CONSUMED)

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


def legacy_token(sid: str, transcript: str) -> str:
    """The RETIRED deterministic confirm token - what an attacker who knows
    sid+text can compute. The suite proves it executes NOTHING."""
    norm = " ".join(transcript.split()).lower()
    return hashlib.sha256(f"{sid}|{norm}".encode("utf-8")).hexdigest()[:12]


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
    for unconfirmed and destructive utterances. `calls` holds EVERYTHING that
    reached the seam - the set that must stay empty for destructive verbs now
    that the refusal is local."""

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


class FakeAsker:
    """Records every (question, model) call; returns a canned answer dict.
    Never touches a network or a wallet - the seam under test is VoiceMode's
    routing, refusal honesty, and provenance recording."""

    def __init__(self, text="The UPS work function here is 4.36 eV.",
                 usd=0.0123):
        self.calls = []
        self.text = text
        self.usd = usd

    def __call__(self, question, model=None):
        self.calls.append((question, model))
        return {"text": self.text, "model": model or "grok-4.5",
                "usd": self.usd}


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

    convo_ledger = Ledger(td / "convo.jsonl", KEY, "voice", clock=clock)
    convo = ConvoStore(convo_ledger, clock=clock)
    itc = ITC(Ledger(td / "itc.jsonl", KEY, "voice", clock=clock),
              fetcher=lambda url: CSV, clock=clock)
    itc.refresh()
    itc.register_corpus([r"V:\Research4\Ai\notes\manifest_notes.txt"])
    cmd = FakeCommander()
    vm = VoiceMode(convo, cmd, itc, clock=clock)

    sid = convo.create_session("road session", scope=["itc", "corpus"])

    def confirm_events(kind):
        return [r["payload"] for r in convo_ledger.verify()
                if r["event"] == kind]

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
    check("consequential 'submit ...' -> needs_confirm=True, a NONCE minted",
          lambda: r2["needs_confirm"] and isinstance(r2["confirm_id"], str)
          and len(r2["confirm_id"]) == 32
          and all(c in "0123456789abcdef" for c in r2["confirm_id"]))
    check("...and the commander was NOT called (nothing executed on first hearing)",
          lambda: len(cmd.executed) == n_exec and "submit high do the thing"
          not in cmd.calls)
    check("...the nonce is NOT the old deterministic token (unforgeable, "
          "server-issued)",
          lambda: r2["confirm_id"] != legacy_token(sid, "submit high do the thing"))
    check("...CONFIRM_ISSUED is ON THE LEDGER {nonce, sid, cmd_hash, epoch}",
          lambda: any(p.get("nonce") == r2["confirm_id"] and p.get("sid") == sid
                      and len(p.get("cmd_hash", "")) == 64
                      and p.get("epoch") == 5000.0
                      for p in confirm_events(EV_CONFIRM_ISSUED)))

    # ===== THE FORGERY ATTACK: guessed deterministic token NEVER executes =====
    r3 = vm.handle(sid, "submit high do the thing",
                   confirm_id=legacy_token(sid, "submit high do the thing"))
    check("ATTACK: sid+text-derived (old deterministic) confirm_id -> re-prompt, "
          "NOT an execution",
          lambda: r3["needs_confirm"] and len(cmd.executed) == n_exec
          and "submit high do the thing" not in cmd.calls)
    check("...the re-prompt says the mismatch out loud (nothing silent)",
          lambda: "did not match" in r3["reply"])
    check("...and re-prompts with a FRESH nonce, different from the first",
          lambda: isinstance(r3["confirm_id"], str)
          and r3["confirm_id"] != r2["confirm_id"])

    # ===== correct nonce: NOW it executes, exactly once =====
    r4 = vm.handle(sid, "submit high do the thing", confirm_id=r2["confirm_id"])
    check("re-call WITH the issued nonce EXECUTES (commander called once)",
          lambda: not r4["needs_confirm"] and r4["ok"]
          and cmd.executed.count("submit high do the thing") == 1)
    check("...reply names what ran (the action is on the record, not implied)",
          lambda: r4["action"] == "submit high do the thing"
          and "JOB-FAKE-1" in r4["reply"])
    check("...CONFIRM_CONSUMED is ON THE LEDGER for that nonce",
          lambda: any(p.get("nonce") == r2["confirm_id"]
                      for p in confirm_events(EV_CONFIRM_CONSUMED)))

    # ===== SINGLE-USE: replaying the consumed nonce never executes again =====
    r4b = vm.handle(sid, "submit high do the thing", confirm_id=r2["confirm_id"])
    check("REPLAY: the consumed nonce re-prompts - still exactly ONE execution",
          lambda: r4b["needs_confirm"]
          and cmd.executed.count("submit high do the thing") == 1
          and "already used" in r4b["reply"])

    # ===== TTL: an expired nonce re-prompts; a fresh one still executes =====
    rE1 = vm.handle(sid, "session close")
    check("second consequential verb ('session close') -> its own nonce",
          lambda: rE1["needs_confirm"] and rE1["confirm_id"] not in
          (r2["confirm_id"], r3["confirm_id"]))
    fake_t[0] = 5000.0 + CONFIRM_TTL + 1.0          # past the TTL
    rE2 = vm.handle(sid, "session close", confirm_id=rE1["confirm_id"])
    check("EXPIRED nonce (TTL exceeded via injected clock) -> re-prompt, "
          "NOT an execution",
          lambda: rE2["needs_confirm"] and "expired" in rE2["reply"]
          and "session close" not in cmd.executed)
    rE3 = vm.handle(sid, "session close", confirm_id=rE2["confirm_id"])
    check("...the FRESH nonce from the re-prompt executes (flow recovers)",
          lambda: not rE3["needs_confirm"] and rE3["ok"]
          and cmd.executed.count("session close") == 1)

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

    # ===== dictation: captured as EXACTLY ONE note turn =====
    n_calls = len(cmd.calls)
    r8 = vm.handle(sid, "remember the sky is blue")
    check("dictation -> kind=dictation, acknowledged as captured",
          lambda: r8["ok"] and r8["kind"] == "dictation"
          and "noted" in r8["reply"].lower())
    check("...the dictation is recorded EXACTLY ONCE (double-record closed), "
          "as mode='note'",
          lambda: [t["mode"] for t in convo.get_session(sid)["turns"]
                   if t["text"] == "remember the sky is blue"] == ["note"])
    check("...NO command ran and none was guessed at (commander untouched)",
          lambda: len(cmd.calls) == n_calls)

    # ===== destructive: refused LOCALLY, commander NEVER dispatched =====
    n_calls2, n_exec2 = len(cmd.calls), len(cmd.executed)
    r9 = vm.handle(sid, "delete everything")
    check("'delete everything' -> kind=refused, refused=True, error=REFUSED",
          lambda: r9["kind"] == "refused" and r9["refused"]
          and not r9["ok"] and r9.get("error") == "REFUSED")
    check("...the commander was NEVER DISPATCHED (defense in depth: nothing "
          "sent hoping a downstream fence holds)",
          lambda: len(cmd.calls) == n_calls2 and len(cmd.executed) == n_exec2
          and "delete everything" not in cmd.calls)
    check("...the LOCAL refusal is ledgered (COMMAND_REFUSED, via='voice')",
          lambda: any(r["event"] == "COMMAND_REFUSED"
                      and r["payload"].get("text") == "delete everything"
                      and r["payload"].get("via") == "voice"
                      for r in convo_ledger.verify()))

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
              "submit high do the thing",           # forged/legacy confirm
              "submit high do the thing",           # confirmed (nonce)
              "submit high do the thing",           # replayed consumed nonce
              "session close",                      # first hearing
              "session close",                      # expired nonce
              "session close",                      # fresh nonce, ran
              "search manifest", "find fig1",
              "open figures/fig1.png", "open no/such/key.bin",
              "delete everything", "events banana"])
    check("...every utterance has an assistant reply turn (user/assistant paired)",
          lambda: sum(1 for t in turns if t["role"] == "assistant") == 15)
    check("...a SECOND ConvoStore on the same ledger sees the same conversation "
          "(reconnect IS resume)",
          lambda: ConvoStore(Ledger(td / "convo.jsonl", KEY, "phone2",
                                    clock=clock), clock=clock)
          .get_session(sid)["turn_count"] == len(turns))

    # ===== cross-session binding: a nonce is bound to ITS sid =====
    sid2 = convo.create_session("second handset")
    rX1 = vm.handle(sid2, "submit other thing")
    rX2 = vm.handle(sid, "submit other thing", confirm_id=rX1["confirm_id"])
    check("a nonce issued in ANOTHER session re-prompts here - never executes",
          lambda: rX1["needs_confirm"] and rX2["needs_confirm"]
          and "submit other thing" not in cmd.executed
          and "different request" in rX2["reply"])
    rX3 = vm.handle(sid2, "submit other thing", confirm_id=r3["confirm_id"])
    check("a nonce issued for a DIFFERENT utterance re-prompts - never executes",
          lambda: rX3["needs_confirm"]
          and "submit other thing" not in cmd.executed)

    # ===== ledger bookkeeping of the whole confirm history =====
    check("confirm bookkeeping: 8 CONFIRM_ISSUED, exactly 2 CONFIRM_CONSUMED",
          lambda: (len(confirm_events(EV_CONFIRM_ISSUED)),
                   len(confirm_events(EV_CONFIRM_CONSUMED))) == (8, 2))

    # ===== ASK: injected asker - routing, provenance, honest refusals =====
    fa = FakeAsker()
    va = VoiceMode(convo, cmd, itc, asker=fa, clock=clock)
    sida = convo.create_session("ask session")
    n_cmd = len(cmd.calls)
    rA = va.handle(sida, "ask what is the ups work function")
    check("'ask <q>' -> kind=ask, ok, the model's ANSWER is the reply",
          lambda: rA["ok"] and rA["kind"] == "ask" and rA["reply"] == fa.text
          and not rA["needs_confirm"] and not rA["refused"])
    check("...routed to the asker ONCE, question intact, DEFAULT model (None)",
          lambda: fa.calls == [("what is the ups work function", None)])
    check("...spoken is the answer in TTS form (nonempty, bounded)",
          lambda: rA["spoken"].startswith("The UPS work function")
          and 0 < len(rA["spoken"]) <= SPOKEN_MAX + 4)
    check("...provenance names the model AND the spend (auditable turn)",
          lambda: rA["sources"] == ["model:grok-4.5", "usd:0.012300"])
    check("...both turns recorded: user utterance + assistant answer w/ sources",
          lambda: (lambda s: [t["role"] for t in s["turns"]]
                   == ["user", "assistant"]
                   and s["turns"][1]["text"] == fa.text
                   and "model:grok-4.5" in s["sources"]
                   and "usd:0.012300" in s["sources"])
          (convo.get_session(sida)))
    check("...ask is NOT a command: the commander was never involved, and no "
          "confirm nonce was minted (spend gating lives in the asker)",
          lambda: len(cmd.calls) == n_cmd and rA["confirm_id"] is None)

    va.handle(sida, "ask grok is xps surface sensitive")
    check("'ask grok <q>' selects grok; the alias is stripped from the question",
          lambda: fa.calls[-1] == ("is xps surface sensitive", "grok"))
    va.handle(sida, "ask gpt summarize chapter four")
    check("'ask gpt <q>' routes to canonical 'openai'",
          lambda: fa.calls[-1] == ("summarize chapter four", "openai"))
    va.handle(sida, "ask sgh what is on x today")
    check("'ask sgh <q>' routes to grok (sgh IS the Grok rail)",
          lambda: fa.calls[-1] == ("what is on x today", "grok"))
    rB3 = va.handle(sida, "ask about the beamline schedule")
    check("an unknown 2nd word is QUESTION TEXT, not a guessed model route",
          lambda: rB3["ok"]
          and fa.calls[-1] == ("about the beamline schedule", None))

    nq = len(fa.calls)
    rB4 = va.handle(sida, "ask")
    check("'ask' with no question -> in-band prompt, asker NOT called (no spend)",
          lambda: (not rB4["ok"]) and len(fa.calls) == nq)

    # asker=None -> refused IN-BAND, mirroring itc=None; nothing fabricated
    v_none = VoiceMode(convo, cmd, itc, asker=None, clock=clock)
    rC = v_none.handle(sida, "ask what is the meaning of life")
    check("asker=None -> kind=refused, ASK_UNAVAILABLE, never a crash",
          lambda: rC["kind"] == "refused" and rC["refused"] and not rC["ok"]
          and rC.get("error") == "ASK_UNAVAILABLE"
          and "nothing was spent" in rC["reply"])
    check("...and NO assistant turn carries a fabricated answer",
          lambda: all("meaning of life" not in t["text"]
                      for t in convo.get_session(sida)["turns"]
                      if t["role"] == "assistant"))

    # a RAISING asker (the spend gate saying DENIED) -> in-band, reason kept
    class DeniedError(RuntimeError):
        kind = "DENIED"

    def deny(question, model=None):
        raise DeniedError("worst case would pass the cap")
    v_deny = VoiceMode(convo, cmd, itc, asker=deny, clock=clock)
    rD = v_deny.handle(sida, "ask an expensive question")
    check("a RAISING asker (spend DENIED) -> in-band refusal CARRYING the kind",
          lambda: rD["kind"] == "refused" and not rD["ok"]
          and rD.get("error") == "DENIED" and "DENIED" in rD["reply"])
    check("...the recorded assistant turn is the refusal, not a fake answer",
          lambda: convo.get_session(sida)["turns"][-1]["text"]
          .startswith("[DENIED]"))

    # a not-ok return is the same refusal - an absent answer is never invented
    v_notok = VoiceMode(convo, cmd, itc,
                        asker=lambda q, m=None: {"ok": False,
                                                 "detail": "rail unreachable"},
                        clock=clock)
    rE = v_notok.handle(sida, "ask anything at all")
    check("a not-ok asker return -> refused ASK_FAILED with the detail",
          lambda: rE["kind"] == "refused" and rE.get("error") == "ASK_FAILED"
          and "rail unreachable" in rE["reply"])

    # the question inherits the MAX_TRANSCRIPT cap at the door
    expect("oversized ask -> BAD_INPUT (the transcript cap bounds the question)",
           "BAD_INPUT", lambda: va.handle(sida, "ask " + "x" * MAX_TRANSCRIPT))

    # ===== typed refusals: BAD_INPUT and NO_SESSION =====
    n_all = convo.get_session(sid)["turn_count"]
    expect("empty transcript -> BAD_INPUT (typed, before anything is recorded)",
           "BAD_INPUT", lambda: vm.handle(sid, "   "))
    expect("non-string transcript -> BAD_INPUT too",
           "BAD_INPUT", lambda: vm.handle(sid, None))
    expect("transcript over MAX_TRANSCRIPT chars -> BAD_INPUT (no ledger "
           "write amplification)",
           "BAD_INPUT", lambda: vm.handle(sid, "x" * (MAX_TRANSCRIPT + 1)))
    expect("bogus session_id -> NO_SESSION (convo's refusal, surfaced typed)",
           "NO_SESSION", lambda: vm.handle("no-such-sid", "status"))
    check("...and the refused calls left NO new turns in the real session",
          lambda: convo.get_session(sid)["turn_count"] == n_all)

    # ===== the chains verify end-to-end after everything =====
    check("convo ledger chain VERIFIES after the whole exchange",
          lambda: (lambda recs: [r["seq"] for r in recs]
                   == list(range(1, len(recs) + 1)))
          (list(Ledger(td / "convo.jsonl", KEY, "aud", clock=clock).verify())))

    bad = [(l, e) for l, ok, e in RESULTS if not ok]
    for label, ok, err in RESULTS:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label,
                              ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks (voice is session-continuous; confirm is a "
          "ledger-backed single-use nonce; destructive verbs never dispatch; "
          "ask is injected, spend-audited, and refuses honestly)"
          % ("PASS" if not bad else "FAIL", len(RESULTS)))
    return 0 if not bad else 1


def test_voice():
    assert main() == 0


if __name__ == "__main__":
    sys.exit(main())
