#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Isolated tests for cosmos_ccr. No live-tree writes."""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

_here = Path(__file__).resolve().parent
_root = _here.parent
sys.path.insert(0, str(_root / "cosmos"))

from cosmos_ccr import (  # noqa: E402
    SCHEMA, SCHEMA_LEGACY, CcrError, acquire, held, is_legacy, read_lease,
    release, renew, status,
)
from cosmos_clock import atomic_json  # noqa: E402
from cosmos_paths import CosmosPaths, write_sentinel  # noqa: E402


def _live():
    td = Path(tempfile.mkdtemp(prefix="cosmos_ccr_"))
    live = td / "live"
    write_sentinel(live, tree_id="ccr-selftest")
    (live / "state" / "control").mkdir(parents=True)
    return CosmosPaths(live)


def test_acquire_held_release():
    p = _live()
    assert held(p) is False
    rec = acquire(p, sid="s1", pid=11, stream="Cm")
    assert rec["sid"] == "s1"
    assert held(p) is True
    st = status(p)
    assert st["held"] is True
    release(p, sid="s1")
    assert held(p) is False


def test_second_acquire_refuses():
    p = _live()
    acquire(p, sid="s1", pid=1)
    try:
        acquire(p, sid="s2", pid=2)
    except CcrError as e:
        assert e.kind == "CCR_HELD"
    else:
        raise AssertionError("second acquire must REFUSE")


def test_wrong_sid_release_refuses():
    p = _live()
    acquire(p, sid="s1", pid=1)
    try:
        release(p, sid="other")
    except CcrError as e:
        assert e.kind == "CCR_SID_MISMATCH"
    else:
        raise AssertionError("mismatched release must REFUSE")
    assert held(p) is True


def test_release_missing_is_noop():
    p = _live()
    release(p, sid="nobody")
    assert held(p) is False


def test_acquire_is_schema_v2_with_token():
    p = _live()
    rec = acquire(p, sid="s1", pid=11)
    assert rec["schema"] == SCHEMA
    assert int(rec["token"]) >= 1
    assert rec.get("expires_at")
    nxt = renew(p, sid="s1")
    assert nxt["token"] == rec["token"]
    assert nxt["expires_at"] >= rec["expires_at"]
    release(p, sid="s1")


def test_legacy_v1_honored_until_sid_releases():
    p = _live()
    atomic_json(p.role("state", "control", "CCR.lease"), {
        "schema": SCHEMA_LEGACY,
        "sid": "old-sid",
        "pid": 7,
        "stream": "Cm",
        "tree_id": "ccr-selftest",
        "taken_at": 1.0,
        "taken_pid": 7,
    })
    assert is_legacy(read_lease(p)) is True
    assert held(p) is True
    try:
        acquire(p, sid="new-sid", pid=8)
    except CcrError as e:
        assert e.kind == "CCR_HELD"
    else:
        raise AssertionError("legacy /1 must block acquire until release")
    release(p, sid="old-sid")
    rec = acquire(p, sid="new-sid", pid=8)
    assert rec["schema"] == SCHEMA
    release(p, sid="new-sid")


if __name__ == "__main__":
    test_acquire_held_release()
    test_second_acquire_refuses()
    test_wrong_sid_release_refuses()
    test_release_missing_is_noop()
    test_acquire_is_schema_v2_with_token()
    test_legacy_v1_honored_until_sid_releases()
    print("ok")
