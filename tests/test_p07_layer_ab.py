#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""P07: Layer A spawn grant is not Layer B fencing token."""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "cosmos"))

from cosmos_lock import Lease  # noqa: E402
from cosmos_spawn_grant import (  # noqa: E402
    SpawnGrant, SpawnGrantError, assert_granted, refuse_as_fencing_token,
)


def test_grant_is_not_fencing_token():
    td = Path(tempfile.mkdtemp(prefix="p07_"))
    g = SpawnGrant(td, "s1")
    fence = Lease("tree", "GROK", token=4, granted_at=0.0, expires_at=9.0)
    assert g.kind == "layer-a-folder-grant"
    assert isinstance(fence.token, int)
    assert g.kind != str(fence.token)
    try:
        refuse_as_fencing_token(g)
    except SpawnGrantError as e:
        assert e.kind == "LAYER_COLLAPSE"
    else:
        raise AssertionError("spawn grant must not pass as fencing token")
    try:
        assert_granted(fence.token, td / "x")
    except SpawnGrantError as e:
        assert e.kind == "NOT_A_GRANT"
    else:
        raise AssertionError("int fencing token must not pass as grant")


def test_write_outside_grant_denied():
    td = Path(tempfile.mkdtemp(prefix="p07g_"))
    root = td / "grant"
    root.mkdir()
    g = SpawnGrant(root, "s1")
    assert_granted(g, root / "ok.txt")
    try:
        assert_granted(g, td / "escape.txt")
    except SpawnGrantError as e:
        assert e.kind == "GRANT_DENIED"
    else:
        raise AssertionError("outside grant must GRANT_DENIED")


def main() -> int:
    test_grant_is_not_fencing_token()
    test_write_outside_grant_denied()
    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
