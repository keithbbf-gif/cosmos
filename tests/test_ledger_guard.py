#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest: Ledger.append_guarded - THE ONE-WRITER / EXACTLY-ONCE FENCE.

WHY THIS FILE EXISTS. `Ledger.append_guarded` is the atomic READ-DECIDE-APPEND
every exactly-once decision in COSMOS rests on: the spend cap check
(cosmos_spend.guarded_call), the voice confirm-nonce consume (cosmos_voice),
the maker duplicate check (cosmos_makers), the convo turn append (cosmos_convo).
On 2026-08-30 a contract audit found it had NO TEST ANYWHERE - zero hits in
tests/ - so `docs/contracts/ledger.toml` pinned its invariant on CODE EVIDENCE
ONLY (a grep for a docstring phrase). A docstring is not a running proof, and
the finding it replaced (RG-B1) was MEASURED, not theorised: sampling the head
only at APPEND time let two overlapping callers both pass a $1 cap and spend
$1.40. This suite makes the invariant executable.

THE RACE IS REAL, NOT MOCKED. G3 runs RACERS real OS threads, each with its own
Ledger handle (its own sidecar lock fd), released together from a Barrier onto
ONE projected head. The winner's `decide` SLEEPS WIDEN seconds while holding the
exclusive lock; every loser is blocked in `_lock_handle` for that whole window.
That makes the failure deterministic in the broken direction: an implementation
that called `decide` outside the lock - or that re-read the head only at append
time - would hand all RACERS callers the same pre-append history and commit all
RACERS claims. Exactly one commit is a property that only an atomic critical
section can produce.

G2's refusal also proves the lock is RELEASED on the abort path (append_guarded's
`finally: self._unlock(lk)`): the same Ledger object commits immediately after,
which a leaked lock would turn into a hang, not a wrong answer.

Canon: no hard-coded paths (everything under a tempdir resolved from __file__);
typed refusals only; nothing deleted.
"""
from __future__ import annotations

import sys
import tempfile
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "cosmos"))
from cosmos_ledger import Ledger, LedgerError

KEY = b"guard-key"
RACERS = 8
WIDEN = 0.05          # the winner holds the lock this long INSIDE decide

RESULTS = []


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:                                            # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


def _head(recs) -> int:
    """The head seq a decision is being made against; 0 for an empty history."""
    return recs[-1]["seq"] if recs else 0


def main() -> int:
    td = Path(tempfile.mkdtemp(prefix="cosmos_guard_"))

    # ===== G1: the head matches -> the decision COMMITS =====
    p1 = td / "g1.jsonl"
    w = Ledger(p1, KEY, "W")
    w.append("SEED", {"n": 1})                      # head is now 1
    seen = {}

    def decide_ok(recs):
        seen["head"] = _head(recs)
        seen["n"] = len(recs)
        return ("GUARDED", {"n": 2})

    rec = w.append_guarded(decide_ok)
    check("G1: guarded append on a MATCHING head COMMITS",
          lambda: rec is not None and rec["seq"] == 2 and rec["event"] == "GUARDED")
    check("G1: decide() receives the FRESHLY REPLAYED history, not a remembered one",
          lambda: seen["head"] == 1 and seen["n"] == 1)
    check("G1: a decision that returns None writes NOTHING",
          lambda: w.append_guarded(lambda recs: None) is None
          and len(list(Ledger(p1, KEY, "R").verify())) == 2)

    # ===== G2: the head MOVED under the decision -> typed refusal =====
    # `w` still remembers head=2. Another writer advances the file to 3 behind
    # its back - exactly the stale-projection shape of RG-B1.
    Ledger(p1, KEY, "INTERLOPER").append("INTERLOPER", {"n": 3})
    before_bytes = p1.read_bytes()
    my_head = 2                                     # what w decided against

    def decide_stale(recs):
        seen["saw"] = _head(recs)
        if _head(recs) != my_head:
            raise LedgerError("STALE_HEAD",
                              f"decided on head {my_head}, disk head is {_head(recs)}")
        return ("SHOULD_NEVER_LAND", {})

    def _refuses():
        try:
            w.append_guarded(decide_stale)
        except LedgerError as e:
            return e.kind == "STALE_HEAD"
        return False

    check("G2: a head that MOVED under the decision REFUSES, typed STALE_HEAD",
          _refuses)
    check("G2: the guard showed decide() the REAL head (3), not w's remembered 2",
          lambda: seen["saw"] == 3)

    # ===== G4a: the refusal did not corrupt or truncate anything =====
    check("G4: the refusal leaves the ledger BYTE-IDENTICAL and still VERIFYING",
          lambda: p1.read_bytes() == before_bytes
          and [r["seq"] for r in Ledger(p1, KEY, "R").verify()] == [1, 2, 3])
    check("G4: no SHOULD_NEVER_LAND record reached the chain",
          lambda: not [r for r in Ledger(p1, KEY, "R").verify()
                       if r["event"] == "SHOULD_NEVER_LAND"])
    # A leaked lock would HANG here rather than answer wrongly: the abort path's
    # `finally: self._unlock(lk)` is what makes the loser re-project and retry.
    check("G2: the clean loser can re-project and commit on the new head",
          lambda: w.append_guarded(lambda recs: ("RETRY", {"on": _head(recs)}))["seq"] == 4)

    # ===== G3: RACERS real threads, ONE head - exactly one may commit =====
    p3 = td / "g3.jsonl"
    Ledger(p3, KEY, "SETUP").append("JOB_OPEN", {"job": "J"})
    gate = threading.Barrier(RACERS)
    won, lost, errors, heads = [], [], [], []

    def racer(name: str):
        led = Ledger(p3, KEY, name)
        head = led.head_seq()                       # every racer projects the SAME head
        heads.append(head)
        gate.wait()

        def decide(recs):
            if _head(recs) != head:                 # the head I decided on is gone
                raise LedgerError("STALE_HEAD",
                                  f"{name}: decided on {head}, disk head is {_head(recs)}")
            time.sleep(WIDEN)                       # hold the lock; widen the window
            return ("CLAIM", {"by": name})

        try:
            won.append(led.append_guarded(decide)["payload"]["by"])
        except LedgerError as e:
            lost.append(e.kind)
        except Exception as e:                                        # noqa: BLE001
            errors.append(repr(e))

    threads = [threading.Thread(target=racer, args=(f"R{i}",)) for i in range(RACERS)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    check("G3: every racer decided against the SAME head (it was a real race)",
          lambda: len(heads) == RACERS and len(set(heads)) == 1)
    check("G3: 8 racing writers on ONE head -> EXACTLY ONE commit",
          lambda: len(won) == 1)
    check("G3: every loser lost CLEANLY and TYPED (STALE_HEAD), none by exception",
          lambda: lost == ["STALE_HEAD"] * (RACERS - 1) and not errors)
    after = list(Ledger(p3, KEY, "R").verify())
    check("G3: exactly one CLAIM landed in the chain (was: all 8, if decide ran "
          "outside the lock)",
          lambda: [r["event"] for r in after].count("CLAIM") == 1)
    check("G3: the winning CLAIM is the one the caller was told won",
          lambda: [r["payload"]["by"] for r in after
                   if r["event"] == "CLAIM"] == [won[0]])
    check("G3: the chain VERIFIES after the race, seqs 1..2 with no duplicates",
          lambda: [r["seq"] for r in after] == [1, 2])

    bad = [(l, e) for l, ok, e in RESULTS if not ok]
    for label, ok, err in RESULTS:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label,
                              ("  [" + err + "]") if err else ""))
    print("live_value: winner=%s losers=%d chain=%s"
          % (won[0] if won else None, len(lost), [r["event"] for r in after]))
    print("SELFTEST %s - %d checks on append_guarded (real threads, not a mocked race)"
          % ("PASS" if not bad else "FAIL", len(RESULTS)))
    return 0 if not bad else 1


def test_ledger_guard():
    assert main() == 0


if __name__ == "__main__":
    sys.exit(main())
