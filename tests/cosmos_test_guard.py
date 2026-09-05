#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fence test guard — a suite may only heartbeat/lock into a SCRATCH root.

F-60. Same contract as builds/cvm-dt/cvm_test_guard.py, owned under tests/
so the collector / node-bucket suites (this fence) can import it without
touching builds/cvm-dt/ (another session's fence) or builds/health/.

The rule is path-free: every heartbeat and lock a suite writes must land
under the OS temp dir. Anything else is PROD_WRITE_REFUSED at the write,
naming the target.

CLOCKS leftover (F-60): `cosmos_clock.run_schtasks` / `harden_task` are
native writers. A Python heartbeat fence does not see `schtasks.exe`.
This guard wraps those helpers too: `/create` `/delete` `/change` `/run`
`/end` and `harden_task` are PROD_WRITE_REFUSED. `/query` stays readable
in the parent. Descendant `--once` children inherit
`COSMOS_SCHTASKS_SANDBOX=1` so `cosmos_clock.run_schtasks` never invokes
the native binary (health suite leftover). Tests inject; they do not
register production tasks.

    from cosmos_test_guard import sandbox_heartbeats
    with sandbox_heartbeats():
        ...run the suite...

Rebinding walks sys.modules because workers import helpers by value
(`from cosmos_clock import write_heartbeat`).
"""
from __future__ import annotations

import os
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "cosmos"))

import cosmos_clock  # noqa: E402


class ProductionWriteRefused(RuntimeError):
    """kind = PROD_WRITE_REFUSED. A suite aimed a write outside the scratch root."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


def _scratch_ok(path: Path) -> bool:
    tmp = Path(tempfile.gettempdir()).resolve()
    try:
        Path(path).resolve().relative_to(tmp)
    except (ValueError, OSError):
        return False
    return True


def _refuse(kind: str, path) -> None:
    raise ProductionWriteRefused(
        "PROD_WRITE_REFUSED",
        "%s target %r is not under the scratch root %r - tests write a "
        "temp root, never live/logs (CLOCK_POSTMORTEM residual)"
        % (kind, str(path), tempfile.gettempdir()))


def _rebind(name: str, old, new) -> list:
    hits = []
    for mod in list(sys.modules.values()):
        if mod is None:
            continue
        if getattr(mod, name, None) is old:
            setattr(mod, name, new)
            hits.append(mod)
    return hits


_SCHTASKS_WRITE_VERBS = ("/create", "/delete", "/change", "/run", "/end")


def _schtasks_writes(argv) -> bool:
    """True iff argv would mutate the Windows task table (CLOCKS writers)."""
    if not argv:
        return False
    parts = [str(x).lower() for x in argv]
    joined = " ".join(parts)
    if "schtasks" not in joined:
        return False
    return any(v in joined for v in _SCHTASKS_WRITE_VERBS)


@contextmanager
def sandbox_heartbeats():
    """Refuse, fail-closed, any heartbeat/lock write outside the temp dir,
    and any CLOCKS schtasks writer (`run_schtasks` / `harden_task`)."""
    real_hb, real_lock = cosmos_clock.write_heartbeat, cosmos_clock.acquire_lock
    real_sch = cosmos_clock.run_schtasks
    real_harden = cosmos_clock.harden_task

    def guarded_write_heartbeat(path, *a, **kw):
        if not _scratch_ok(path):
            _refuse("heartbeat", path)
        return real_hb(path, *a, **kw)

    def guarded_acquire_lock(lock_path, *a, **kw):
        if not _scratch_ok(lock_path):
            _refuse("lock", lock_path)
        return real_lock(lock_path, *a, **kw)

    def guarded_run_schtasks(argv, *a, **kw):
        if _schtasks_writes(argv):
            _refuse("schtasks", " ".join(str(x) for x in argv))
        return real_sch(argv, *a, **kw)

    def guarded_harden_task(task_name, *a, **kw):
        _refuse("schtasks", "harden_task %r" % (task_name,))

    hb_mods = _rebind("write_heartbeat", real_hb, guarded_write_heartbeat)
    lk_mods = _rebind("acquire_lock", real_lock, guarded_acquire_lock)
    sch_mods = _rebind("run_schtasks", real_sch, guarded_run_schtasks)
    hd_mods = _rebind("harden_task", real_harden, guarded_harden_task)
    cosmos_clock.write_heartbeat = guarded_write_heartbeat
    cosmos_clock.acquire_lock = guarded_acquire_lock
    cosmos_clock.run_schtasks = guarded_run_schtasks
    cosmos_clock.harden_task = guarded_harden_task
    prev_env = os.environ.get("COSMOS_SCHTASKS_SANDBOX")
    os.environ["COSMOS_SCHTASKS_SANDBOX"] = "1"
    try:
        yield {
            "heartbeat_modules": len(hb_mods),
            "lock_modules": len(lk_mods),
            "schtasks_modules": len(sch_mods),
            "harden_modules": len(hd_mods),
        }
    finally:
        if prev_env is None:
            os.environ.pop("COSMOS_SCHTASKS_SANDBOX", None)
        else:
            os.environ["COSMOS_SCHTASKS_SANDBOX"] = prev_env
        _rebind("write_heartbeat", guarded_write_heartbeat, real_hb)
        _rebind("acquire_lock", guarded_acquire_lock, real_lock)
        _rebind("run_schtasks", guarded_run_schtasks, real_sch)
        _rebind("harden_task", guarded_harden_task, real_harden)
        cosmos_clock.write_heartbeat = real_hb
        cosmos_clock.acquire_lock = real_lock
        cosmos_clock.run_schtasks = real_sch
        cosmos_clock.harden_task = real_harden
