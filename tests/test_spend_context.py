#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest: cosmos_spend (the breaker in the caller) + cosmos_context (carry-over as
mechanism). Refusals BY KIND; the breaker proven to DENY BEFORE the call; both-direction
budget audit; S-121 (paid return, nobody watching) made structurally impossible."""
from __future__ import annotations
import sys, tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cosmos_ledger import Ledger
from cosmos_spend import SpendGate, SpendError
from cosmos_context import Session, ContextError, boot_inherit

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
    td = Path(tempfile.mkdtemp(prefix="cosmos_sc_"))
    KEY = b"k"

    # ================= SPEND =================
    fake = [1000.0]
    led = Ledger(td / "spend.jsonl", KEY, "F5", clock=lambda: fake[0])
    g = SpendGate(led, clock=lambda: fake[0])
    g.set_budget("gem", 1.00, expires_epoch=fake[0] + 30 * 86400)

    calls = []
    r = g.guarded_call("gem", 0.30, lambda: (calls.append(1), {"usd": 0.05})[1])
    check("reserve -> call -> settle at MEASURED (not worst case)",
          lambda: r["usd"] == 0.05 and g.audit()["rails"]["gem"]["settled_usd"] == 0.05)

    # THE BREAKER: deny happens BEFORE the call - the call list must not grow
    n_before = len(calls)
    check("over-cap call DENIED", expect(SpendError, "DENIED")(
        lambda: g.guarded_call("gem", 5.0, lambda: (calls.append(1), {"usd": 0})[1])))
    check("...and the call NEVER RAN (denial precedes spend - the whole point)",
          lambda: len(calls) == n_before)
    check("unbudgeted rail -> UNKNOWN_RAIL",
          expect(SpendError, "UNKNOWN_RAIL")(lambda: g.guarded_call("nope", 0.01, dict)))

    # UNPRICED is a state, never zero
    fake[0] += 1
    g.guarded_call("gem", 0.10, lambda: {"text": "no usd field"})
    a = g.audit()
    check("unpriced call counted as UNPRICED, settled unchanged",
          lambda: a["rails"]["gem"]["unpriced_calls"] == 1
          and a["rails"]["gem"]["settled_usd"] == 0.05)

    # a raising call RELEASES its reservation
    def boom(): raise ValueError("rail died")
    try:
        g.guarded_call("gem", 0.20, boom)
    except ValueError:
        pass
    check("a raising call releases its reservation",
          lambda: g.audit()["rails"]["gem"]["reserved_usd"] == 0)

    # BOTH DIRECTIONS: expiring credit flags as the risk
    g.set_budget("vertex", 300.0, expires_epoch=fake[0] + 20 * 86400)
    check("expiring unspent credit -> EXPIRY RISK flagged (S-102: we governed the "
          "wrong direction)",
          lambda: "EXPIRING" in (g.audit()["rails"]["vertex"]["expiry_risk"] or ""))
    check("every audit number carries measured_at",
          lambda: g.audit()["measured_at_epoch"] > 0)

    # ================= CONTEXT =================
    led2 = Ledger(td / "ctx.jsonl", KEY, "F5")
    s1 = Session(led2, "s1", "pb")
    s1.record_fact("repo", "keithbbf-gif/cosmos")
    s1.open_watcher("w-grok", "grok stage 4 return")
    check("close with an open watcher REFUSES (S-121 made structural)",
          expect(ContextError, "UNRESOLVED")(lambda: s1.close("s2")))
    m = s1.close("s2", force=True)
    check("forced close records OPEN_CONTEXT incident",
          lambda: any(r["event"] == "OPEN_CONTEXT" for r in led2.verify()))
    inh = boot_inherit(led2)
    check("next boot INHERITS the facts", lambda: inh["facts"]["repo"] == "keithbbf-gif/cosmos")
    check("next boot SEES the unresolved watcher as an incident",
          lambda: inh["incidents"] and "w-grok" in inh["incidents"][0]["unresolved"])
    s2 = Session(led2, "s2", "pb")
    s2.open_watcher("w-grok", "carried over")
    s2.resolve_watcher("w-grok", "return landed")
    m2 = s2.close("s3")
    check("clean close after resolution needs no force", lambda: m2["handoff_to"] == "s3")
    check("resolved incident clears from inheritance",
          lambda: not boot_inherit(led2)["incidents"])
    check("double close REFUSES",
          expect(ContextError, "ALREADY_CLOSED")(lambda: s2.close("s4")))

    bad = [(l, e) for l, ok, e in RESULTS if not ok]
    for label, ok, err in RESULTS:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label, ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks (breaker denies BEFORE the call; carry-over is a "
          "mechanism)" % ("PASS" if not bad else "FAIL", len(RESULTS)))
    return 0 if not bad else 1


def test_spend_context():
    assert main() == 0


if __name__ == "__main__":
    sys.exit(main())