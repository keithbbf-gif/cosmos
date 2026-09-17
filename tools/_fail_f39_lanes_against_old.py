#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prove the F-39 BTS-lane-accounting-split pins FAIL against the staged predecessor.

Loads `_delme/predispose_dispatch_f39_lanes_20260831T1812Z/cosmos_dispatch.py`
as source so the new pins are measured against the unsplit module. Writes
`cosmos/_fail_f39_lanes_against_old.json`. all_new_pins_failed is the bite.

Does not import the old module as cosmos_dispatch (would shadow live).
"""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OLD_DIR = REPO / "_delme" / "predispose_dispatch_f39_lanes_20260831T1812Z"
OLD = OLD_DIR / "cosmos_dispatch.py"
OUT = REPO / "cosmos" / "_fail_f39_lanes_against_old.json"


def main() -> int:
    if not OLD.is_file():
        rec = {"ok": False, "kind": "NO_PREDECESSOR", "old": str(OLD)}
        OUT.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
        print(json.dumps(rec, indent=1))
        return 2
    old_src = OLD.read_text(encoding="utf-8")
    live_mod = REPO / "cosmos" / "cosmos_dispatch_lanes.py"
    pins = {
        "lanes_module_imported": "cosmos_dispatch_lanes" in old_src,
        "lane_dir_moved_out": "def _lane_dir" not in old_src,
        "measure_lanes_moved_out": "def measure_lanes" not in old_src,
        "pick_least_loaded_moved_out": "def pick_least_loaded" not in old_src,
        "job_filename_moved_out": "def job_filename" not in old_src,
        "locate_job_moved_out": "def locate_job" not in old_src,
        "returns_dir_moved_out": "def returns_dir" not in old_src,
        "banner_is_reexport_only": (
            "live in cosmos_dispatch_lanes" in old_src
            and "from cosmos_dispatch_lanes import" in old_src
            and "def measure_lanes" not in old_src
        ),
        "lanes_file_was_present": (
            OLD_DIR / "cosmos_dispatch_lanes.py").is_file(),
    }
    rec = {
        "schema": "cosmos-f39-lanes-fail-old/1",
        "old_dispatch": str(OLD),
        "old_bytes": OLD.stat().st_size,
        "old_lines": old_src.count("\n") + 1,
        "old_has_lanes_banner": "# BTS compatibility lane accounting" in old_src,
        "old_defines_measure": "def measure_lanes" in old_src,
        "live_lanes_exists": live_mod.is_file(),
        "live_lanes_bytes": live_mod.stat().st_size if live_mod.is_file() else 0,
        "pins": pins,
        "failed_pin_count": sum(1 for v in pins.values() if v is False),
        "all_new_pins_failed": all(v is False for v in pins.values()),
    }
    OUT.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(rec, indent=1))
    return 0 if rec["all_new_pins_failed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
