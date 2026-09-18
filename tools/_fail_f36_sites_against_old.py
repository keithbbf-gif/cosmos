#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prove the F-36 work-order-2.3 pins FAIL against the staged predecessor.

Loads `_delme/predispose_f36_sites_20260831T160120Z/` so the new pins are
measured against the modules that still used filenames/prose as skip/stage
authority. Writes `cosmos/_fail_f36_sites_against_old.json`.
all_new_pins_failed is the bite.

Does not flip tracker authority. Does not import the old modules as live.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OLD_DIR = REPO / "_delme" / "predispose_f36_sites_20260831T160120Z"
OLD_MOTIF = OLD_DIR / "cosmos" / "cosmos_motif_driver.py"
OLD_WD2 = OLD_DIR / "cosmos" / "cosmos_watchdog2.py"
OLD_SCAN = OLD_DIR / "cosmos" / "cosmos_watchdog2_scan.py"
OLD_AUDIT = OLD_DIR / "cosmos" / "cosmos_derivation_audit.py"
OUT = REPO / "cosmos" / "_fail_f36_sites_against_old.json"


def main() -> int:
    missing = [str(p) for p in (OLD_MOTIF, OLD_WD2, OLD_SCAN, OLD_AUDIT)
               if not p.is_file()]
    if missing:
        rec = {"ok": False, "kind": "NO_PREDECESSOR", "missing": missing}
        OUT.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
        print(json.dumps(rec, indent=1))
        return 2
    motif = OLD_MOTIF.read_text(encoding="utf-8")
    wd2 = OLD_WD2.read_text(encoding="utf-8")
    scan = OLD_SCAN.read_text(encoding="utf-8")
    audit = OLD_AUDIT.read_text(encoding="utf-8")

    # Each pin is the NEW contract. The predecessor must fail ALL of them.
    pins = {
        "effective_stage_does_not_lift_from_critique_file": (
            "if critique_exists(repo" not in motif
        ),
        "drive_once_filenames_are_not_skip_authority": (
            "names = inflight_filenames" not in motif
        ),
        "wd2_filenames_are_not_skip_authority": (
            "names = inflight_filenames" not in wd2
        ),
        "name_hit_does_not_return_dhx_token": (
            'return f"dhx:{t}"' not in scan
        ),
        "audit_open_verdict_count_is_1": (
            audit.count('"verdict": "open"') == 1
        ),
        "audit_critique_site_is_advisory": (
            '"id": "critique_filename_stage"' in audit
            and '"verdict": "advisory"' in audit.split(
                '"id": "critique_filename_stage"', 1)[1][:400]
        ),
        "audit_inflight_filenames_site_is_advisory": (
            '"id": "inflight_filenames_mtime"' in audit
            and '"verdict": "advisory"' in audit.split(
                '"id": "inflight_filenames_mtime"', 1)[1][:400]
        ),
        "audit_dhx_haystack_site_is_advisory": (
            '"id": "wd2_dhx_haystack"' in audit
            and '"verdict": "advisory"' in audit.split(
                '"id": "wd2_dhx_haystack"', 1)[1][:400]
        ),
    }
    rec = {
        "schema": "cosmos-f36-fail-old/1",
        "old_dir": str(OLD_DIR),
        "old_bytes": {
            "motif": OLD_MOTIF.stat().st_size,
            "wd2": OLD_WD2.stat().st_size,
            "scan": OLD_SCAN.stat().st_size,
            "audit": OLD_AUDIT.stat().st_size,
        },
        "old_open_verdicts": audit.count('"verdict": "open"'),
        "old_has_critique_lift": "if critique_exists(repo" in motif,
        "old_names_eq_inflight_filenames_motif": "names = inflight_filenames" in motif,
        "old_names_eq_inflight_filenames_wd2": "names = inflight_filenames" in wd2,
        "old_dhx_return": 'return f"dhx:{t}"' in scan,
        "pins": pins,
        "failed_pins": [k for k, v in pins.items() if v is False],
        "all_new_pins_failed": all(v is False for v in pins.values()),
    }
    OUT.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({
        "ok": rec["all_new_pins_failed"],
        "all_new_pins_failed": rec["all_new_pins_failed"],
        "failed_pins": rec["failed_pins"],
        "old_open_verdicts": rec["old_open_verdicts"],
        "artifact": str(OUT),
    }, indent=1))
    return 0 if rec["all_new_pins_failed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
