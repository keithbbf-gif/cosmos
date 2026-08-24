#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest: durable conversational sessions (cosmos_convo over cosmos_ledger).

The claim under test is the canon one: THE LEDGER IS THE AUTHORITY. A second
ConvoStore on the same chain must see the same conversation - that is what makes
a phone reconnect a RESUME instead of a restart. Plus the typed-refusal surface
(NO_SESSION / BAD_ROLE / BAD_TURN / BAD_SCOPE), dedup of sources/job_ids, the
close-then-reopen rule, and chain verification BY EVENT after everything."""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cosmos_ledger import Ledger
from cosmos_convo import ConvoStore, ConvoError

RESULTS = []


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:                                            # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


def expect(label, kind, fn):
    """fn must raise ConvoError with .kind == kind - typed errors ONLY."""
    def _run():
        try:
            fn()
        except ConvoError as e:
            return e.kind == kind
        except Exception:                                             # noqa: BLE001
            return False   # a bare exception escaping the API is a FAIL
        return False       # not raising at all is a FAIL
    check(label, _run)


def main() -> int:
    td = Path(tempfile.mkdtemp(prefix="cosmos_convo_"))
    KEY = b"k"
    lp = td / "convo.jsonl"
    fake = [1000.0]
    clock = lambda: fake[0]                                           # noqa: E731

    store = ConvoStore(Ledger(lp, KEY, "phone", clock=clock), clock=clock)

    # ===== create -> mixed-mode turns on ONE session =====
    sid = store.create_session("road trip planning", scope=["itc", "corpus"])
    check("create_session mints a uuid4-hex sid", lambda: len(sid) == 32)
    fake[0] = 1010.0
    n1 = store.append_turn(sid, "user", "what's left on the Ch4 list?",
                           mode="text", sources=["BU.MD"])
    fake[0] = 1020.0
    n2 = store.append_turn(sid, "assistant", "two K-96 blanks and the 5d cite",
                           mode="voice", sources=["BU.MD", "00_DOI_INDEX.md"],
                           job_ids=["job-7"])
    check("turn seqs are per-session and monotonic (1 then 2)",
          lambda: (n1, n2) == (1, 2))
    s = store.get_session(sid)
    check("get_session shows both turns IN ORDER",
          lambda: [t["role"] for t in s["turns"]] == ["user", "assistant"])
    check("a voice turn and a text turn share ONE conversation (modes kept)",
          lambda: [t["mode"] for t in s["turns"]] == ["text", "voice"])
    check("turn epochs come from the ledger records (injected clock)",
          lambda: [t["epoch"] for t in s["turns"]] == [1010.0, 1020.0])
    check("scope carried", lambda: s["scope"] == ["itc", "corpus"])
    check("turn_count measured", lambda: s["turn_count"] == 2)

    # ===== DURABILITY: a SECOND store on the SAME ledger path =====
    # This is the phone reconnecting from the road: new process, new store,
    # same sid - the conversation must be THERE, because it lives in the
    # chain, not in the client.
    store2 = ConvoStore(Ledger(lp, KEY, "phone-reconnect", clock=clock),
                        clock=clock)
    s2 = store2.get_session(sid)
    check("DURABILITY: second ConvoStore on the same ledger sees the session",
          lambda: s2["sid"] == sid and s2["title"] == "road trip planning")
    check("DURABILITY: both turns survive the reconnect, texts intact",
          lambda: [t["text"] for t in s2["turns"]] == [t["text"] for t in s["turns"]]
          and s2["turn_count"] == 2)
    fake[0] = 1030.0
    n3 = store2.append_turn(sid, "user", "ok keep going", mode="voice")
    check("DURABILITY: the reconnected store CONTINUES the numbering (seq 3)",
          lambda: n3 == 3)
    check("DURABILITY: first store sees the reconnect's turn (one authority)",
          lambda: store.get_session(sid)["turn_count"] == 3)

    # ===== typed refusals =====
    expect("NO_SESSION on get_session with a bogus sid", "NO_SESSION",
           lambda: store.get_session("deadbeef" * 4))
    expect("NO_SESSION on append_turn with a bogus sid", "NO_SESSION",
           lambda: store.append_turn("deadbeef" * 4, "user", "hello"))
    expect("BAD_ROLE on role='narrator'", "BAD_ROLE",
           lambda: store.append_turn(sid, "narrator", "hello"))
    expect("BAD_TURN on empty text", "BAD_TURN",
           lambda: store.append_turn(sid, "user", ""))
    expect("BAD_TURN on whitespace-only text", "BAD_TURN",
           lambda: store.append_turn(sid, "user", "   "))
    expect("BAD_SCOPE on a non-list scope", "BAD_SCOPE",
           lambda: store.create_session("bad", scope="itc"))
    expect("BAD_SCOPE on a list of non-strings", "BAD_SCOPE",
           lambda: store.create_session("bad", scope=[1, 2]))
    n_before = sum(1 for _ in store._ledger.verify())
    expect("a refused turn appends NOTHING (checked next)", "BAD_ROLE",
           lambda: store.append_turn(sid, "narrator", "hello again"))
    check("refusals leave the chain untouched",
          lambda: sum(1 for _ in store._ledger.verify()) == n_before)

    # ===== sources + job_ids: carried per-turn, DEDUPED in the union =====
    su = store.get_session(sid)
    check("sources union is deduped, order-preserving",
          lambda: su["sources"] == ["BU.MD", "00_DOI_INDEX.md"])
    check("job_ids union carried", lambda: su["job_ids"] == ["job-7"])
    fake[0] = 1040.0
    store.append_turn(sid, "system", "job-7 finished", sources=["BU.MD"],
                      job_ids=["job-7", "job-8"])
    su = store.get_session(sid)
    check("dedup holds across new turns (no BU.MD or job-7 twice)",
          lambda: su["sources"] == ["BU.MD", "00_DOI_INDEX.md"]
          and su["job_ids"] == ["job-7", "job-8"])

    # ===== list_sessions: newest first =====
    fake[0] = 2000.0
    sid_b = store.create_session("second thread")
    rows = store.list_sessions()
    check("list_sessions returns both, NEWEST FIRST",
          lambda: [r["sid"] for r in rows] == [sid_b, sid]
          and rows[0]["turn_count"] == 0 and rows[1]["turn_count"] == 4)
    fake[0] = 2010.0
    store.append_turn(sid, "user", "back to the first thread")
    check("activity reorders: touched session floats to the top",
          lambda: store.list_sessions()[0]["sid"] == sid)

    # ===== close: turns REMAIN; the chosen rule: refuse, then explicit reopen =====
    fake[0] = 2020.0
    store.close_session(sid)
    sc = store.get_session(sid)
    check("close_session -> open=False", lambda: sc["open"] is False)
    check("NEVER DELETE: all 5 turns still present after close",
          lambda: sc["turn_count"] == 5
          and sc["turns"][0]["text"] == "what's left on the Ch4 list?")
    expect("RULE: a turn on a CLOSED session refuses BAD_TURN", "BAD_TURN",
           lambda: store.append_turn(sid, "user", "sneaking one in"))
    expect("closing an already-closed session refuses BAD_TURN", "BAD_TURN",
           lambda: store.close_session(sid))
    expect("NO_SESSION on close of a bogus sid", "NO_SESSION",
           lambda: store.close_session("deadbeef" * 4))
    fake[0] = 2030.0
    store.reopen_session(sid)
    check("RULE: reopen_session -> open=True again",
          lambda: store.get_session(sid)["open"] is True)
    n6 = store.append_turn(sid, "user", "resumed after reopen", mode="voice")
    check("turns flow again after reopen, numbering continuous (seq 6)",
          lambda: n6 == 6)
    expect("reopening an OPEN session refuses BAD_TURN", "BAD_TURN",
           lambda: store.reopen_session(sid))
    check("a fresh store sees the reopen too (it is an EVENT, not a flag)",
          lambda: ConvoStore(Ledger(lp, KEY, "r3", clock=clock),
                             clock=clock).get_session(sid)["open"] is True)

    # ===== the chain itself: verify() passes, BY EVENT =====
    recs = list(Ledger(lp, KEY, "auditor", clock=clock).verify())
    events = [r["event"] for r in recs]
    check("ledger chain VERIFIES end-to-end after all appends",
          lambda: [r["seq"] for r in recs] == list(range(1, len(recs) + 1)))
    check("BY EVENT: 2x CONVO_OPENED, 6x CONVO_TURN, 1x CLOSED, 1x REOPENED",
          lambda: (events.count("CONVO_OPENED"), events.count("CONVO_TURN"),
                   events.count("CONVO_CLOSED"),
                   events.count("CONVO_REOPENED")) == (2, 6, 1, 1))
    check("every CONVO_TURN payload names its sid (projection has its facts)",
          lambda: all(r["payload"].get("sid")
                      for r in recs if r["event"] == "CONVO_TURN"))

    # ===== FOLD HARDENING: signed-but-wrong records never project =====
    # These records are appended STRAIGHT to the ledger (valid chain, valid
    # hmac - the signature is not the defense being tested; the fold is).
    led = store._ledger
    before = store.get_session(sid)
    led.append("CONVO_OPENED", {"sid": sid, "title": "hijacked",
                                "scope": [], "owner": "attacker",
                                "opened_epoch": 9999.0})
    after = store.get_session(sid)
    check("HARDENING: a hand-injected DUPLICATE CONVO_OPENED does NOT wipe "
          "turns, retitle, or reown",
          lambda: after["turn_count"] == before["turn_count"]
          and after["title"] == before["title"]
          and after["owner"] == before["owner"]
          and after["open"] == before["open"])
    led.append("CONVO_TURN", {"sid": sid, "role": "user", "text": "ghost turn",
                              "mode": "text", "sources": [], "job_ids": [],
                              "seq": 99})
    check("HARDENING: a turn with a NON-CONTIGUOUS seq (99) is not projected",
          lambda: all(t["text"] != "ghost turn"
                      for t in store.get_session(sid)["turns"]))
    led.append("CONVO_TURN", {"sid": sid, "role": "user", "text": "replayed",
                              "mode": "text", "sources": [], "job_ids": [],
                              "seq": 1})
    check("HARDENING: a REPLAYED seq (1, already taken) is not projected",
          lambda: all(t["text"] != "replayed"
                      for t in store.get_session(sid)["turns"]))
    led.append("CONVO_TURN", {"sid": sid, "text": "no role", "mode": "text",
                              "seq": before["turn_count"] + 1})
    led.append("CONVO_TURN", {"sid": sid, "role": "user", "text": "bad sources",
                              "mode": "text", "sources": [1, 2],
                              "seq": before["turn_count"] + 1})
    check("HARDENING: malformed payloads (missing role / non-string sources) "
          "are ignored, never a crash",
          lambda: store.get_session(sid)["turn_count"] == before["turn_count"])
    n7 = store.append_turn(sid, "user", "after the ghosts")
    check("HARDENING: legit numbering CONTINUES past the ignored records "
          "(next seq unaffected by them)",
          lambda: n7 == before["turn_count"] + 1)
    store.close_session(sid_b)
    led.append("CONVO_TURN", {"sid": sid_b, "role": "user",
                              "text": "into a closed session", "mode": "text",
                              "sources": [], "job_ids": [], "seq": 1})
    check("HARDENING: a turn injected into a CLOSED session is not projected",
          lambda: store.get_session(sid_b)["turn_count"] == 0)

    # ===== OWNERSHIP: sessions bound to a principal =====
    sid_o = store.create_session("owned session", owner="bearer:abc123")
    check("owner is recorded and projected (get_session names it)",
          lambda: store.get_session(sid_o)["owner"] == "bearer:abc123")
    check("assert_owner passes for the recorded principal",
          lambda: store.assert_owner(sid_o, "bearer:abc123") is None)
    expect("assert_owner REFUSES NO_SESSION for a different principal "
           "(existence never leaked)", "NO_SESSION",
           lambda: store.assert_owner(sid_o, "bearer:evil"))
    expect("assert_owner REFUSES NO_SESSION for an unknown sid the same way",
           "NO_SESSION", lambda: store.assert_owner("deadbeef" * 4,
                                                    "bearer:abc123"))
    def _refusal_detail(fn, sid_in_msg):
        try:
            fn()
            return None
        except ConvoError as e:
            return str(e).replace(sid_in_msg, "SID")
    check("...and the two refusals are INDISTINGUISHABLE (same kind, "
          "same detail shape - existence never leaked)",
          lambda: _refusal_detail(
              lambda: store.assert_owner(sid_o, "bearer:evil"), sid_o)
          == _refusal_detail(
              lambda: store.assert_owner("deadbeef" * 4, "bearer:abc123"),
              "deadbeef" * 4))
    check("ownerless (legacy) sessions still work: owner is None",
          lambda: store.get_session(sid)["owner"] is None)
    check("assert_owner(sid, None) matches an ownerless session",
          lambda: store.assert_owner(sid, None) is None)
    expect("...but a REAL principal does not match an ownerless session",
           "NO_SESSION", lambda: store.assert_owner(sid, "bearer:abc123"))
    expect("owner of a wrong type refuses BAD_TURN at create", "BAD_TURN",
           lambda: store.create_session("bad owner", owner=123))

    # ===== the chain still verifies after every injection =====
    recs2 = list(Ledger(lp, KEY, "auditor2", clock=clock).verify())
    check("ledger chain STILL VERIFIES after the hand-injected records "
          "(they are signed; the FOLD is the defense)",
          lambda: [r["seq"] for r in recs2] == list(range(1, len(recs2) + 1)))

    bad = [(l, e) for l, ok, e in RESULTS if not ok]
    for label, ok, err in RESULTS:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label,
                              ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks (conversation state is a LEDGER PROJECTION; "
          "reconnect IS resume)" % ("PASS" if not bad else "FAIL", len(RESULTS)))
    return 0 if not bad else 1


def test_convo():
    assert main() == 0


if __name__ == "__main__":
    sys.exit(main())
