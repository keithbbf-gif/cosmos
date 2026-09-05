#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""New lock-scope pins MUST FAIL against the staged predecessor.

The predecessor:

  * iter_files matched excludes as exact basenames only (`.git`, `__pycache__`)
  * cosmos_local_clock.tick() passed DEFAULT_EXCLUDES into run_once

so:

  * an exclusive-locked `live/logs/cdeck_feed.lock` was SOURCE_UNREADABLE
    (the 16:50Z live refusal) instead of VERIFIED
  * with BOTH a lock and an unreadable in-scope data file, the refusal
    named the lock (walked first) instead of `zzz/data.txt`

New pins (TestLiveLockScope):
  test_lock_file_does_not_block_verified
  test_unreadable_in_scope_data_still_refuses

    py -3.14 builds/backup/_fail_local_excludes_against_old.py
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
OLD = HERE / "_delme" / "predispose_local_excludes_20260831T171335Z"
OUT = HERE / "_fail_local_excludes_against_old.json"
KEEP = {
    "test_lock_file_does_not_block_verified",
    "test_unreadable_in_scope_data_still_refuses",
}


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    old_cb = OLD / "cosmos_backup.py"
    old_lc = OLD / "cosmos_local_clock.py"
    if not old_cb.is_file() or not old_lc.is_file():
        raise SystemExit(f"missing predecessor {OLD}")

    sys.path.insert(0, str(HERE))
    # Current mounts / offsite (unchanged contract) so old local_clock can import.
    import cosmos_backup_mounts  # noqa: F401
    import cosmos_offsite_clock  # noqa: F401

    _load("cosmos_backup", old_cb)
    _load("cosmos_local_clock", old_lc)

    test_path = HERE / "test_local_clock.py"
    tspec = importlib.util.spec_from_file_location(
        "test_local_clock_excludes_against_old", test_path)
    tmod = importlib.util.module_from_spec(tspec)
    tspec.loader.exec_module(tmod)

    loader = unittest.defaultTestLoader
    kept = unittest.TestSuite()
    ran_names = []
    suite = loader.loadTestsFromTestCase(tmod.TestLiveLockScope)
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
        "what": ("new TestLiveLockScope pins FAIL against predecessor "
                 "(basename-only excludes; tick hard-coded DEFAULT_EXCLUDES)"),
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
