#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bite: P07 Layer A spawn grant ≠ Layer B fencing token.

    py -3.14 cosmos/_bite_p07_layer_ab.py
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent / "cosmos"
sys.path.insert(0, str(HERE))

from cosmos_lock import Lease  # noqa: E402
from cosmos_spawn_grant import (  # noqa: E402
    SpawnGrant, SpawnGrantError, assert_granted, refuse_as_fencing_token,
)

OUT = HERE / "_bite_p07_layer_ab.json"


def main() -> int:
    td = Path(tempfile.mkdtemp(prefix="cosmos_bite_p07_"))
    grant_root = td / "attempt"
    grant_root.mkdir()
    inside = grant_root / "out.txt"
    outside = td / "desktop" / "escape.txt"
    outside.parent.mkdir()

    grant = SpawnGrant(grant_root, "p07-sid")
    fence = Lease("tree", "GROK", token=3, granted_at=0.0, expires_at=9.0)

    types_distinct = grant.kind == "layer-a-folder-grant" and isinstance(fence.token, int)
    not_same_object = grant is not fence and not isinstance(grant, type(fence))

    assert_granted(grant, inside)
    denied = None
    try:
        assert_granted(grant, outside)
    except SpawnGrantError as e:
        denied = e.kind

    not_a_grant = None
    try:
        assert_granted(fence.token, inside)
    except SpawnGrantError as e:
        not_a_grant = e.kind

    collapse = None
    try:
        refuse_as_fencing_token(grant)
    except SpawnGrantError as e:
        collapse = e.kind

    rec = {
        "types_distinct": types_distinct,
        "not_same_object": not_same_object,
        "inside_allowed": grant.allows(inside),
        "outside_denied_kind": denied,
        "int_token_not_a_grant": not_a_grant,
        "grant_as_fence_kind": collapse,
        "grant_kind": grant.kind,
        "fence_token_type": type(fence.token).__name__,
    }
    rec["all_bite"] = (
        rec["types_distinct"] is True
        and rec["not_same_object"] is True
        and rec["inside_allowed"] is True
        and rec["outside_denied_kind"] == "GRANT_DENIED"
        and rec["int_token_not_a_grant"] == "NOT_A_GRANT"
        and rec["grant_as_fence_kind"] == "LAYER_COLLAPSE"
    )
    OUT.write_text(json.dumps(rec, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(rec, indent=2))
    return 0 if rec["all_bite"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
