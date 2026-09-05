#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Chief Coder lease — one writer of the COSMOS live tree at a time.

Contract: docs/CCR.md. Presence of state/control/CCR.lease is the write token.
A second acquire REFUSES. No lease → not CCr. Does not touch the ledger.
Not wired into Watchdog2 this file; callers must check held().
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path

from cosmos_clock import atomic_json
from cosmos_paths import CosmosPaths

LEASE_NAME = "CCR.lease"
SCHEMA = "cosmos-ccr-lease/1"


class CcrError(RuntimeError):
    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


def lease_path(paths: CosmosPaths) -> Path:
    return paths.role("state", "control", LEASE_NAME)


def read_lease(paths: CosmosPaths) -> dict | None:
    p = lease_path(paths)
    if not p.is_file():
        return None
    try:
        raw = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        raise CcrError("UNPARSEABLE", f"{p}: {e}") from e
    if not isinstance(raw, dict):
        raise CcrError("UNPARSEABLE", f"{p}: not an object")
    return raw


def held(paths: CosmosPaths) -> bool:
    return read_lease(paths) is not None


def acquire(paths: CosmosPaths, *, sid: str, pid: int, stream: str = "Cm") -> dict:
    """Take the CCr lease. REFUSES if one is already present."""
    cur = read_lease(paths)
    if cur is not None:
        raise CcrError(
            "CCR_HELD",
            f"lease held by sid={cur.get('sid')!r} pid={cur.get('pid')!r}",
        )
    rec = {
        "schema": SCHEMA,
        "sid": str(sid),
        "pid": int(pid),
        "stream": str(stream),
        "tree_id": paths.sentinel.tree_id,
        "taken_at": time.time(),
        "taken_pid": os.getpid(),
    }
    atomic_json(lease_path(paths), rec)
    back = read_lease(paths)
    if not back or back.get("sid") != rec["sid"]:
        raise CcrError("ROUND_TRIP_UNVERIFIED", "lease write did not read back")
    return back


def release(paths: CosmosPaths, *, sid: str) -> None:
    """Drop the lease. REFUSES if sid does not match. Missing lease is a no-op."""
    cur = read_lease(paths)
    if cur is None:
        return
    if str(cur.get("sid")) != str(sid):
        raise CcrError(
            "CCR_SID_MISMATCH",
            f"held sid={cur.get('sid')!r} release sid={sid!r}",
        )
    p = lease_path(paths)
    p.unlink()


def status(paths: CosmosPaths) -> dict:
    cur = read_lease(paths)
    return {
        "held": cur is not None,
        "lease": cur,
        "path": str(lease_path(paths)),
    }
