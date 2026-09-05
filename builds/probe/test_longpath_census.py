#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_longpath_census - pin the probe's typed REFUSALS.

longpath_census.ProbeRefusal.kind lists ROOT_MISSING and SCRATCH_UNSAFE.
Neither was named by a test. A census that only walks a real dir, and a
behave() that only runs on %TEMP%, stay green if those branches are deleted
— which is how a probe writes the live tree or silently walks a hole.

Hermetic: missing-path and in-tree-scratch only. No V:\\Ai walk, no
deep-tree fixture, nothing created under the repo.

    py -3.14 builds/probe/test_longpath_census.py
"""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import longpath_census as lp                                          # noqa: E402
from longpath_census import (                                         # noqa: E402
    ProbeRefusal, behave, census_one, realscope,
)

RESULTS: list[tuple[str, bool, str]] = []
BITE = HERE / "_bite_unpinned_refusals.json"


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:                                            # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


def _raises(fn, kind: str) -> bool:
    try:
        fn()
    except ProbeRefusal as e:
        return e.kind == kind
    return False


def main() -> int:
    missing = str(Path(tempfile.gettempdir()) / "cosmos_lp_no_such_root_9f4c")
    check("census of a missing root is ROOT_MISSING, not an untyped walk",
          lambda: _raises(lambda: census_one(missing), "ROOT_MISSING"))
    scratch = Path(tempfile.mkdtemp(prefix="cosmos_lp_ex_"))
    try:
        check("census exclude_dirs string is BAD_EXCLUDES not characters (round-8)",
              lambda: _raises(lambda: census_one(str(scratch),
                                                 exclude_dirs="git"),
                              "BAD_EXCLUDES"))
        check("census exclude_dirs int is BAD_EXCLUDES not TypeError",
              lambda: _raises(lambda: census_one(str(scratch),
                                                 exclude_dirs=1),
                              "BAD_EXCLUDES"))
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    check("realscope of a missing root is ROOT_MISSING",
          lambda: _raises(lambda: realscope(missing), "ROOT_MISSING"))

    in_tree = HERE / "_would_write_scratch_inside_repo"
    check("behave() scratch inside the live tree is SCRATCH_UNSAFE",
          lambda: _raises(lambda: behave(str(in_tree)), "SCRATCH_UNSAFE"))
    check("SCRATCH_UNSAFE did not create the in-tree scratch",
          lambda: not in_tree.exists())

    old_win = lp._is_windows
    lp._is_windows = lambda: False
    try:
        check("census on a POSIX host is NOT_WINDOWS, not a silent walk",
              lambda: _raises(lambda: census_one(missing), "NOT_WINDOWS"))
        check("realscope on a POSIX host is NOT_WINDOWS",
              lambda: _raises(lambda: realscope(missing), "NOT_WINDOWS"))
        check("behave() on a POSIX host is NOT_WINDOWS before any scratch write",
              lambda: _raises(lambda: behave(str(in_tree)), "NOT_WINDOWS"))
        check("NOT_WINDOWS behave() did not create the in-tree scratch",
              lambda: not in_tree.exists())
    finally:
        lp._is_windows = old_win

    tdi = Path(tempfile.mkdtemp(prefix="cosmos_imp_"))
    try:
        src = tdi / "src"
        src.mkdir()
        (src / "a.txt").write_text("x", encoding="utf-8")
        rec_imp = lp._probe_running_backup(
            {"scratch": str(src), "files": {}},
            tdi / "scratch", tdi / "no_such_module.py", "missing")
        check("missing walker module is IMPORT_FAILED, not a guessed walk",
              lambda: rec_imp.get("kind") == "IMPORT_FAILED"
              and rec_imp.get("state") == "UNMEASURED")
    finally:
        shutil.rmtree(tdi, ignore_errors=True)

    if BITE.is_file():
        rec = json.loads(BITE.read_text(encoding="utf-8"))
        check("bite records ROOT_MISSING old crash as FileNotFoundError/untyped",
              lambda: rec.get("root_missing_old_kind") in (
                  "FileNotFoundError", "NotADirectoryError", None, "untyped"))
        check("bite records SCRATCH_UNSAFE old as would-write",
              lambda: rec.get("scratch_unsafe_old_would_write") is True)

    bad = [r for r in RESULTS if not r[1]]
    for label, ok, err in RESULTS:
        print(f"  {'OK  ' if ok else 'FAIL'}  {label}{('  ' + err) if err else ''}")
    print("live_value: " + json.dumps(
        {"checks": len(RESULTS), "passed": len(RESULTS) - len(bad),
         "refusal_kinds": ["ROOT_MISSING", "SCRATCH_UNSAFE",
                           "NOT_WINDOWS", "IMPORT_FAILED"]},
        sort_keys=True))
    print(f"result: {'ok' if not bad else 'FAIL'}  "
          f"{len(RESULTS) - len(bad)}/{len(RESULTS)}")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
