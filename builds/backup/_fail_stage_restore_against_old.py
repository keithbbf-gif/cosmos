#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Run TestRestoreFailClosed against the stripped predecessor.

The new pins MUST FAIL here. A green run against this module means the
tests are not actually asking the claim. Output:
`builds/backup/_fail_stage_restore_against_old.json`.

    py -3.14 builds/backup/_fail_stage_restore_against_old.py
"""
from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
OLD = (HERE / "_delme" / "predispose_stage_restore_20260831T123422Z"
       / "cosmos_backup.py")
OUT = HERE / "_fail_stage_restore_against_old.json"
# The bite-artifact check is about the recorded pre-fix JSON, not the
# predecessor module, so it is expected to PASS even against old.
SKIP = {"test_bite_artifact_records_pre_fix"}


def main() -> int:
    if not OLD.is_file():
        raise SystemExit(f"missing predecessor {OLD}")
    spec = importlib.util.spec_from_file_location("cosmos_backup", OLD)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["cosmos_backup"] = mod
    spec.loader.exec_module(mod)

    test_path = HERE / "test_cosmos_backup.py"
    tspec = importlib.util.spec_from_file_location("test_cosmos_backup_against_old",
                                                   test_path)
    tmod = importlib.util.module_from_spec(tspec)
    tspec.loader.exec_module(tmod)

    loader = unittest.defaultTestLoader
    suite = loader.loadTestsFromTestCase(tmod.TestRestoreFailClosed)
    kept = unittest.TestSuite()
    ran_names = []
    for test in suite:
        name = test.id().rsplit(".", 1)[-1]
        if name in SKIP:
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
        "what": "new TestRestoreFailClosed pins FAIL against stripped predecessor",
        "predecessor": str(OLD),
        "tests_run": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "unexpected_successes": len(getattr(result, "unexpectedSuccesses", [])),
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
    sys.exit(main())
