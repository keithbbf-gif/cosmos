#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_f24_prechange_suite_check - are tests/test_rails_prober.py and
tests/test_boot_attach.py red because of THIS change, or were they already?

Runs both suites twice: once as the tree stands, once with the staged
pre-change `cosmos_rails_prober.py` shadowing the fixed one on PYTHONPATH.
Identical failure sets mean the red predates this slice (it is the "the four"
literal the F-24 row already flags), and this change regressed nothing.

    py -3.14 cosmos\\_f24_prechange_suite_check.py --staged <path to staged .py>
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SUITES = ["tests/test_rails_prober.py", "tests/test_boot_attach.py"]


def run(env=None) -> tuple[set[str], str]:
    r = subprocess.run([sys.executable, "-m", "pytest", *SUITES, "-q"],
                       capture_output=True, text=True, env=env,
                       cwd=str(Path(__file__).resolve().parents[1]))
    fails = {ln.strip()[5:].strip() for ln in r.stdout.splitlines()
             if ln.startswith("  FAIL")}
    tail = next((ln for ln in reversed(r.stdout.splitlines())
                 if "passed" in ln or "failed" in ln), "")
    return fails, tail


def main() -> int:
    ap = argparse.ArgumentParser(prog="_f24_prechange_suite_check")
    ap.add_argument("--staged", required=True)
    a = ap.parse_args()
    staged = Path(a.staged)
    if not staged.is_file():
        print(f"staged prober not found: {staged}")
        return 2

    now, now_tail = run()
    td = Path(tempfile.mkdtemp(prefix="f24_prechange_"))
    shutil.copy2(staged, td / "cosmos_rails_prober.py")
    before, before_tail = run(dict(os.environ, PYTHONPATH=str(td)))

    print(f"AS THE TREE STANDS       : {sorted(now)}  [{now_tail}]")
    print(f"WITH PRE-CHANGE PROBER   : {sorted(before)}  [{before_tail}]")
    print(f"  staged shim: {td / 'cosmos_rails_prober.py'}")
    same = now == before
    print(f"identical failure sets   : {same}")
    print("VERDICT: " + ("pre-existing red, this change regressed nothing"
                         if same else
                         "DIFFERENT - this change moved these suites"))
    return 0 if same else 1


if __name__ == "__main__":
    raise SystemExit(main())
