#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prove the F-39 collector-scanning-split pins FAIL against the staged predecessor.

Loads `_delme/predispose_collector_f39_scan_20260831T173040Z/cosmos_collector.py`
as source so the new pins are measured against the unsplit module. Writes
`cosmos/_fail_f39_scan_against_old.json`. all_new_pins_failed is the bite.

Does not import the old module as cosmos_collector (would shadow live).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OLD_DIR = REPO / "_delme" / "predispose_collector_f39_scan_20260831T173040Z"
OLD = OLD_DIR / "cosmos_collector.py"
OUT = REPO / "cosmos" / "_fail_f39_scan_against_old.json"


def main() -> int:
    if not OLD.is_file():
        rec = {"ok": False, "kind": "NO_PREDECESSOR", "old": str(OLD)}
        OUT.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
        print(json.dumps(rec, indent=1))
        return 2
    old_src = OLD.read_text(encoding="utf-8")
    live_scan = REPO / "cosmos" / "cosmos_collector_scan.py"
    pins = {
        "scan_module_imported": "cosmos_collector_scan" in old_src,
        "walk_moved_out": "def _walk_files" not in old_src,
        "queue_iter_moved_out": "def iter_queue_files" not in old_src,
        "research_iter_moved_out": "def iter_research_files" not in old_src,
        "ledger_iter_moved_out": "def iter_ledger_events" not in old_src,
        "kept_moved_out": "def ledger_event_kept" not in old_src,
        "banner_is_reexport_only": (
            "scanning -- moved to cosmos_collector_scan" in old_src
            and "from cosmos_collector_scan import" in old_src
            and "def _walk_files" not in old_src
        ),
        "scan_file_was_present": (OLD_DIR / "cosmos_collector_scan.py").is_file(),
    }
    rec = {
        "schema": "cosmos-f39-scan-fail-old/1",
        "old_collector": str(OLD),
        "old_bytes": OLD.stat().st_size,
        "old_lines": old_src.count("\n") + 1,
        "old_has_scan_banner": "# scanning" in old_src,
        "old_defines_walk": "def _walk_files" in old_src,
        "live_scan_exists": live_scan.is_file(),
        "live_scan_bytes": live_scan.stat().st_size if live_scan.is_file() else 0,
        "pins": pins,
        "failed_pin_count": sum(1 for v in pins.values() if v is False),
        "all_new_pins_failed": all(v is False for v in pins.values()),
    }
    OUT.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(rec, indent=1))
    return 0 if rec["all_new_pins_failed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
