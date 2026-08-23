#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest: cosmos_ledger + cosmos_sched (foundation + scheduler-on-foundation).
Refusals BY KIND; chain breaks planted and detected BY LINE; interrupt demo MEASURED."""
from __future__ import annotations
import json, sys, tempfile, threading, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cosmos_ledger import Ledger, LedgerError
from cosmos_sched import Scheduler, SchedError

RESULTS = []

def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:                                            # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))

def expect(exc, kind):
    def wrap(f):
        def inner():
            try:
                f()
            except exc as e:
                return e.kind == kind
            return False
        return inner
    return wrap


def main() -> int:
    td = Path(tempfile.mkdtemp(prefix="cosmos_core_"))
    KEY = b"spike-install-key"

    # ================= LEDGER =================
    lp = td / "ledger.jsonl"
    led = Ledger(lp, KEY, "F5")
    for i in range(5):
        led.append("PING", {"n": i})
    check("5 appends verify as a chain", lambda: len(list(led.verify())) == 5)
    check("projection rebuilds state by replay",
          lambda: led.project(lambda s, r: s + r["payload"]["n"], 0) == 10)
    check("reload continues the chain (writer state survives restart)",
          lambda: Ledger(lp, KEY, "F5").append("PING", {"n": 5})["seq"] == 6)

    # --- three corruption kinds, planted, detected BY KIND ---
    lines = lp.read_text(encoding="utf-8").splitlines()
    torn = td / "torn.jsonl"; torn.write_text("\n".join(lines[:2] + ["{ torn"]), encoding="utf-8")
    check("torn line -> TORN", expect(LedgerError, "TORN")(lambda: Ledger(torn, KEY, "F5")))
    tam = json.loads(lines[1]); tam["payload"]["n"] = 99
    tampered = td / "tampered.jsonl"
    tampered.write_text("\n".join([lines[0], json.dumps(tam, sort_keys=True, separators=(",", ":"))]), encoding="utf-8")
    check("tampered payload -> BROKEN_CHAIN (bytes/hash disagree)",
          expect(LedgerError, "BROKEN_CHAIN")(lambda: Ledger(tampered, KEY, "F5")))
    check("record signed with the WRONG KEY -> FORGED",
          expect(LedgerError, "FORGED")(lambda: Ledger(lp, b"other-key", "F5")))
    dropped = td / "dropped.jsonl"; dropped.write_text("\n".join([lines[0]] + lines[2:]), encoding="utf-8")
    check("silently dropped middle record -> BROKEN_CHAIN",
          expect(LedgerError, "BROKEN_CHAIN")(lambda: Ledger(dropped, KEY, "F5")))

    # ================= SCHEDULER =================
    s = Scheduler(td / "sched", KEY, "F5")
    j_low = s.submit("low job", "low")
    j_crit = s.submit("critical job", "critical")
    j_norm = s.submit("normal job", "normal")
    check("priority admission: critical first, low last",
          lambda: [m["job_id"] for m in s.queued()] == [j_crit, j_norm, j_low])
    check("bad priority REFUSES", expect(SchedError, "BAD_PRIORITY")(lambda: s.submit("x", "urgent")))

    m = s.claim_next()
    check("claim takes the critical job", lambda: m["job_id"] == j_crit)
    check("claimed job leaves the queue", lambda: [x["job_id"] for x in s.queued()] == [j_norm, j_low])
    s.done(j_crit, "FINDINGS", "found 3 things")
    check("FINDINGS is an outcome, not a failure",
          lambda: s._state()[j_crit]["st"] == "FINDINGS")
    check("bare-rc outcome REFUSES (three words only)",
          expect(SchedError, "BAD_STATE")(lambda: s.done(j_norm, "OK")))
    check("done on a non-RUNNING job REFUSES",
          expect(SchedError, "BAD_STATE")(lambda: s.done(j_norm, "CLEAN")))

    # exactly-once under overlap: claim all, then 50 replayed claim attempts
    while s.claim_next():
        pass
    claims = sum(1 for r in s.ledger.verify() if r["event"] == "JOB_CLAIMED")
    check("every job claimed EXACTLY once (ledger count = jobs)", lambda: claims == 3)
    check("claim on empty queue returns None (empty != error)", lambda: s.claim_next() is None)

    # stale: report, never retry
    s2 = Scheduler(td / "sched2", KEY, "F5", clock=lambda: fake[0])
    fake = [1000.0]
    jid = s2.submit("long", "normal"); s2.claim_next()
    fake[0] += 7300
    rep = s2.report_stale(7200)
    check("stale RUNNING is REPORTED (event), job NOT retried",
          lambda: rep == [jid] and s2._state()[jid]["st"] == "RUNNING")
    check("stale is reported ONCE, not every tick", lambda: s2.report_stale(7200) == [])

    # ================= INTERRUPT (measured) =================
    s3 = Scheduler(td / "sched3", KEY, "F5")
    res = {}
    def waiter():
        res.update(s3.wait_for_submission(timeout_s=8))
    th = threading.Thread(target=waiter); th.start()
    time.sleep(0.6)
    s3.submit("wake up", "normal")
    th.join(timeout=10)
    check("wakeup FIRED on submission [%s, %.3fs latency]"
          % (res.get("mechanism", "?"), res.get("latency_s", -1)),
          lambda: res.get("fired") is True)

    bad = [(l, e) for l, ok, e in RESULTS if not ok]
    for label, ok, err in RESULTS:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label, ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks (7 refusals BY KIND, 4 planted corruptions, "
          "1 measured interrupt)" % ("PASS" if not bad else "FAIL", len(RESULTS)))
    return 0 if not bad else 1


def test_core():
    assert main() == 0


if __name__ == "__main__":
    sys.exit(main())
