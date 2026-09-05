#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""New F-54 clock pins MUST FAIL against the staged predecessor.

    py -3.14 builds/backup/_fail_f54_plan_task_against_old.py
"""
from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
OLD = (HERE / "_delme" / "predispose_state_offsite_f54_20260831T154055Z"
       / "cosmos_state_offsite.py")
OUT = HERE / "_fail_f54_plan_task_against_old.json"
KEEP = {
    "test_plan_task_argv_is_daily_windowless_and_points_at_this_file",
    "test_plan_task_registers_nothing",
    "test_stale_threshold_matches_a_daily_cadence",
    "test_payload_is_the_whitelist_not_a_scope_tree",
    "test_cli_plan_task_in_a_fresh_interpreter",
}


def main() -> int:
    if not OLD.is_file():
        raise SystemExit(f"missing predecessor {OLD}")
    sys.path.insert(0, str(HERE))
    spec = importlib.util.spec_from_file_location("cosmos_state_offsite", OLD)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["cosmos_state_offsite"] = mod
    spec.loader.exec_module(mod)

    test_path = HERE / "test_state_offsite.py"
    tspec = importlib.util.spec_from_file_location(
        "test_state_offsite_f54_against_old", test_path)
    tmod = importlib.util.module_from_spec(tspec)
    tspec.loader.exec_module(tmod)

    loader = unittest.defaultTestLoader
    kept = unittest.TestSuite()
    ran_names = []
    for case in (tmod.TestScheduling, tmod.TestCliFreshInterpreter):
        for test in loader.loadTestsFromTestCase(case):
            name = test.id().rsplit(".", 1)[-1]
            if name not in KEEP:
                continue
            kept.addTest(test)
            ran_names.append(name)

    result = unittest.TextTestRunner(verbosity=2, stream=sys.stdout).run(kept)
    failed_names = sorted(
        [t.id().rsplit(".", 1)[-1] for t, _ in result.failures]
        + [t.id().rsplit(".", 1)[-1] for t, _ in result.errors]
    )
    rec = {
        "schema": "cosmos-bite/1",
        "what": "new F-54 --plan-task pins FAIL against predecessor (no clock vehicle)",
        "predecessor": str(OLD),
        "tests_run": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "failed_names": failed_names,
        "ran_names": sorted(ran_names),
        "all_new_pins_failed": (
            result.testsRun == len(ran_names)
            and (len(result.failures) + len(result.errors)) == result.testsRun
            and result.testsRun > 0
        ),
    }
    OUT.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(rec, indent=2))
    return 0 if rec["all_new_pins_failed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
