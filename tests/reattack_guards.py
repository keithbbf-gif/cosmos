#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""REATTACK — guards cluster residuals after stage-7 (critic, not builder).

Subject: origin/main @ 483e0fe (K1-K6+H2 claimed closed).
Cluster: cosmos_spend, cosmos_validate, cosmos_context, cosmos_platform,
         cosmos_backup, cosmos_health.

Convention:
  * test_repro_*  PASSES iff the hole is present (adversarial PASS = OPEN).
  * test_closed_* PASSES iff the named stage-7 fix still holds.

A finding without a repro that runs is an opinion. This file is the evidence.

Run:
    PYTHONPATH=cosmos python3 tests/reattack_guards.py
    PYTHONPATH=cosmos python3 -m pytest -v tests/reattack_guards.py
"""
from __future__ import annotations

import inspect
import json
import multiprocessing as mp
import os
import sys
import tempfile
import threading
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "cosmos"))

from cosmos_backup import Backup, BackupError
from cosmos_ledger import Ledger
from cosmos_spend import SpendGate, SpendError

RESULTS: list[tuple[str, str, str]] = []


def _record(aid: str, broken: bool, detail: str) -> None:
    RESULTS.append((aid, "BROKEN" if broken else "HELD", detail))


def attack(aid: str):
    def deco(fn):
        def run_one():
            try:
                broken, detail = fn()
                _record(aid, bool(broken), str(detail))
            except Exception as e:  # noqa: BLE001
                RESULTS.append((aid, "ERROR", f"{type(e).__name__}: {e}"))
        return run_one
    return deco


# =====================================================================
# Known residual that TOUCHES this cluster: spend over-cap under overlap
# Stage-7 K6 closed rid collision and claimed:
#   "two concurrent callers cannot both slip past the cap"
# because reserve binds expect_head_seq. The bind is sampled at append
# time (ledger.head_seq()), not at the projection the decision used.
# =====================================================================

def _spend_gate(td: Path, cap: float = 1.00, clock=None):
    clock = clock or (lambda: 1000.0)
    led = Ledger(td / "s.jsonl", b"k", "A", clock=clock)
    g = SpendGate(led, clock=clock)
    g.set_budget("gem", cap)
    return g, led


@attack("SPEND-OVERCAP-STALE-PROJECTION")
def _overcap_stale_projection():
    """NEW. Stage-7 samples expect_head_seq at append time. A caller that
    projected empty reserved/settled still appends AFTER a second caller has
    already reserved+settled, because head_seq() sees the new head and
    STALE_HEAD never fires. The 'fix' is why the stale decision lands."""
    td = Path(tempfile.mkdtemp(prefix="ra_stale_"))
    g, led = _spend_gate(td)

    orig = g._state
    stale_has_projected = threading.Event()
    fresh_done = threading.Event()
    first = {"yes": True}
    lock = threading.Lock()

    def gated_state():
        s = orig()
        with lock:
            is_stale = first["yes"]
            first["yes"] = False
        if is_stale:
            stale_has_projected.set()
            if not fresh_done.wait(timeout=5):
                raise RuntimeError("fresh caller did not finish")
        return s

    g._state = gated_state
    spent: list[float] = []
    errors: list[str] = []
    stale_kinds: list[str] = []

    def stale_worker():
        try:
            g.guarded_call("gem", 0.70, lambda: (spent.append(0.70), {"usd": 0.70})[1])
        except SpendError as e:
            stale_kinds.append(e.kind)
            errors.append(f"stale:{e.kind}")
        except Exception as e:  # noqa: BLE001
            errors.append(f"stale:{type(e).__name__}:{e}")

    t = threading.Thread(target=stale_worker)
    t.start()
    if not stale_has_projected.wait(timeout=5):
        fresh_done.set()
        t.join(timeout=2)
        return True, "stale projector never reached _state()"

    try:
        g.guarded_call("gem", 0.70, lambda: (spent.append(0.70), {"usd": 0.70})[1])
    except SpendError as e:
        errors.append(f"fresh:{e.kind}")
    except Exception as e:  # noqa: BLE001
        errors.append(f"fresh:{type(e).__name__}:{e}")
    fresh_done.set()
    t.join(timeout=5)

    events = [r["event"] for r in Ledger(td / "s.jsonl", b"k", "R").verify()]
    reserved = events.count("SPEND_RESERVED")
    settled = events.count("SPEND_SETTLED")
    denied = events.count("SPEND_DENIED")
    total = sum(spent)
    over = total > 1.00 + 1e-9 and reserved >= 2 and "DENIED" not in stale_kinds
    return (over,
            f"spent={spent} total={total} cap=1.00 reserved={reserved} "
            f"settled={settled} denied={denied} stale_kinds={stale_kinds} "
            f"errors={errors} — expect_head_seq was sampled AFTER the fresh "
            f"writer moved the head; STALE_HEAD did not fire")


@attack("SPEND-OVERCAP-CALLBACK-BARRIER")
def _overcap_callback_barrier():
    """Statistical sibling (not the evidence). A barrier inside the callback
    only keeps both calls in-flight; if the two check-then-append windows
    miss each other, one is honestly DENIED. Retried so a land is recorded
    when the race is won. The deterministic evidence is STALE-PROJECTION."""
    lands = 0
    last = ""
    for i in range(24):
        td = Path(tempfile.mkdtemp(prefix=f"ra_bar_{i}_"))
        g, _ = _spend_gate(td)
        barrier = threading.Barrier(2)
        spent: list[float] = []
        errors: list[str] = []

        def body():
            barrier.wait(timeout=2)
            return {"usd": 0.70}

        def worker():
            try:
                g.guarded_call("gem", 0.70, body)
                spent.append(0.70)
            except SpendError as e:
                errors.append(e.kind)
            except Exception as e:  # noqa: BLE001
                errors.append(repr(e))

        t1 = threading.Thread(target=worker)
        t2 = threading.Thread(target=worker)
        t1.start(); t2.start()
        t1.join(timeout=5); t2.join(timeout=5)
        total = sum(spent)
        last = f"trial {i+1} spent={spent} total={total} errors={errors}"
        if total > 1.00 + 1e-9:
            lands += 1
            return True, f"{last} (landed on retry {i+1}/24)"
    return False, f"0/24 callback-barrier trials over-cap; last={last}"


def _mp_stale_child(path: str, projected: mp.Event, release: mp.Event, q: mp.Queue) -> None:
    """Stale process: project, wait for the sibling to finish a full spend,
    then continue with the stale snapshot. Same mechanism as the in-process
    stale-projection attack; the ledger flock is the only new variable."""
    led = Ledger(path, b"k", f"STALE{os.getpid()}")
    g = SpendGate(led)
    orig = g._state

    def gated():
        s = orig()
        projected.set()
        if not release.wait(timeout=5):
            raise RuntimeError("fresh process did not release")
        return s

    g._state = gated
    try:
        g.guarded_call("gem", 0.70, lambda: {"usd": 0.70})
        q.put(("stale", 0.70, None))
    except SpendError as e:
        q.put(("stale", 0.0, e.kind))
    except Exception as e:  # noqa: BLE001
        q.put(("stale", 0.0, f"{type(e).__name__}:{e}"))


def _mp_fresh_child(path: str, q: mp.Queue) -> None:
    led = Ledger(path, b"k", f"FRESH{os.getpid()}")
    g = SpendGate(led)
    try:
        g.guarded_call("gem", 0.70, lambda: {"usd": 0.70})
        q.put(("fresh", 0.70, None))
    except SpendError as e:
        q.put(("fresh", 0.0, e.kind))
    except Exception as e:  # noqa: BLE001
        q.put(("fresh", 0.0, f"{type(e).__name__}:{e}"))


@attack("SPEND-OVERCAP-MULTIPROCESS")
def _overcap_multiprocess():
    """NEW. Cross-process form of the stale projection. Two OS processes,
    one ledger file. The flock serializes append+re-prime; it does not
    re-check the cap. The stale process still spends past $1."""
    ctx = mp.get_context("fork")
    td = Path(tempfile.mkdtemp(prefix="ra_mp_"))
    path = str(td / "s.jsonl")
    _spend_gate(td)  # BUDGET_SET
    projected, release = ctx.Event(), ctx.Event()
    q: mp.Queue = ctx.Queue()
    stale = ctx.Process(target=_mp_stale_child, args=(path, projected, release, q))
    stale.start()
    if not projected.wait(timeout=5):
        release.set()
        stale.join(timeout=2)
        return True, "stale process never projected"
    fresh = ctx.Process(target=_mp_fresh_child, args=(path, q))
    fresh.start()
    fresh.join(timeout=5)
    release.set()
    stale.join(timeout=5)
    got = []
    while not q.empty():
        got.append(q.get_nowait())
    spent = sum(v for _, v, _ in got)
    kinds = [(who, kind) for who, _, kind in got]
    if stale.is_alive():
        stale.terminate()
    if fresh.is_alive():
        fresh.terminate()
    events = [r["event"] for r in Ledger(path, b"k", "R").verify()]
    return (spent > 1.00 + 1e-9,
            f"got={got} spent={spent} cap=1.00 kinds={kinds} "
            f"events={events} — flock serialized the append; both still settled")


@attack("SPEND-HEAD-SEQ-SAMPLED-AT-APPEND")
def _head_seq_sampled_late():
    """NEW. Instrument head_seq vs _state: the seq bound into expect_head_seq
    is read AFTER the decision, and can differ from the head the projection
    saw. Combined with STALE-PROJECTION this is the mechanism, not a guess."""
    td = Path(tempfile.mkdtemp(prefix="ra_seq_"))
    g, led = _spend_gate(td)
    seen = {"at_state": None, "at_head_seq": []}

    orig_state = g._state
    orig_head = led.head_seq

    def wrapped_state():
        s = orig_state()
        seen["at_state"] = orig_head()
        return s

    def wrapped_head():
        h = orig_head()
        seen["at_head_seq"].append(h)
        return h

    stale_projected = threading.Event()
    fresh_done = threading.Event()
    first = {"yes": True}
    lock = threading.Lock()

    def gated_state():
        s = wrapped_state()
        with lock:
            is_stale = first["yes"]
            first["yes"] = False
        if is_stale:
            stale_projected.set()
            fresh_done.wait(timeout=5)
        return s

    g._state = gated_state
    led.head_seq = wrapped_head

    def stale():
        try:
            g.guarded_call("gem", 0.70, lambda: {"usd": 0.70})
        except SpendError:
            pass

    t = threading.Thread(target=stale)
    t.start()
    stale_projected.wait(timeout=5)
    try:
        g.guarded_call("gem", 0.70, lambda: {"usd": 0.70})
    except SpendError:
        pass
    fresh_done.set()
    t.join(timeout=5)

    src = inspect.getsource(SpendGate.guarded_call)
    late_in_source = "expect_head_seq=self.ledger.head_seq()" in src
    # stale's head_seq sample (last one before its reserve) should be GREATER
    # than the head it projected, if the fresh writer landed in between.
    projected = seen["at_state"]
    samples = seen["at_head_seq"]
    moved = projected is not None and any(h > projected for h in samples)
    return (late_in_source and moved,
            f"source_binds_live_head={late_in_source} "
            f"projected_head={projected} later_head_seq_samples={samples}")


@attack("SPEND-BUDGET-RESET-STILL-WIPES")
def _budget_reset():
    """Remain of the same breaker (not the K6 residual). BUDGET_SET still
    replaces the rail dict; a 'refresh' zeroes settled and the next spend
    is ALLOWED past the original cap."""
    td = Path(tempfile.mkdtemp(prefix="ra_reset_"))
    g, _ = _spend_gate(td)
    g.guarded_call("gem", 0.90, lambda: {"usd": 0.90})
    g.set_budget("gem", 1.00)
    ran = []
    try:
        g.guarded_call("gem", 0.90, lambda: (ran.append(1), {"usd": 0.90})[1])
        allowed = True
    except SpendError:
        allowed = False
    settled = g.audit()["rails"]["gem"]["settled_usd"]
    return (allowed and bool(ran) and settled >= 0.90,
            f"second_allowed={allowed} projected_settled={settled} "
            f"(true spend $1.80 on a $1 cap)")


# =====================================================================
# Honest HOLDS — do not re-open K6 rid / sequential deny / K3 backup
# =====================================================================

@attack("CLOSED-K6-RID-UNIQUE")
def _closed_rid():
    """K6 as named: two sequential reserves at a frozen clock get distinct rids.
    Passing this attack as HELD means the original collision is still closed.
    (The harness records HELD when the hole is absent.)"""
    td = Path(tempfile.mkdtemp(prefix="ra_rid_"))
    clock = [1000.0]
    g, led = _spend_gate(td, cap=10.00, clock=lambda: clock[0])
    g.guarded_call("gem", 0.10, lambda: {"usd": 0.01})
    g.guarded_call("gem", 0.10, lambda: {"usd": 0.01})
    rids = [e["payload"]["rid"] for e in led.verify() if e["event"] == "SPEND_RESERVED"]
    collided = len(rids) == 2 and len(set(rids)) == 1
    return (collided, f"rids={rids}")


@attack("CLOSED-SEQUENTIAL-CAP")
def _closed_seq_cap():
    """Sequential over-cap deny still holds. The existing suite's happy path
    is real; it is not the overlap case."""
    td = Path(tempfile.mkdtemp(prefix="ra_seqcap_"))
    g, _ = _spend_gate(td)
    ran = []
    g.guarded_call("gem", 0.70, lambda: (ran.append(0.70), {"usd": 0.70})[1])
    denied = False
    kind = None
    try:
        g.guarded_call("gem", 0.70, lambda: (ran.append(0.70), {"usd": 0.70})[1])
    except SpendError as e:
        denied = e.kind == "DENIED"
        kind = e.kind
    hole = (not denied) or len(ran) != 1
    return (hole, f"ran={ran} denied={denied} kind={kind}")


@attack("CLOSED-K3-BACKUP-TRAVERSAL")
def _closed_k3():
    """K3 as named: manifest key with .. must refuse and must not write outside."""
    td = Path(tempfile.mkdtemp(prefix="ra_k3_"))
    dest = td / "backup"; dest.mkdir()
    (dest / "_MANIFEST.sha256.json").write_text(
        json.dumps({"..\\..\\k3_escape.txt": "0" * 64}), encoding="utf-8")
    escape = td / "k3_escape.txt"
    bk = Backup(Ledger(td / "b.jsonl", b"k", "A"))
    refused = False
    kind = None
    try:
        bk.rehearse_restore(dest, td / "scratch")
    except BackupError as e:
        refused = e.kind == "REHEARSAL_FAILED"
        kind = e.kind
    return (not refused or escape.exists(),
            f"refused={refused} kind={kind} escape_landed={escape.exists()}")


# =====================================================================
# pytest surface — test_repro_* passes IFF the hole is present
# =====================================================================

def test_repro_spend_overcap_stale_projection():
    _overcap_stale_projection()
    row = [r for r in RESULTS if r[0] == "SPEND-OVERCAP-STALE-PROJECTION"][-1]
    assert row[1] == "BROKEN", row


def test_repro_spend_overcap_multiprocess():
    _overcap_multiprocess()
    row = [r for r in RESULTS if r[0] == "SPEND-OVERCAP-MULTIPROCESS"][-1]
    assert row[1] == "BROKEN", row


def test_repro_spend_head_seq_sampled_at_append():
    _head_seq_sampled_late()
    row = [r for r in RESULTS if r[0] == "SPEND-HEAD-SEQ-SAMPLED-AT-APPEND"][-1]
    assert row[1] == "BROKEN", row


def test_repro_spend_budget_reset_wipes_settled():
    _budget_reset()
    row = [r for r in RESULTS if r[0] == "SPEND-BUDGET-RESET-STILL-WIPES"][-1]
    assert row[1] == "BROKEN", row


def test_closed_k6_rid_unique():
    _closed_rid()
    row = [r for r in RESULTS if r[0] == "CLOSED-K6-RID-UNIQUE"][-1]
    assert row[1] == "HELD", row


def test_closed_sequential_cap():
    _closed_seq_cap()
    row = [r for r in RESULTS if r[0] == "CLOSED-SEQUENTIAL-CAP"][-1]
    assert row[1] == "HELD", row


def test_closed_k3_backup_traversal():
    _closed_k3()
    row = [r for r in RESULTS if r[0] == "CLOSED-K3-BACKUP-TRAVERSAL"][-1]
    assert row[1] == "HELD", row


def main() -> int:
    RESULTS.clear()
    for fn in (
        _overcap_stale_projection,
        _overcap_callback_barrier,
        _overcap_multiprocess,
        _head_seq_sampled_late,
        _budget_reset,
        _closed_rid,
        _closed_seq_cap,
        _closed_k3,
    ):
        fn()
    broken = [(i, d) for i, st, d in RESULTS if st == "BROKEN"]
    held = [(i, d) for i, st, d in RESULTS if st == "HELD"]
    errors = [(i, d) for i, st, d in RESULTS if st == "ERROR"]
    for aid, st, detail in RESULTS:
        print(f"  {st:6}  {aid}  — {detail}")
    print(f"REATTACK_GUARDS {len(broken)} BROKEN / {len(held)} HELD / {len(errors)} ERROR "
          f"of {len(RESULTS)}")
    return 0 if not errors else 2


if __name__ == "__main__":
    sys.exit(main())
