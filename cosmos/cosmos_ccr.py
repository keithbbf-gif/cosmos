#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Chief Coder lease — one writer of the COSMOS live tree at a time.

Contract: docs/CCR.md. Presence of state/control/CCR.lease is the write token.
A second acquire REFUSES. No lease → not CCr. Does not touch the authority
ledger. Not wired into Watchdog2 this file; callers must check held().

Opus P0: the file is a projection (schema cosmos-ccr-lease/2). Authority
for TTL / fencing token / renew is cosmos_lock.Arbiter on resource
CCR.lease. Legacy schema /1 (no token) is honored until that sid
releases — do not evict, do not invent a TTL.
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path

from cosmos_clock import atomic_json
from cosmos_lock import Arbiter, Lease, LockError
from cosmos_paths import CosmosPaths

LEASE_NAME = "CCR.lease"
ARB_LEDGER_NAME = "CCR.lease.jsonl"
SCHEMA = "cosmos-ccr-lease/2"
SCHEMA_LEGACY = "cosmos-ccr-lease/1"
CCR_RESOURCE = "CCR.lease"
DEFAULT_TTL_S = 90 * 60


class CcrError(RuntimeError):
    """kind in {CCR_HELD, CCR_SID_MISMATCH, UNPARSEABLE, ROUND_TRIP_UNVERIFIED,
    CCR_NO_LEASE, CCR_STALE_TOKEN}."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


def lease_path(paths: CosmosPaths) -> Path:
    return paths.role("state", "control", LEASE_NAME)


def arbiter_ledger_path(paths: CosmosPaths) -> Path:
    return paths.role("state", "control", ARB_LEDGER_NAME)


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


def is_legacy(rec: dict | None) -> bool:
    """True for schema /1 or a projection with no fencing token."""
    if not rec:
        return False
    schema = str(rec.get("schema") or "")
    if schema == SCHEMA_LEGACY:
        return True
    if schema == SCHEMA:
        return False
    return rec.get("token") is None


def _expired(rec: dict, now: float) -> bool:
    if is_legacy(rec):
        return False
    exp = rec.get("expires_at")
    if exp is None:
        return False
    try:
        return now >= float(exp)
    except (TypeError, ValueError):
        return False


def _arbiter(paths: CosmosPaths, clock) -> Arbiter:
    return Arbiter(arbiter_ledger_path(paths), clock=clock,
                   default_ttl=DEFAULT_TTL_S)


def held(paths: CosmosPaths, clock=time.time) -> bool:
    cur = read_lease(paths)
    if cur is None:
        return False
    if is_legacy(cur):
        return True
    return not _expired(cur, float(clock()))


def assert_pen(paths: CosmosPaths, *, sid: str, clock=time.time) -> None:
    """SkillRegistry.accept / reject: live lease must match this sid."""
    rec = read_lease(paths)
    if rec is None or not held(paths, clock=clock):
        raise CcrError("CCR_NO_LEASE", "no live CCR.lease")
    if str(rec.get("sid")) != str(sid):
        raise CcrError(
            "CCR_SID_MISMATCH",
            f"held sid={rec.get('sid')!r} pen sid={sid!r}",
        )


def acquire(paths: CosmosPaths, *, sid: str, pid: int, stream: str = "Cm",
            ttl: float | None = None, clock=time.time) -> dict:
    """Take the CCr lease via Arbiter. REFUSES if one is already live.

    Legacy /1 is held until that sid releases (no TTL steal).
    Expired /2 is free — Arbiter TAKEOVER after EXPIRE.
    """
    now = float(clock())
    cur = read_lease(paths)
    if cur is not None and (is_legacy(cur) or not _expired(cur, now)):
        raise CcrError(
            "CCR_HELD",
            f"lease held by sid={cur.get('sid')!r} pid={cur.get('pid')!r} "
            f"schema={cur.get('schema')!r}",
        )
    arb = _arbiter(paths, clock)
    lease = arb.acquire(CCR_RESOURCE, str(sid), ttl=ttl)
    rec = {
        "schema": SCHEMA,
        "sid": str(sid),
        "pid": int(pid),
        "stream": str(stream),
        "tree_id": paths.sentinel.tree_id,
        "taken_at": float(lease.granted_at),
        "taken_pid": os.getpid(),
        "token": int(lease.token),
        "expires_at": float(lease.expires_at),
        "granted_at": float(lease.granted_at),
    }
    atomic_json(lease_path(paths), rec)
    back = read_lease(paths)
    if not back or back.get("sid") != rec["sid"] or back.get("token") != rec["token"]:
        raise CcrError("ROUND_TRIP_UNVERIFIED", "lease write did not read back")
    return back


def renew(paths: CosmosPaths, *, sid: str, ttl: float | None = None,
          clock=time.time) -> dict:
    """Extend TTL under the current fencing token. Legacy /1 is a no-op."""
    cur = read_lease(paths)
    if cur is None:
        raise CcrError("CCR_NO_LEASE", "no CCR.lease to renew")
    if str(cur.get("sid")) != str(sid):
        raise CcrError(
            "CCR_SID_MISMATCH",
            f"held sid={cur.get('sid')!r} renew sid={sid!r}",
        )
    if is_legacy(cur):
        return cur
    try:
        lease = Lease(
            resource=CCR_RESOURCE,
            holder=str(sid),
            token=int(cur["token"]),
            granted_at=float(cur.get("granted_at") or cur.get("taken_at") or 0.0),
            expires_at=float(cur.get("expires_at") or 0.0),
        )
        nxt = _arbiter(paths, clock).renew(lease, ttl=ttl)
    except LockError as e:
        kind = "CCR_STALE_TOKEN" if e.kind == "STALE_TOKEN" else e.kind
        raise CcrError(kind, str(e)) from e
    except (KeyError, TypeError, ValueError) as e:
        raise CcrError("UNPARSEABLE", f"projection missing token: {e}") from e
    out = dict(cur)
    out["schema"] = SCHEMA
    out["token"] = int(nxt.token)
    out["expires_at"] = float(nxt.expires_at)
    atomic_json(lease_path(paths), out)
    back = read_lease(paths)
    if not back or back.get("token") != out["token"]:
        raise CcrError("ROUND_TRIP_UNVERIFIED", "renew write did not read back")
    return back


def release(paths: CosmosPaths, *, sid: str, clock=time.time) -> None:
    """Drop the lease. REFUSES if sid does not match. Missing lease is a no-op."""
    cur = read_lease(paths)
    if cur is None:
        return
    if str(cur.get("sid")) != str(sid):
        raise CcrError(
            "CCR_SID_MISMATCH",
            f"held sid={cur.get('sid')!r} release sid={sid!r}",
        )
    if not is_legacy(cur) and cur.get("token") is not None:
        try:
            lease = Lease(
                resource=CCR_RESOURCE,
                holder=str(sid),
                token=int(cur["token"]),
                granted_at=float(cur.get("granted_at") or cur.get("taken_at") or 0.0),
                expires_at=float(cur.get("expires_at") or 0.0),
            )
            _arbiter(paths, clock).release(lease)
        except (LockError, TypeError, ValueError, KeyError, OSError):
            pass
    p = lease_path(paths)
    p.unlink()


def status(paths: CosmosPaths, clock=time.time) -> dict:
    cur = read_lease(paths)
    now = float(clock())
    return {
        "held": held(paths, clock=clock),
        "lease": cur,
        "path": str(lease_path(paths)),
        "schema": (cur or {}).get("schema"),
        "legacy": is_legacy(cur) if cur else False,
        "expired": bool(cur) and _expired(cur, now),
    }
