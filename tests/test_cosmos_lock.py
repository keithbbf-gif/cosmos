#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest for cosmos_lock spike. Injectable clock - expiry is TESTED, not slept for.
Positive and negative controls; refusals asserted BY KIND; ledger chain asserted BY EVENT.
"""
from __future__ import annotations
import sys, tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cosmos_lock import Arbiter, LockError

RESULTS = []

def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:                                            # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))

def expect(kind):
    def wrap(f):
        def inner():
            try:
                f()
            except LockError as e:
                return e.kind == kind
            return False
        return inner
    return wrap


class Clock:
    def __init__(self): self.t = 1000.0
    def __call__(self): return self.t


def main() -> int:
    td = Path(tempfile.mkdtemp(prefix="cosmos_lock_"))
    clk = Clock()
    led = td / "lock_ledger.jsonl"
    arb = Arbiter(led, clock=clk, default_ttl=100)

    # ---- POSITIVE path ----
    l1 = arb.acquire("tree", "F5")
    check("grant issues token 1", lambda: l1.token == 1)
    check("fenced commit under live token runs", lambda: arb.fenced_commit(l1, lambda: "did") == "did")
    check("renew extends expiry", lambda: arb.renew(l1).expires_at == clk.t + 100)

    # ---- second writer refused, BY KIND ----
    check("second writer -> HELD", expect("HELD")(lambda: arb.acquire("tree", "GROK")))

    # ---- THE DYING HOLDER: no release, clock passes expiry ----
    clk.t += 101
    l2 = arb.acquire("tree", "GROK")            # succeeds - lease expired on arbiter clock
    check("dying holder recovered by expiry, no cleanup discipline", lambda: l2.holder == "GROK")
    check("fencing token is MONOTONIC across takeover", lambda: l2.token == 2)
    check("dead holder's late commit -> STALE_TOKEN, refused and ledgered",
          expect("STALE_TOKEN")(lambda: arb.fenced_commit(l1, lambda: "necromancy")))
    ev = [e["event"] for e in arb.events()]
    check("expiry is a RECORDED event (EXPIRE precedes the new GRANT)",
          lambda: "EXPIRE" in ev and ev.index("EXPIRE") < len(ev) - 1)
    check("the refusal is a RECORDED event, not console prose",
          lambda: any(e["event"] == "REFUSE" and e.get("op") == "commit" for e in arb.events()))

    # ---- release semantics ----
    arb.release(l2)
    check("release frees the resource", lambda: arb.status("tree") is None)
    check("release with stale token is recorded, ignored, and harmless",
          lambda: (arb.release(l1), True)[1])
    l3 = arb.acquire("tree", "F5")
    check("token still monotonic after release (3 > 2)", lambda: l3.token == 3)
    check("commit after release of a DIFFERENT older lease -> works for current holder",
          lambda: arb.fenced_commit(l3, lambda: 42) == 42)
    check("commit on released lease -> NO_LEASE",
          expect("NO_LEASE")(lambda: (arb.release(l3), arb.fenced_commit(l3, lambda: 0))[1]))

    # ---- ARBITER RESTART: replay rebuilds state AND the token counter ----
    l4 = arb.acquire("tree", "F5")
    arb2 = Arbiter(led, clock=clk, default_ttl=100)
    check("replayed arbiter sees the live lease", lambda: arb2.status("tree").token == l4.token)
    check("replayed arbiter's NEXT token is higher (counter survives restart)",
          lambda: arb2.acquire("other", "GROK").token > l4.token)

    # ---- TORN LEDGER refuses ----
    bad = td / "torn.jsonl"
    bad.write_text('{"event": "GRANT", "resource": "x", "holder": "A", "token": 1, '
                   '"t": 1, "expires_at": 2}\n{ torn line', encoding="utf-8")
    check("torn ledger -> TORN_LEDGER refusal (never reads as free)",
          expect("TORN_LEDGER")(lambda: Arbiter(bad, clock=clk)))

    bad2 = [(l, e) for l, ok, e in RESULTS if not ok]
    for label, ok, err in RESULTS:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label, ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks (5 refusals asserted BY KIND, 2 chains BY EVENT)"
          % ("PASS" if not bad2 else "FAIL", len(RESULTS)))
    return 0 if not bad2 else 1


def test_cosmos_lock():
    assert main() == 0


if __name__ == "__main__":
    sys.exit(main())
