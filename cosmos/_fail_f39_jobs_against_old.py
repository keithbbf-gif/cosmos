#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prove the F-39 dispatch-job-source-split pins FAIL against the staged predecessor.

Loads `_delme/predispose_dispatch_f39_jobs_20260831T1750Z/cosmos_dispatch.py`
as source so the new pins are measured against the unsplit module. Writes
`cosmos/_fail_f39_jobs_against_old.json`. all_new_pins_failed is the bite.

Does not import the old module as cosmos_dispatch (would shadow live).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OLD_DIR = REPO / "_delme" / "predispose_dispatch_f39_jobs_20260831T1750Z"
OLD = OLD_DIR / "cosmos_dispatch.py"
OUT = REPO / "cosmos" / "_fail_f39_jobs_against_old.json"


def main() -> int:
    if not OLD.is_file():
        rec = {"ok": False, "kind": "NO_PREDECESSOR", "old": str(OLD)}
        OUT.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
        print(json.dumps(rec, indent=1))
        return 2
    old_src = OLD.read_text(encoding="utf-8")
    live_jobs = REPO / "cosmos" / "cosmos_dispatch_jobs.py"
    pins = {
        "jobs_module_imported": "cosmos_dispatch_jobs" in old_src,
        "grok_moved_out": "def _grok_job" not in old_src,
        "cursor_moved_out": "def _cursor_job" not in old_src,
        "claude_moved_out": "def _claude_job" not in old_src,
        "codex_moved_out": "def _codex_job" not in old_src,
        "render_moved_out": "def render_job" not in old_src,
        "banner_is_reexport_only": (
            "builders live in cosmos_dispatch_jobs" in old_src
            and "from cosmos_dispatch_jobs import" in old_src
            and "def _grok_job" not in old_src
        ),
        "jobs_file_was_present": (OLD_DIR / "cosmos_dispatch_jobs.py").is_file(),
    }
    rec = {
        "schema": "cosmos-f39-jobs-fail-old/1",
        "old_dispatch": str(OLD),
        "old_bytes": OLD.stat().st_size,
        "old_lines": old_src.count("\n") + 1,
        "old_has_jobs_banner": "# job source (R4" in old_src,
        "old_defines_grok": "def _grok_job" in old_src,
        "live_jobs_exists": live_jobs.is_file(),
        "live_jobs_bytes": live_jobs.stat().st_size if live_jobs.is_file() else 0,
        "pins": pins,
        "failed_pin_count": sum(1 for v in pins.values() if v is False),
        "all_new_pins_failed": all(v is False for v in pins.values()),
    }
    OUT.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(rec, indent=1))
    return 0 if rec["all_new_pins_failed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
