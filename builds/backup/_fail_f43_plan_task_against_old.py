#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prove the new F-43 clock pins FAIL against the predecessor daemon.

Predecessor is builds/backup/cosmos_backup.py (schtasks in the docstring,
no plan_task_argv, no TASK_NAME assignment, --plan-task is not a verb).

    py -3.14 builds/backup/_fail_f43_plan_task_against_old.py
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DAEMON = HERE / "cosmos_backup.py"
OUT = HERE / "_fail_f43_plan_task_against_old.json"

NEW_PINS = (
    "has_plan_task_argv",
    "has_TASK_NAME_assignment",
    "cli_plan_task_is_a_verb",
    "cli_registers_false",
    "task_name_is_bulletproof_backup",
)


def main() -> int:
    text = DAEMON.read_text(encoding="utf-8")
    p = subprocess.run(
        [sys.executable, str(DAEMON), "--root", str(HERE), "--plan-task"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=30)
    err = (p.stderr or "") + (p.stdout or "")
    pins = {
        "has_plan_task_argv": "def plan_task_argv" in text,
        "has_TASK_NAME_assignment":
            'TASK_NAME = "COSMOS Bulletproof Backup"' in text,
        "cli_plan_task_is_a_verb": p.returncode == 0,
        "cli_registers_false": '"registers": false' in err.lower()
        or '"registers": False' in err,
        "task_name_is_bulletproof_backup": False,
    }
    try:
        body = json.loads(p.stdout or "{}")
        pins["task_name_is_bulletproof_backup"] = (
            body.get("task") == "COSMOS Bulletproof Backup")
    except ValueError:
        pins["task_name_is_bulletproof_backup"] = False
    rec = {
        "what": "new F-43 --plan-task pins FAIL against predecessor (no clock vehicle)",
        "predecessor": str(DAEMON),
        "cli_rc": p.returncode,
        "cli_stderr_tail": err[-400:],
        "pins": pins,
        "failed_pins": [k for k in NEW_PINS if pins[k] is False],
        "passed_pins": [k for k in NEW_PINS if pins[k] is True],
    }
    rec["all_new_pins_failed"] = all(pins[k] is False for k in NEW_PINS)
    OUT.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({
        "all_new_pins_failed": rec["all_new_pins_failed"],
        "failed": rec["failed_pins"],
        "passed": rec["passed_pins"],
        "cli_rc": rec["cli_rc"],
    }, indent=2))
    return 0 if rec["all_new_pins_failed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
