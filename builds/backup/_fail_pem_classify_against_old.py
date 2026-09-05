#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""New PEM-classification pins MUST FAIL against the staged predecessor.

The predecessor treated every `.pem` as key material (path suffix) and never
looked at BEGIN labels, so:

  * a public CA bundle (`vendor/certifi/cacert.pem`) was SECRETS_IN_SCOPE
  * a private-key envelope stored as `signing.key` was NOT a hit

New pins (TestPemClassification):
  test_public_ca_bundle_is_not_SECRETS_IN_SCOPE
  test_private_key_shape_is_SECRETS_IN_SCOPE

    py -3.14 builds/backup/_fail_pem_classify_against_old.py
"""
from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
OLD = HERE / "_delme" / "predispose_pem_classify_20260831T164619Z"
OUT = HERE / "_fail_pem_classify_against_old.json"
KEEP = {
    "test_public_ca_bundle_is_not_SECRETS_IN_SCOPE",
    "test_private_key_shape_is_SECRETS_IN_SCOPE",
}


def main() -> int:
    old_cb = OLD / "cosmos_backup.py"
    old_r2 = OLD / "cosmos_backup_r2.py"
    if not old_cb.is_file() or not old_r2.is_file():
        raise SystemExit(f"missing predecessor {OLD}")

    # Load the PRE-FIX scanner as cosmos_backup / cosmos_backup_r2 so the new
    # tests import the predecessor. Order matters: r2 imports cosmos_backup.
    spec_cb = importlib.util.spec_from_file_location("cosmos_backup", old_cb)
    mod_cb = importlib.util.module_from_spec(spec_cb)
    sys.modules["cosmos_backup"] = mod_cb
    spec_cb.loader.exec_module(mod_cb)

    spec_r2 = importlib.util.spec_from_file_location("cosmos_backup_r2", old_r2)
    mod_r2 = importlib.util.module_from_spec(spec_r2)
    sys.modules["cosmos_backup_r2"] = mod_r2
    spec_r2.loader.exec_module(mod_r2)

    test_path = HERE / "test_cosmos_backup.py"
    tspec = importlib.util.spec_from_file_location(
        "test_cosmos_backup_pem_against_old", test_path)
    tmod = importlib.util.module_from_spec(tspec)
    tspec.loader.exec_module(tmod)

    loader = unittest.defaultTestLoader
    kept = unittest.TestSuite()
    ran_names = []
    suite = loader.loadTestsFromTestCase(tmod.TestPemClassification)
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
        "what": ("new TestPemClassification pins FAIL against predecessor "
                 "(all .pem treated as secrets; .key content ignored)"),
        "predecessor": str(OLD),
        "tests_run": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "failed_names": failed_names,
        "ran_names": sorted(ran_names),
        "all_new_pins_failed": (
            result.testsRun == len(KEEP)
            and set(ran_names) == KEEP
            and (len(result.failures) + len(result.errors)) == result.testsRun
            and result.testsRun > 0
        ),
    }
    OUT.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(rec, indent=2))
    return 0 if rec["all_new_pins_failed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
