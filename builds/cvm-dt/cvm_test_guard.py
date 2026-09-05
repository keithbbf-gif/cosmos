#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fence test guard — a suite may only heartbeat/lock into a SCRATCH root.

Why this exists (CLOCK_POSTMORTEM.md, residual finding): a suite that writes
the *production* heartbeat path freshens a dead worker's `last_run_epoch`, so
"the heartbeat is fresh" stops meaning "the daemon is alive". That is a signal
producible by something other than the thing it measures — the false-green
class this fence exists to close. Observing that the suites happen to be clean
today is weaker than making a leak impossible to commit quietly.

The rule is path-free and therefore needs no notion of where production is:
**every heartbeat and lock a suite writes must land under the OS temp dir.**
Anything else is a typed refusal at the moment of the write, naming the
target — not a silent production write discovered days later.

    from cvm_test_guard import sandbox_heartbeats
    with sandbox_heartbeats():
        ...run the suite...

Rebinding is done across `sys.modules` because the workers import the helpers
by value (`from cosmos_clock import write_heartbeat`), so patching
`cosmos_clock` alone would miss every caller that already holds a reference.
"""
from __future__ import annotations

import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "cosmos"))

import cosmos_clock  # noqa: E402


class ProductionWriteRefused(RuntimeError):
    """A suite aimed a heartbeat/lock at a path outside the scratch root."""


def _scratch_ok(path: Path) -> bool:
    tmp = Path(tempfile.gettempdir()).resolve()
    try:
        Path(path).resolve().relative_to(tmp)
    except (ValueError, OSError):
        return False
    return True


def _refuse(kind: str, path) -> None:
    raise ProductionWriteRefused(
        "[PROD_WRITE_REFUSED] %s target %r is not under the scratch root %r - "
        "tests write a temp root, never live/logs (CLOCK_POSTMORTEM residual)"
        % (kind, str(path), tempfile.gettempdir()))


def _rebind(name: str, old, new) -> list:
    """Point every module that already imported `old` by value at `new`."""
    hits = []
    for mod in list(sys.modules.values()):
        if mod is None:
            continue
        if getattr(mod, name, None) is old:
            setattr(mod, name, new)
            hits.append(mod)
    return hits


@contextmanager
def sandbox_heartbeats():
    """Refuse, fail-closed, any heartbeat/lock write outside the temp dir."""
    real_hb, real_lock = cosmos_clock.write_heartbeat, cosmos_clock.acquire_lock

    def guarded_write_heartbeat(path, *a, **kw):
        if not _scratch_ok(path):
            _refuse("heartbeat", path)
        return real_hb(path, *a, **kw)

    def guarded_acquire_lock(lock_path, *a, **kw):
        if not _scratch_ok(lock_path):
            _refuse("lock", lock_path)
        return real_lock(lock_path, *a, **kw)

    hb_mods = _rebind("write_heartbeat", real_hb, guarded_write_heartbeat)
    lk_mods = _rebind("acquire_lock", real_lock, guarded_acquire_lock)
    try:
        yield {"heartbeat_modules": len(hb_mods), "lock_modules": len(lk_mods)}
    finally:
        _rebind("write_heartbeat", guarded_write_heartbeat, real_hb)
        _rebind("acquire_lock", guarded_acquire_lock, real_lock)
