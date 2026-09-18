#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prove the F-39 CVM-projection-split pins FAIL against the staged predecessor.

Loads `_delme/predispose_service_f39_cvm_20260831T111409Z/cosmos_service.py`
as source so the new pins are measured against the unsplit module. Writes
`cosmos/_fail_f39_cvm_against_old.json`. all_new_pins_failed is the bite.

Does not import the old module as cosmos_service (would shadow live).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OLD_DIR = REPO / "_delme" / "predispose_service_f39_cvm_20260831T111409Z"
OLD = OLD_DIR / "cosmos_service.py"
OLD_P3 = OLD_DIR / "test_cvm_p3.py"
OUT = REPO / "cosmos" / "_fail_f39_cvm_against_old.json"


def main() -> int:
    if not OLD.is_file():
        rec = {"ok": False, "kind": "NO_PREDECESSOR", "old": str(OLD)}
        OUT.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
        print(json.dumps(rec, indent=1))
        return 2
    old_src = OLD.read_text(encoding="utf-8")
    old_p3 = (OLD_P3.read_text(encoding="utf-8")
              if OLD_P3.is_file() else "")
    live_proj = REPO / "cosmos" / "cosmos_cvm_projection.py"
    pins = {
        "projection_module_imported": "cosmos_cvm_projection" in old_src,
        "cvmerror_moved_out": "class CvmError" not in old_src,
        "pull_response_moved_out": "def _cvm_pull_response" not in old_src,
        "store_snapshot_moved_out": "def _cvm_store_snapshot" not in old_src,
        "filter_kinds_moved_out": "def _cvm_filter_kinds" not in old_src,
        "p3_reads_projection_file": "cosmos_cvm_projection.py" in old_p3,
    }
    rec = {
        "schema": "cosmos-f39-cvm-fail-old/1",
        "old_service": str(OLD),
        "old_bytes": OLD.stat().st_size,
        "old_has_cvm_banner": "# ---------------- CVM projection" in old_src,
        "old_defines_cvmerror": "class CvmError" in old_src,
        "live_proj_exists": live_proj.is_file(),
        "live_proj_bytes": live_proj.stat().st_size if live_proj.is_file() else 0,
        "pins": pins,
        "all_new_pins_failed": all(v is False for v in pins.values()),
    }
    OUT.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(rec, indent=1))
    return 0 if rec["all_new_pins_failed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
