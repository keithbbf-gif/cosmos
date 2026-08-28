#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ADVERSARIAL attacks on the guards cluster (critic, not builder).

Does not modify cosmos/ or the existing selftests. Each attack tries to violate a
ratified contract (FINAL_ARCHITECTURE / H1-H5 / Decision 8/10/11). A BROKEN line
is a finding with a runnable repro. A HELD line means this attack did not land.

Run:
    PYTHONPATH=cosmos python3 tests/attack_guards.py
    PYTHONPATH=cosmos python3 -m pytest tests/attack_guards.py -v
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "cosmos"))

from cosmos_backup import Backup, BackupError
from cosmos_context import Session, ContextError, boot_inherit
from cosmos_health import HealthBoard
from cosmos_kernel import Kernel, install
from cosmos_ledger import Ledger
from cosmos_platform import PlatformError, run, run_tree_killed, write_text_lf, makedirs
from cosmos_spend import SpendGate, SpendError
from cosmos_validate import (
    ValidateError, read_verified, write_declared, ReturnValidator,
)

RESULTS: list[tuple[str, str, str]] = []  # (id, HELD|BROKEN|ERROR, detail)


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
# cosmos_spend
# =====================================================================

@attack("SPEND-RACE-OVERSPEND")
def _spend_race():
    """Check-then-append is not atomic. Widening the window after _state()
    (50ms) is enough for two callers to both pass a $1 cap and both spend."""
    td = Path(tempfile.mkdtemp(prefix="ag_spend_race_"))
    clock = [1000.0]
    g = SpendGate(Ledger(td / "s.jsonl", b"k", "A", clock=lambda: clock[0]),
                  clock=lambda: clock[0])
    g.set_budget("gem", 1.00)
    orig = g._state

    def slow_state():
        s = orig()
        time.sleep(0.05)  # the TOCTOU window the production lock does not cover
        return s

    g._state = slow_state
    spent = []
    errors = []

    def worker(usd):
        try:
            g.guarded_call("gem", 0.80, lambda: (spent.append(usd), {"usd": usd})[1],
                           ttl_s=600)
        except SpendError as e:
            errors.append(e.kind)
        except Exception as e:  # noqa: BLE001
            errors.append(repr(e))

    t1 = threading.Thread(target=worker, args=(0.70,))
    t2 = threading.Thread(target=worker, args=(0.70,))
    t1.start(); t2.start(); t1.join(); t2.join()
    total = sum(spent)
    return (total > 1.00 + 1e-9,
            f"calls_ran={spent} total={total} cap=1.00 errors={errors} "
            f"(50ms gap after _state(); ledger lock does not cover the decision)")


@attack("SPEND-BUDGET-RESET-WIPES-SETTLED")
def _spend_reset():
    """BUDGET_SET on a live rail zeroes settled/reserved — a second spend past the
    original cap is ALLOWED. The ledger is a receipt of the wipe, not a control."""
    td = Path(tempfile.mkdtemp(prefix="ag_spend_reset_"))
    clock = [1000.0]
    g = SpendGate(Ledger(td / "s.jsonl", b"k", "A", clock=lambda: clock[0]),
                  clock=lambda: clock[0])
    g.set_budget("gem", 1.00)
    g.guarded_call("gem", 0.90, lambda: {"usd": 0.90})
    g.set_budget("gem", 1.00)  # same cap, "refresh"
    second_ran = []
    try:
        g.guarded_call("gem", 0.90, lambda: (second_ran.append(1), {"usd": 0.90})[1])
        allowed = True
    except SpendError:
        allowed = False
    settled = g.audit()["rails"]["gem"]["settled_usd"]
    return (allowed and settled >= 0.90,
            f"second_call_allowed={allowed} ran={bool(second_ran)} "
            f"projected_settled={settled} (true spend was $1.80 on a $1 cap)")


@attack("SPEND-NEGATIVE-WORST-CASE")
def _spend_neg():
    """A hanging reservation with negative worst_case_usd creates headroom and
    lets a later call pass a cap it should not."""
    td = Path(tempfile.mkdtemp(prefix="ag_spend_neg_"))
    clock = [1000.0]
    g = SpendGate(Ledger(td / "s.jsonl", b"k", "A", clock=lambda: clock[0]),
                  clock=lambda: clock[0])
    g.set_budget("gem", 1.00)
    hold = threading.Event()
    go = threading.Event()
    err_hang = []

    def hang():
        hold.set()
        go.wait(timeout=5)
        return {"usd": 0.0}

    def blocker():
        try:
            g.guarded_call("gem", -10.0, hang, ttl_s=600)
        except Exception as e:  # noqa: BLE001
            err_hang.append(repr(e))

    t = threading.Thread(target=blocker)
    t.start()
    if not hold.wait(timeout=5):
        go.set(); t.join(timeout=2)
        return True, "hanging negative reserve did not start"
    over = []
    try:
        g.guarded_call("gem", 5.00, lambda: (over.append(5), {"usd": 5.00})[1])
        allowed = True
    except SpendError as e:
        allowed = False
        over.append(e.kind)
    go.set(); t.join(timeout=5)
    return (allowed,
            f"negative_reserve_in_flight; later $5 on $1 cap allowed={allowed} "
            f"detail={over} hang_err={err_hang}")


@attack("SPEND-RID-COLLISION")
def _spend_rid():
    """Frozen clock → identical rid. Two in-flight reserves share a projection key."""
    td = Path(tempfile.mkdtemp(prefix="ag_spend_rid_"))
    clock = [1000.0]
    g = SpendGate(Ledger(td / "s.jsonl", b"k", "A", clock=lambda: clock[0]),
                  clock=lambda: clock[0])
    g.set_budget("gem", 10.00)
    hold = threading.Event()
    go = threading.Event()
    n = threading.Barrier(2)

    def hang():
        n.wait(timeout=5)
        hold.set()
        go.wait(timeout=5)
        return {"usd": 0.10}

    def one():
        g.guarded_call("gem", 1.00, hang, ttl_s=600)

    t1 = threading.Thread(target=one)
    t2 = threading.Thread(target=one)
    t1.start(); t2.start()
    hold.wait(timeout=5)
    reserved_events = [r for r in Ledger(td / "s.jsonl", b"k", "R").verify()
                       if r["event"] == "SPEND_RESERVED"]
    rids = [r["payload"]["rid"] for r in reserved_events]
    go.set(); t1.join(timeout=5); t2.join(timeout=5)
    return (len(rids) >= 2 and len(set(rids)) == 1,
            f"reserved_rids={rids} (m2 harvest: r%d % int(clock*1000))")


@attack("SPEND-AUDIT-SKIPS-EXPIRED-RESERVE")
def _spend_audit_lie():
    """audit() does not sweep expired reservations; headroom keeps lying until
    the next guarded_call happens to sweep."""
    td = Path(tempfile.mkdtemp(prefix="ag_spend_audit_"))
    clock = [1000.0]
    g = SpendGate(Ledger(td / "s.jsonl", b"k", "A", clock=lambda: clock[0]),
                  clock=lambda: clock[0])
    g.set_budget("gem", 1.00)
    hold = threading.Event()
    go = threading.Event()

    def hang():
        hold.set()
        go.wait(timeout=5)
        return {"usd": 0.01}

    t = threading.Thread(target=lambda: g.guarded_call("gem", 0.80, hang, ttl_s=10))
    t.start()
    hold.wait(timeout=5)
    clock[0] = 2000.0  # reservation expired (ttl 10s from 1000)
    a = g.audit()["rails"]["gem"]
    go.set(); t.join(timeout=5)
    return (a["reserved_usd"] > 0 and a["headroom_usd"] < 1.00,
            f"after expiry, audit reserved={a['reserved_usd']} "
            f"headroom={a['headroom_usd']} (sweep is only inside guarded_call)")


@attack("SPEND-RESERVATION-EXPIRED-NOT-RAISED")
def _spend_kinds():
    """A reservation that expires during the call is swept as SPEND_RELEASED
    (or still settled). RESERVATION_EXPIRED is never raised. DOUBLE_SETTLE
    is never raised when two same-rid settles land."""
    td = Path(tempfile.mkdtemp(prefix="ag_spend_kinds_"))
    clock = [1000.0]
    g = SpendGate(Ledger(td / "s.jsonl", b"k", "A", clock=lambda: clock[0]),
                  clock=lambda: clock[0])
    g.set_budget("gem", 10.00)
    hold = threading.Event()
    kinds = []

    def hang():
        hold.set()
        clock[0] = 2000.0  # past ttl
        return {"usd": 0.5}

    try:
        g.guarded_call("gem", 1.00, hang, ttl_s=10)
    except SpendError as e:
        kinds.append(e.kind)
    ev = [r["event"] for r in Ledger(td / "s.jsonl", b"k", "R").verify()]
    return ("RESERVATION_EXPIRED" not in kinds and "SPEND_SETTLED" in ev,
            f"raised={kinds} events={ev} "
            f"(expired-during-call still SETTLED; RESERVATION_EXPIRED absent)")


@attack("SPEND-UNPRICED-INFINITE")
def _spend_unpriced():
    """UNPRICED settle does not consume cap. A loop of unpriced calls is unbounded."""
    td = Path(tempfile.mkdtemp(prefix="ag_spend_unp_"))
    clock = [1000.0]
    g = SpendGate(Ledger(td / "s.jsonl", b"k", "A", clock=lambda: clock[0]),
                  clock=lambda: clock[0])
    g.set_budget("gem", 0.50)
    n = 0
    for i in range(20):
        clock[0] += 1
        g.guarded_call("gem", 0.40, lambda: {"text": "no usd"})
        n += 1
    a = g.audit()["rails"]["gem"]
    return (n == 20 and a["settled_usd"] == 0 and a["unpriced_calls"] == 20,
            f"unpriced_calls={a['unpriced_calls']} settled={a['settled_usd']} "
            f"on cap=0.50 — twenty 40-cent estimates never consumed the cap")


@attack("SPEND-ZERO-WORST-CASE")
def _spend_zero():
    td = Path(tempfile.mkdtemp(prefix="ag_spend_z_"))
    clock = [1000.0]
    g = SpendGate(Ledger(td / "s.jsonl", b"k", "A", clock=lambda: clock[0]),
                  clock=lambda: clock[0])
    g.set_budget("gem", 0.01)
    ran = []
    g.guarded_call("gem", 0.0, lambda: (ran.append(1), {"usd": 99.0})[1])
    a = g.audit()["rails"]["gem"]
    return (bool(ran) and a["settled_usd"] == 99.0,
            f"worst_case=0 reserved then settled $99 on a $0.01 cap; "
            f"settled={a['settled_usd']} (reserve is the gate, settle is a receipt)")


@attack("SPEND-IMPORT-AROUND-KERNEL")
def _spend_import_around():
    """Decision 11 / H4: workers cannot import around the primitives. Anyone
    can construct a SpendGate on the authority ledger and spend."""
    td = Path(tempfile.mkdtemp(prefix="ag_spend_imp_"))
    root = td / "Cosmos"
    install(root, tree_id="imp")
    k = Kernel(root, worker="core")
    # worker-shaped: import the gate, point it at Core's ledger, ignore the kernel
    rogue = SpendGate(k.ledger)
    rogue.set_budget("stolen", 999.0)
    rogue.guarded_call("stolen", 1.0, lambda: {"usd": 1.0})
    ev = [r["event"] for r in k.ledger.verify()]
    return ("SPEND_SETTLED" in ev and "BUDGET_SET" in ev,
            f"rogue SpendGate wrote {ev[-4:]} onto the kernel authority ledger "
            f"with no capability check")


# =====================================================================
# cosmos_context
# =====================================================================

@attack("CTX-CRASH-FORGETS")
def _ctx_crash():
    """H1 / Decision 10: a forgotten fact is a detectable bug. A session that
    dies without close() leaves facts+watchers invisible to boot_inherit —
    no OPEN_CONTEXT, no facts, no incidents."""
    td = Path(tempfile.mkdtemp(prefix="ag_ctx_crash_"))
    led = Ledger(td / "c.jsonl", b"k", "A")
    s = Session(led, "s-crash", "pb")
    s.record_fact("repo", "keithbbf-gif/cosmos")
    s.open_watcher("w-paid", "paid return inbound")
    # crash: no close
    inh = boot_inherit(led)
    forgotten = (inh["facts"] == {} and inh["incidents"] == []
                 and inh["last_handoff"] is None)
    return (forgotten,
            f"boot_inherit after unclosed session={inh} "
            f"(OPEN_CONTEXT events={[r['event'] for r in led.verify()]})")


@attack("CTX-RESOLVE-DROPS-SIBLING")
def _ctx_sibling():
    """WATCHER_RESOLVED matching one wid drops the ENTIRE OPEN_CONTEXT incident,
    including sibling unresolved watchers."""
    td = Path(tempfile.mkdtemp(prefix="ag_ctx_sib_"))
    led = Ledger(td / "c.jsonl", b"k", "A")
    s1 = Session(led, "s1", "pb")
    s1.open_watcher("w-a", "A")
    s1.open_watcher("w-b", "B")
    s1.close("s2", force=True)
    before = boot_inherit(led)
    s2 = Session(led, "s2", "pb")
    s2.open_watcher("w-a", "carried")  # same wid, different session
    s2.resolve_watcher("w-a", "landed")
    s2.close("s3")
    after = boot_inherit(led)
    dropped_b = (before["incidents"]
                 and "w-b" in before["incidents"][0]["unresolved"]
                 and not any("w-b" in i.get("unresolved", {}) for i in after["incidents"]))
    return (dropped_b,
            f"before={before['incidents']} after={after['incidents']} "
            f"(resolving w-a cleared w-b)")


@attack("CTX-WATCHER-AFTER-CLOSE")
def _ctx_after_close():
    """open_watcher does not check _open. A closed session still ledgers
    WATCHER_OPENED after SESSION_CLOSED."""
    td = Path(tempfile.mkdtemp(prefix="ag_ctx_ac_"))
    led = Ledger(td / "c.jsonl", b"k", "A")
    s = Session(led, "s1", "pb")
    s.close("s2")
    try:
        s.open_watcher("late", "should refuse")
        ev = [r["event"] for r in led.verify()]
        return (ev[-1] == "WATCHER_OPENED" and "SESSION_CLOSED" in ev,
                f"events={ev}")
    except ContextError as e:
        return False, f"refused kind={e.kind}"


@attack("CTX-MANIFEST-NO-LEASES")
def _ctx_leases():
    """Decision 10: manifest names inherited facts, active leases, open
    watchers, handoff. Close a clean session and look for leases."""
    td = Path(tempfile.mkdtemp(prefix="ag_ctx_ls_"))
    led = Ledger(td / "c.jsonl", b"k", "A")
    s = Session(led, "s1", "pb")
    s.record_fact("k", "v")
    m = s.close("s2")
    return ("leases" not in m and "active_leases" not in m,
            f"manifest keys={sorted(m.keys())} (no lease field)")


@attack("CTX-DOUBLE-OPEN-SAME-SID")
def _ctx_double():
    td = Path(tempfile.mkdtemp(prefix="ag_ctx_dup_"))
    led = Ledger(td / "c.jsonl", b"k", "A")
    Session(led, "s1", "pb")
    Session(led, "s1", "pb")  # second open, same sid, no refuse
    opens = [r for r in led.verify() if r["event"] == "SESSION_OPENED"]
    return (len(opens) == 2,
            f"SESSION_OPENED count={len(opens)} for one sid")


# =====================================================================
# cosmos_validate
# =====================================================================

@attack("VAL-EMPTY-CLAIMS-ACCEPTED")
def _val_empty():
    """A return that names ZERO validators is RETURN_VALIDATED. The gate
    is optional if the caller simply lists nothing."""
    td = Path(tempfile.mkdtemp(prefix="ag_val_e_"))
    rv = ReturnValidator(Ledger(td / "v.jsonl", b"k", "A"))
    try:
        out = rv.accept("r-empty", [])
        ev = [r["event"] for r in Ledger(td / "v.jsonl", b"k", "R").verify()]
        return (out["rid"] == "r-empty" and "RETURN_VALIDATED" in ev,
                f"accept([]) -> {out} events={ev}")
    except ValidateError as e:
        return False, f"refused kind={e.kind}"


@attack("VAL-EMPTY-QUOTE-MATCHES")
def _val_quote():
    """Whitespace-normalized containment: an empty quote is a substring of
    every source. Fabrication of '' is accepted."""
    td = Path(tempfile.mkdtemp(prefix="ag_val_q_"))
    src = td / "src.txt"
    src.write_text("anything at all\n", encoding="utf-8")
    rv = ReturnValidator(Ledger(td / "v.jsonl", b"k", "A"))
    try:
        out = rv.accept("r-q", [{"validator": "quote_in_source",
                                 "source_path": str(src), "quote": ""}])
        return (out["checks"][0]["ok"] is True,
                f"empty quote accepted: {out['checks'][0]}")
    except ValidateError as e:
        return False, f"refused kind={e.kind}"


@attack("VAL-MISSING-FILE-UNTYPED")
def _val_missing():
    """read_verified on a missing path raises FileNotFoundError, not
    ValidateError. H2: torn/absent state REFUSES by kind."""
    td = Path(tempfile.mkdtemp(prefix="ag_val_m_"))
    try:
        read_verified(td / "never.bin", expect_len=1)
        return True, "missing file returned bytes"
    except ValidateError as e:
        return False, f"typed kind={e.kind}"
    except FileNotFoundError:
        return True, "FileNotFoundError (untyped absence; not SHORT_READ/UNREADABLE)"


@attack("VAL-PATH-EXISTS-DIRECTORY")
def _val_dir():
    """path_exists treats a directory as a successful path claim."""
    td = Path(tempfile.mkdtemp(prefix="ag_val_d_"))
    d = td / "adir"
    d.mkdir()
    rv = ReturnValidator(Ledger(td / "v.jsonl", b"k", "A"))
    try:
        out = rv.accept("r-d", [{"validator": "path_exists", "path": str(d)}])
        return (out["checks"][0]["ok"] is True,
                f"directory accepted as existing path: {out['checks'][0]}")
    except ValidateError as e:
        return False, f"refused kind={e.kind}"


@attack("VAL-PATH-EXISTS-NO-EXTENDED")
def _val_maxpath():
    """v_path_exists uses Path.exists(), not extended(). On Linux this is
    usually invisible; we still prove the call does not go through the
    platform adapter (C-60 contract)."""
    import inspect
    from cosmos_validate import v_path_exists
    src = inspect.getsource(v_path_exists)
    return ("extended" not in src,
            "v_path_exists source has no extended() — MAX_PATH wear as NOT_FOUND "
            "is unaddressed on the validator path")


@attack("VAL-WRITE-NO-VERIFY-AFTER")
def _val_write():
    """write_declared writes and returns len/sha of the INPUT, not of a
    re-read. A short write (disk full) would declare a lie. We demonstrate
    the function never re-reads: monkeypatch is not needed — the returned
    sha is hashlib of `content`, not of the file."""
    import inspect
    from cosmos_validate import write_declared as wd
    src = inspect.getsource(wd)
    rereads = "read(" in src.split("fh.write")[-1]
    return (not rereads,
            "write_declared hashes the argument, never the bytes on disk")


# =====================================================================
# cosmos_platform
# =====================================================================

@attack("PLT-MISSING-BINARY-UNTYPED")
def _plt_missing():
    """run() on a missing argv[0] raises FileNotFoundError, not PlatformError.
    The adapter owns process start; absence of the child is a typed outcome
    (UNREACHABLE / not SHELL_REFUSED / not TIMEOUT)."""
    try:
        run(["cosmos-no-such-binary-9f3a", "--help"], timeout_s=2)
        return True, "missing binary returned a result dict"
    except PlatformError as e:
        return False, f"typed kind={e.kind}"
    except FileNotFoundError:
        return True, "FileNotFoundError leaked through the ONE process door"


@attack("PLT-TREE-KILL-ORPHAN")
def _plt_orphan():
    """run_tree_killed on Linux SIGKILLs the direct child only. A grandchild
    spawned before timeout keeps running (H9 Job-Object / tree-kill contract)."""
    td = Path(tempfile.mkdtemp(prefix="ag_plt_or_"))
    hb = td / "heartbeat.txt"
    pidf = td / "gpid.txt"
    child = (
        "import subprocess, sys, time\n"
        f"hb = {str(hb)!r}\n"
        f"pf = {str(pidf)!r}\n"
        "g = subprocess.Popen([sys.executable, '-c',\n"
        "    'import time,pathlib,sys\\n'\n"
        "    'p=pathlib.Path(sys.argv[1])\\n'\n"
        "    'end=time.time()+12\\n'\n"
        "    'while time.time()<end:\\n'\n"
        "    '    p.write_text(str(time.time())); time.sleep(0.15)\\n',\n"
        "    hb])\n"
        "open(pf,'w').write(str(g.pid))\n"
        "time.sleep(12)\n"
    )
    r = run_tree_killed([sys.executable, "-c", child], timeout_s=1.2)
    time.sleep(0.6)
    alive = False
    gpid = None
    if pidf.exists():
        gpid = int(pidf.read_text().strip() or "0")
        try:
            os.kill(gpid, 0)
            alive = True
        except OSError:
            alive = False
    # also: heartbeat still advancing after parent timed out
    t1 = hb.read_text() if hb.exists() else ""
    time.sleep(0.4)
    t2 = hb.read_text() if hb.exists() else ""
    advancing = t1 != t2 and t2 != ""
    orphan = alive or advancing
    if gpid and alive:
        try:
            os.kill(gpid, 9)
        except OSError:
            pass
    return (orphan and r["timed_out"] is True,
            f"timed_out={r['timed_out']} kill_result={r['kill_result']!r} "
            f"gpid={gpid} grandchild_alive={alive} heartbeat_advancing={advancing}")


@attack("PLT-RUN-TIMEOUT-NOT-TREE")
def _plt_run_timeout():
    """run() TimeoutExpired kills the direct child only (Python default).
    A grandchild keeps running — the adapter's own comment admits this."""
    td = Path(tempfile.mkdtemp(prefix="ag_plt_rt_"))
    hb = td / "hb.txt"
    pidf = td / "gpid.txt"
    child = (
        "import subprocess, sys, time\n"
        f"hb, pf = {str(hb)!r}, {str(pidf)!r}\n"
        "g = subprocess.Popen([sys.executable, '-c',\n"
        "    'import time,pathlib,sys\\n'\n"
        "    'p=pathlib.Path(sys.argv[1])\\n'\n"
        "    'end=time.time()+8\\n'\n"
        "    'while time.time()<end:\\n'\n"
        "    '    p.write_text(str(time.time())); time.sleep(0.15)\\n',\n"
        "    hb])\n"
        "open(pf,'w').write(str(g.pid))\n"
        "time.sleep(8)\n"
    )
    r = run([sys.executable, "-c", child], timeout_s=1.0)
    time.sleep(0.5)
    alive = False
    gpid = None
    if pidf.exists():
        gpid = int(pidf.read_text().strip() or "0")
        try:
            os.kill(gpid, 0)
            alive = True
        except OSError:
            alive = False
    if gpid and alive:
        try:
            os.kill(gpid, 9)
        except OSError:
            pass
    return (r["timed_out"] is True and alive,
            f"run() timed_out={r['timed_out']} kill_result={r['kill_result']!r} "
            f"gpid={gpid} grandchild_alive={alive}")


@attack("PLT-LAUNCHER-NOT-ADAPTED")
def _plt_launcher():
    """The platform adapter is supposed to own encoding/quoting/process start
    so no tool invents a Windows launcher. cosmos_runner hardcodes argv[0]='py'.
    HERE that binary does not exist — measured."""
    r = None
    kind = None
    try:
        r = run(["py", "-3.14", "-c", "print(1)"], timeout_s=3)
        kind = "returned"
    except FileNotFoundError:
        kind = "FileNotFoundError"
    except PlatformError as e:
        kind = e.kind
    return (kind == "FileNotFoundError",
            f"run(['py',...]) -> {kind} result={r} "
            f"(HERE has python3, not the Windows py launcher)")


# =====================================================================
# cosmos_backup
# =====================================================================

@attack("BKP-MISSING-EQ-EMPTY")
def _bkp_missing():
    """Missing source and empty source both raise EMPTY_SCOPE. H2 four-state:
    absent ≠ empty."""
    td = Path(tempfile.mkdtemp(prefix="ag_bkp_me_"))
    tgt = td / "tgt"; tgt.mkdir()
    bk = Backup(Ledger(td / "b.jsonl", b"k", "A"))
    missing_kind = empty_kind = None
    try:
        bk.run(td / "no_such_src", tgt)
    except BackupError as e:
        missing_kind = e.kind
    empty = td / "empty"; empty.mkdir()
    try:
        bk.run(empty, tgt)
    except BackupError as e:
        empty_kind = e.kind
    return (missing_kind == empty_kind == "EMPTY_SCOPE",
            f"missing={missing_kind} empty={empty_kind}")


@attack("BKP-STAMP-COLLISION")
def _bkp_stamp():
    """Stamp is second-resolution localtime. Two runs at the same clock write
    the same dest; the second is not a new backup and can mix trees."""
    td = Path(tempfile.mkdtemp(prefix="ag_bkp_st_"))
    src1 = td / "s1"; src1.mkdir(); (src1 / "a.txt").write_text("A", encoding="utf-8")
    src2 = td / "s2"; src2.mkdir(); (src2 / "b.txt").write_text("B", encoding="utf-8")
    tgt = td / "tgt"; tgt.mkdir()
    clock = [1_700_000_000.0]
    bk = Backup(Ledger(td / "b.jsonl", b"k", "A"), clock=lambda: clock[0])
    r1 = bk.run(src1, tgt)
    r2 = bk.run(src2, tgt)
    mixed = (r1["dest"] == r2["dest"]
             and (Path(r1["dest"]) / "a.txt").exists()
             and (Path(r2["dest"]) / "b.txt").exists())
    return (mixed,
            f"dest1={r1['dest']} dest2={r2['dest']} "
            f"same={r1['dest']==r2['dest']} contents={list(Path(r1['dest']).iterdir())}")


@attack("BKP-MANIFEST-OVERWRITE")
def _bkp_mf():
    """A source file named _MANIFEST.sha256.json is copied, hashed into the
    manifest, then overwritten by the generated manifest. Backup ledgers
    BACKUP_VERIFIED; rehearsal then fails (or would compare the wrong bytes)."""
    td = Path(tempfile.mkdtemp(prefix="ag_bkp_mf_"))
    src = td / "src"; src.mkdir()
    (src / "_MANIFEST.sha256.json").write_text("not-the-manifest", encoding="utf-8")
    (src / "ok.txt").write_text("ok", encoding="utf-8")
    tgt = td / "tgt"; tgt.mkdir()
    bk = Backup(Ledger(td / "b.jsonl", b"k", "A"))
    r = bk.run(src, tgt)
    ev = [x["event"] for x in Ledger(td / "b.jsonl", b"k", "R").verify()]
    dest_mf = Path(r["dest"]) / "_MANIFEST.sha256.json"
    on_disk = dest_mf.read_text(encoding="utf-8")
    stored = json.loads(on_disk)
    source_hash_recorded = stored.get("_MANIFEST.sha256.json")
    # file on disk is JSON, not 'not-the-manifest'
    overwritten = on_disk != "not-the-manifest" and source_hash_recorded
    rehearse_failed = False
    try:
        bk.rehearse_restore(r["dest"], td / "scratch")
    except BackupError as e:
        rehearse_failed = e.kind == "REHEARSAL_FAILED"
    except Exception:  # noqa: BLE001
        rehearse_failed = True
    return (overwritten and "BACKUP_VERIFIED" in ev,
            f"verified_event={'BACKUP_VERIFIED' in ev} overwritten={overwritten} "
            f"rehearse_failed={rehearse_failed} recorded_self_hash={source_hash_recorded}")


@attack("BKP-NOT-A-JOB")
def _bkp_job():
    """Decision 8: backup/rehearse-restore are first-class scheduled job types.
    Backup.run is a library call; it does not submit to the scheduler."""
    import inspect
    from cosmos_backup import Backup as B
    src = inspect.getsource(B.run) + inspect.getsource(B.rehearse_restore)
    return ("sched" not in src.lower() and "job" not in src.lower(),
            "Backup.run/rehearse_restore contain no scheduler/job admission")


@attack("BKP-WALK-NO-EXTENDED")
def _bkp_walk():
    import inspect
    from cosmos_backup import Backup as B
    src = inspect.getsource(B.run)
    return ("rglob" in src and "extended" not in src,
            "Backup.run walks with Path.rglob, not walk()/extended() (C-60 / M7 harvest)")


@attack("BKP-REHEARSE-MISSING-FILE-UNTYPED")
def _bkp_rehearse_missing():
    """Delete a backed-up file after a good run. rehearse copy2 raises
    FileNotFoundError, not REHEARSAL_FAILED."""
    td = Path(tempfile.mkdtemp(prefix="ag_bkp_rm_"))
    src = td / "src"; src.mkdir(); (src / "a.txt").write_text("A", encoding="utf-8")
    tgt = td / "tgt"; tgt.mkdir()
    bk = Backup(Ledger(td / "b.jsonl", b"k", "A"))
    r = bk.run(src, tgt)
    victim = Path(r["dest"]) / "a.txt"
    victim.unlink()
    try:
        bk.rehearse_restore(r["dest"], td / "scratch")
        return True, "rehearsal passed with a missing file"
    except BackupError as e:
        return False, f"typed kind={e.kind}"
    except FileNotFoundError:
        return True, "FileNotFoundError (untyped; not REHEARSAL_FAILED)"


@attack("BKP-UNICODE-FILENAME")
def _bkp_uni():
    """Unicode filename should survive copy+hash (this one is expected to HOLD
    if shutil/utf-8 paths work). Attack: also a combining-char lookalike."""
    td = Path(tempfile.mkdtemp(prefix="ag_bkp_u_"))
    src = td / "src"; src.mkdir()
    name = "caf\u00e9_\u2713.txt"  # café_✓
    (src / name).write_text("ok", encoding="utf-8")
    tgt = td / "tgt"; tgt.mkdir()
    bk = Backup(Ledger(td / "b.jsonl", b"k", "A"))
    r = bk.run(src, tgt)
    dest = Path(r["dest"]) / name
    return (not dest.exists(),
            f"unicode dest exists={dest.exists()} files={list(Path(r['dest']).iterdir())}")


# =====================================================================
# cosmos_health
# =====================================================================

@attack("HLTH-LEASE-ROW-ALWAYS-GREEN")
def _hlth_lease():
    """leases row returns True unconditionally. Hold the tree lease and run
    the board: the leases row stays ok=True (C-46: a checker that cannot go red)."""
    td = Path(tempfile.mkdtemp(prefix="ag_hlth_ls_"))
    root = td / "Cosmos"
    install(root, tree_id="hlth-lease")
    k = Kernel(root, worker="core")
    lease = k.arbiter.acquire("tree", "attacker")
    b = HealthBoard(k).run()
    row = b["rows"]["leases"]
    k.arbiter.release(lease)
    return (row["ok"] is True,
            f"tree is HELD by attacker token={lease.token}; "
            f"leases row={row} (cannot go RED for a live/held/stale lease)")


@attack("HLTH-BOARD-SKIPS-GUARDS")
def _hlth_skip():
    """The board claims every subsystem is asked to PROVE itself. After a
    healthy boot, spend/backup/validate/context/platform are not rows."""
    td = Path(tempfile.mkdtemp(prefix="ag_hlth_"))
    root = td / "Cosmos"
    install(root, tree_id="hlth")
    k = Kernel(root, worker="core")
    b = HealthBoard(k).run()
    names = set(b["rows"]) | {"negative control (must be RED)"}
    needed = {"spend", "backup", "validate", "context", "platform"}
    missing = [n for n in needed if not any(n in x.lower() for x in b["rows"])]
    return (bool(missing) and b["verdict"] == "GREEN",
            f"rows={list(b['rows'])} missing_guard_rows={missing} verdict={b['verdict']}")


@attack("HLTH-EMPTY-LEDGER-GREEN")
def _hlth_empty_ok():
    """ledger chain row is GREEN on any verify() that doesn't raise, including
    a brand-new chain that has only BOOT_VERIFIED. Not itself a defect — we
    attack the stronger claim: the board is GREEN while spend has no budget
    and backup has never rehearsed. That is a checker that cannot see absence."""
    td = Path(tempfile.mkdtemp(prefix="ag_hlth2_"))
    root = td / "Cosmos"
    install(root, tree_id="hlth2")
    k = Kernel(root, worker="core")
    b = HealthBoard(k).run()
    spend_events = [r["event"] for r in k.ledger.verify()
                    if r["event"].startswith("SPEND") or r["event"].startswith("BUDGET")]
    backup_events = [r["event"] for r in k.ledger.verify()
                     if "BACKUP" in r["event"] or "RESTORE" in r["event"]]
    return (b["verdict"] == "GREEN" and not spend_events and not backup_events,
            f"verdict={b['verdict']} spend_events={spend_events} "
            f"backup_events={backup_events}")


# =====================================================================
# runner
# =====================================================================

def main() -> int:
    # execute every @attack in definition order
    for fn in (
        _spend_race, _spend_reset, _spend_neg, _spend_rid,
        _spend_audit_lie, _spend_kinds, _spend_unpriced, _spend_zero,
        _spend_import_around,
        _ctx_crash, _ctx_sibling, _ctx_after_close, _ctx_leases, _ctx_double,
        _val_empty, _val_quote, _val_missing, _val_dir, _val_maxpath, _val_write,
        _plt_missing, _plt_orphan, _plt_run_timeout, _plt_launcher,
        _bkp_missing, _bkp_stamp, _bkp_mf, _bkp_job, _bkp_walk,
        _bkp_rehearse_missing, _bkp_uni,
        _hlth_lease, _hlth_skip, _hlth_empty_ok,
    ):
        fn()

    broken = [(i, d) for i, st, d in RESULTS if st == "BROKEN"]
    held = [(i, d) for i, st, d in RESULTS if st == "HELD"]
    errors = [(i, d) for i, st, d in RESULTS if st == "ERROR"]
    for aid, st, detail in RESULTS:
        print(f"  {st:6}  {aid}  — {detail}")
    print(f"ATTACK_GUARDS {len(broken)} BROKEN / {len(held)} HELD / {len(errors)} ERROR "
          f"of {len(RESULTS)}")
    # harness itself ran; BROKEN is the finding, not a harness crash
    return 0 if not errors else 2


def test_attack_guards_harness_runs():
    """The attack harness must execute. BROKEN lines are findings, not pytest failures."""
    assert main() in (0, 2)


if __name__ == "__main__":
    sys.exit(main())
