#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prove the F-69 H6 proven-label pins FAIL against the staged predecessor.

Loads `_delme/predispose_f69_h6_20260831T184200Z/` so the new pins
are measured against KIND_LIVE claude=UNPROVEN (the leftover before
the harness PONG). Writes cosmos/_fail_f69_h6_against_old.json.
all_new_pins_failed is the bite.
"""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OLD_DIR = REPO / "_delme" / "predispose_f69_h6_20260831T184200Z"
OLD_DISP = OLD_DIR / "cosmos_dispatch.py"
OLD_JOBS = OLD_DIR / "cosmos_dispatch_jobs.py"
OLD_TEST = OLD_DIR / "test_dispatch.py"
OLD_JOBS_TEST = OLD_DIR / "test_dispatch_jobs.py"
OUT = REPO / "cosmos" / "_fail_f69_h6_against_old.json"


def main() -> int:
    if not OLD_DISP.is_file() or not OLD_JOBS.is_file() or not OLD_TEST.is_file():
        rec = {"ok": False, "kind": "NO_PREDECESSOR", "old": str(OLD_DIR)}
        OUT.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
        print(json.dumps(rec, indent=1))
        return 2
    old_d = OLD_DISP.read_text(encoding="utf-8")
    old_j = OLD_JOBS.read_text(encoding="utf-8")
    old_t = OLD_TEST.read_text(encoding="utf-8")
    old_jt = OLD_JOBS_TEST.read_text(encoding="utf-8") if OLD_JOBS_TEST.is_file() else ""
    pins = {
        "dispatch_claude_kind_live_proven":
            '"claude": "proven"' in old_d,
        "dispatch_sonnet_kind_live_proven":
            '"sonnet": "proven"' in old_d,
        "jobs_claude_bakes_proven":
            '"kind_live": "proven"' in old_j
            and "_claude_job" in old_j,
        "test_pins_claude_proven":
            "claude/F5 kind_live is proven" in old_t,
        "test_h6_ok_requires_claude_proven":
            'h6["claude_kind_live"] == "proven"' in old_t,
        "jobs_suite_pins_claude_proven":
            "claude kind_live in job source is proven" in old_jt,
    }
    rec = {
        "schema": "cosmos-f69-h6-fail-old/1",
        "old_dir": str(OLD_DIR),
        "old_dispatch_bytes": OLD_DISP.stat().st_size,
        "old_jobs_bytes": OLD_JOBS.stat().st_size,
        "old_test_bytes": OLD_TEST.stat().st_size,
        "pins": pins,
        "all_new_pins_failed": all(v is False for v in pins.values()),
        "failed_pin_count": sum(1 for v in pins.values() if v is False),
        "live_prove": "cosmos/_f69_h6_live.json",
    }
    OUT.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(rec, indent=1))
    return 0 if rec["all_new_pins_failed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
