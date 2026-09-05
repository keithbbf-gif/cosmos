#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prove the F-39 scanner-split pins FAIL against the staged predecessor.

Loads `_delme/predispose_watchdog2_f39_20260831T153706Z/cosmos_watchdog2.py`
as source (and the staged derivation_audit) so the new pins are measured
against the unsplit module. Writes `cosmos/_fail_f39_against_old.json`.
all_new_pins_failed is the bite.

Does not import the old module as cosmos_watchdog2 (would shadow live).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OLD_DIR = REPO / "_delme" / "predispose_watchdog2_f39_20260831T153706Z"
OLD = OLD_DIR / "cosmos_watchdog2.py"
OLD_AUDIT = OLD_DIR / "cosmos_derivation_audit.py"
OUT = REPO / "cosmos" / "_fail_f39_against_old.json"


def main() -> int:
    if not OLD.is_file():
        rec = {"ok": False, "kind": "NO_PREDECESSOR", "old": str(OLD)}
        OUT.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
        print(json.dumps(rec, indent=1))
        return 2
    old_src = OLD.read_text(encoding="utf-8")
    old_audit = (OLD_AUDIT.read_text(encoding="utf-8")
                 if OLD_AUDIT.is_file() else "")
    pins = {
        "scan_module_imported": "cosmos_watchdog2_scan" in old_src,
        "parse_md_checkboxes_moved_out": "def parse_md_checkboxes" not in old_src,
        "dhx_haystack_moved_out": "def dhx_haystack" not in old_src,
        "pick_agent_moved_out": "def pick_agent" not in old_src,
        "audit_haystack_follows_split": (
            '"file": "cosmos_watchdog2_scan.py"' in old_audit
            and "wd2_dhx_haystack" in old_audit
        ),
        "old_bytes_smaller_than_unsplit": OLD.stat().st_size < 40000,
    }
    rec = {
        "schema": "cosmos-f39-fail-old/1",
        "old_watchdog2": str(OLD),
        "old_bytes": OLD.stat().st_size,
        "old_has_scanners_banner": "# scanners" in old_src,
        "pins": pins,
        "all_new_pins_failed": all(v is False for v in pins.values()),
    }
    OUT.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(rec, indent=1))
    return 0 if rec["all_new_pins_failed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
