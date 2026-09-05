#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""F-28: HANDS files vs COMPETENCY.toml [nodes.*] — from the files, not prose.

    py -3.14 builds/probe/_emit_f28_census.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from cosmos_newai_scout import (  # noqa: E402
    inventory_from_competency, inventory_from_hands, norm,
)

REPO = HERE.parents[1]
OUT = HERE / "_f28_hands_vs_nodes.json"
_NODES = re.compile(r"^\[nodes\.([A-Za-z0-9_-]+)\]\s*$", re.M)


def main() -> int:
    toml = (REPO / "docs" / "COMPETENCY.toml").read_text(encoding="utf-8")
    nodes = sorted(inventory_from_competency(toml))
    hands = sorted(inventory_from_hands(REPO))
    node_keys = {norm(n) for n in nodes}
    unmapped = []
    mapped = []
    for h in hands:
        if norm(h) in node_keys:
            mapped.append(h)
        else:
            unmapped.append(h)
    # Dedup unmapped by norm (Aider / AIDER / Aider-style stems).
    seen = set()
    unmapped_unique = []
    for h in unmapped:
        k = norm(h)
        if k in seen or k in node_keys:
            continue
        # skip if any token of a node is this stem (PLAYWRIGHT vs DOM is NOT auto)
        seen.add(k)
        unmapped_unique.append(h)
    rec = {
        "schema": "cosmos-f28-census/1",
        "toml_bytes": len(toml.encode("utf-8")),
        "node_count": len(nodes),
        "nodes": nodes,
        "hands_stems": hands,
        "unmapped_hands": unmapped_unique,
        "unmapped_count": len(unmapped_unique),
        # Re-measured 2026-08-31T14:36Z: live_six_nodes is a SUPERSET
        # (required_six <= live_nodes). Adding a [nodes.X] row does NOT
        # fail tests/test_competency.py. The 14:09Z census that claimed
        # otherwise is staged at
        # docs/_delme/predispose_competency_f28_20260831T145400Z/.
        "live_six_nodes_pin_would_break_if_we_add": False,
        "pin": (
            "tests/test_competency.py live_six_nodes SUPERSET "
            "required_six <= live_nodes"
        ),
        "why_not_filed": (
            "filed 2026-08-31T1454Z possessed=false rating=0 HANDS-cited "
            "source; ratings not invented; router.nodes_order still the live six"
            if not unmapped_unique else
            "unmapped HANDS stems remain; file possessed=false rating=0 rows"
        ),
    }
    OUT.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({k: rec[k] for k in (
        "node_count", "nodes", "unmapped_count", "unmapped_hands")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
