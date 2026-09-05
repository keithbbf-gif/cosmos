#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""New TestSecrets pins MUST FAIL against the staged predecessor.

    py -3.14 builds/backup/_fail_f43_secrets_against_old.py
"""
from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
OLD = (HERE / "_delme" / "predispose_cosmos_backup_f43_secrets_20260831T140505Z"
       / "cosmos_backup.py")
OUT = HERE / "_fail_f43_secrets_against_old.json"
KEEP = {
    "test_planted_install_key_bin_is_SECRETS_IN_SCOPE",
    "test_planted_api_token_txt_is_SECRETS_IN_SCOPE",
}


def main() -> int:
    if not OLD.is_file():
        raise SystemExit(f"missing predecessor {OLD}")
    spec = importlib.util.spec_from_file_location("cosmos_backup", OLD)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["cosmos_backup"] = mod
    spec.loader.exec_module(mod)

    test_path = HERE / "test_cosmos_backup.py"
    tspec = importlib.util.spec_from_file_location(
        "test_cosmos_backup_secrets_against_old", test_path)
    tmod = importlib.util.module_from_spec(tspec)
    tspec.loader.exec_module(tmod)

    loader = unittest.defaultTestLoader
    kept = unittest.TestSuite()
    ran_names = []
    suite = loader.loadTestsFromTestCase(tmod.TestSecrets)
    for test in suite:
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
        "what": "new TestSecrets pins FAIL against predecessor (sealed key material)",
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
