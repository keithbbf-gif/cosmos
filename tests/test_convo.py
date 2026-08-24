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
