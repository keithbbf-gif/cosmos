#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bite: F-43 P0 daemon has no schtasks vehicle (required before belief).

builds/backup/cosmos_backup.py has `run --once` but nothing emits a
schtasks /create line. cosmos_local_clock.py does not exist. F-47/F-48/F-54
clocks push adapters/payloads; none schedule the HMAC local daemon.

    py -3.14 builds/backup/_bite_f43_plan_task.py
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "_bite_f43_plan_task.json"
CLOCK = HERE / "cosmos_local_clock.py"
DAEMON = HERE / "cosmos_backup.py"


def main() -> int:
    daemon_text = DAEMON.read_text(encoding="utf-8") if DAEMON.is_file() else ""
    rec = {
        "clock_path": str(CLOCK),
        "clock_exists": CLOCK.is_file(),
        "daemon_exists": DAEMON.is_file(),
        "daemon_has_plan_task_argv": "def plan_task_argv" in daemon_text,
        "daemon_has_TASK_NAME": 'TASK_NAME = "COSMOS Bulletproof Backup"' in daemon_text,
        "daemon_mentions_schtasks": "schtasks" in daemon_text.lower(),
        "import_state": None,
        "import_error": None,
    }
    spec = importlib.util.spec_from_file_location(
        "cosmos_local_clock_bite", CLOCK) if CLOCK.is_file() else None
    if spec is None or spec.loader is None:
        rec["import_state"] = "ABSENT"
        rec["import_error"] = "ModuleNotFoundError"
    else:
        rec["import_state"] = "PRESENT"
    rec["all_bite"] = (
        rec["clock_exists"] is False
        and rec["import_state"] == "ABSENT"
        and rec["import_error"] == "ModuleNotFoundError"
        and rec["daemon_has_plan_task_argv"] is False
        and rec["daemon_has_TASK_NAME"] is False
        and rec["daemon_mentions_schtasks"] is True
        and rec["daemon_exists"] is True
    )
    OUT.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({
        "all_bite": rec["all_bite"],
        "clock_exists": rec["clock_exists"],
        "import_state": rec["import_state"],
        "daemon_has_plan_task_argv": rec["daemon_has_plan_task_argv"],
        "daemon_mentions_schtasks": rec["daemon_mentions_schtasks"],
    }, indent=2))
    return 0 if rec["all_bite"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
