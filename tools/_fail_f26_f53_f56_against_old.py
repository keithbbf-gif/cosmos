#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prove F-26 GH-parser / F-53 prepaid orch / F-56 LAN-node pins FAIL
against the staged predecessor.

Loads `_delme/predispose_f26_f53_f56_20260831T143641Z/` by path.
all_new_pins_failed is the bite. Does not import the live new modules.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OLD = REPO / "_delme" / "predispose_f26_f53_f56_20260831T143641Z"
OUT = REPO / "cosmos" / "_fail_f26_f53_f56_against_old.json"

GH_SAMPLE = """
| 1 | [anomalyco/opencode](https://github.com/anomalyco/opencode) | 202.6k | +1958 |
| 2 | [Aider-AI/aider](https://github.com/Aider-AI/aider) | 48.6k | +180 |
| 3 | [cline/cline](https://github.com/cline/cline) | 67.2k | +468 |
"""


def load(name: str, filename: str):
    sys.path.insert(0, str(REPO / "cosmos"))
    spec = importlib.util.spec_from_file_location(name, OLD / filename)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    scout = load("scout_old", "cosmos_newai_scout.py")
    clocks = load("own_clocks_old", "cosmos_own_clocks.py")
    ident = load("identity_old", "cosmos_identity.py")
    ids = [c.get("id") for c in clocks.CLOCKS]
    parsed = scout.parse_catalog(GH_SAMPLE, "gh-sample")
    folds = {r.get("fold") for r in parsed}
    ident_text = (OLD / "cosmos_identity.py").read_text(encoding="utf-8")
    pins = {
        "gh_parser_lifts_opencode": "opencode" in folds,
        "clock_24_prepaid_orch": any(
            c.get("id") == 24 and "Prepaid" in str(c.get("task") or "")
            for c in clocks.CLOCKS),
        "prepaid_orch_module_staged": (OLD / "cosmos_prepaid_orch.py").is_file(),
        "LAN_NODES_attr": hasattr(ident, "LAN_NODES"),
        "SRV1_symbol": "SRV1" in ident_text,
        "T7920_symbol": "T7920" in ident_text,
        "probe_lan_node_fn": hasattr(ident, "probe_lan_node"),
    }
    rec = {
        "schema": "cosmos-f26-f53-f56-fail-old/1",
        "old_dir": str(OLD),
        "old_clock_count": len(clocks.CLOCKS),
        "old_max_id": max(ids) if ids else None,
        "old_ids": ids,
        "old_gh_folds": sorted(folds),
        "old_gh_count": len(parsed),
        "pins": pins,
        "all_new_pins_failed": all(v is False for v in pins.values()),
    }
    OUT.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(rec, indent=1))
    return 0 if rec["all_new_pins_failed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
