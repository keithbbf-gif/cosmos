#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prove the F-60 schtasks-writer pins FAIL against the staged predecessor.

Loads `_delme/predispose_f60_schtasks_20260831T164154Z/` so the new pins
are measured against the unguarded test fence. Writes
`cosmos/_fail_f60_schtasks_against_old.json`. all_new_pins_failed is the bite.

Does not invoke schtasks.exe. Source pins only.
"""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OLD_DIR = REPO / "_delme" / "predispose_f60_schtasks_20260831T164154Z"
OLD_GUARD = OLD_DIR / "cosmos_test_guard.py"
OLD_FENCE = OLD_DIR / "test_live_write_fence.py"
OUT = REPO / "cosmos" / "_fail_f60_schtasks_against_old.json"


def main() -> int:
    if not OLD_GUARD.is_file() or not OLD_FENCE.is_file():
        rec = {"ok": False, "kind": "NO_PREDECESSOR", "old": str(OLD_DIR)}
        OUT.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
        print(json.dumps(rec, indent=1))
        return 2
    old_g = OLD_GUARD.read_text(encoding="utf-8")
    old_f = OLD_FENCE.read_text(encoding="utf-8")
    pins = {
        "guard_wraps_run_schtasks": "guarded_run_schtasks" in old_g,
        "guard_wraps_harden_task": "guarded_harden_task" in old_g,
        "guard_detects_schtasks_writes": "_schtasks_writes" in old_g,
        "fence_includes_backup_clock": "tests/test_backup_clock.py" in old_f,
    }
    rec = {
        "schema": "cosmos-f60-schtasks-fail-old/1",
        "old_dir": str(OLD_DIR),
        "old_guard_bytes": OLD_GUARD.stat().st_size,
        "old_fence_bytes": OLD_FENCE.stat().st_size,
        "pins": pins,
        "all_new_pins_failed": all(v is False for v in pins.values()),
        "failed_pin_count": sum(1 for v in pins.values() if v is False),
    }
    OUT.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(rec, indent=1))
    return 0 if rec["all_new_pins_failed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
