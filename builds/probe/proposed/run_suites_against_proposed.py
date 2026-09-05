#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""No-regression harness for the `builds/probe/proposed/` files.

A proposal COW cannot run is a proposal COW has to take on faith. This runs the
EXISTING tree suites against the proposed module instead of the live one, so
"no regression" is a measurement rather than a reading of the diff.

The binding is `sys.modules`, not `sys.path`: every suite under `tests/` does
`sys.path.insert(0, .../cosmos)` at import time, which no PYTHONPATH or path
ordering can outrank. Pre-seeding `sys.modules["cosmos_registry"]` from the
proposed file wins because `from cosmos_registry import X` consults sys.modules
first, and every downstream importer (`cosmos_kernel`, `cosmos_rails_prober`, the
five rails) then gets the same object.

Each suite runs in its OWN subprocess. They mutate sys.modules, os.environ and
cwd, and a shared interpreter would let one suite's leftovers decide the next
suite's verdict - which is the failure this harness exists to detect, not cause.

    py -3.14 builds/probe/proposed/run_suites_against_proposed.py
    py -3.14 builds/probe/proposed/run_suites_against_proposed.py --live
        (bind the LIVE cosmos_registry instead - the control run)
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent.parent
PROPOSED = REPO / "builds" / "probe" / "proposed" / "cosmos_registry.py"
LIVE = REPO / "cosmos" / "cosmos_registry.py"

# Every suite in tests/ that imports cosmos_registry, directly or through the
# Kernel. Enumerated by grep, not by memory:
#   py -3.14 -c "..." over tests/*.py for the string 'cosmos_registry'
SUITES = (
    "tests/test_registry.py",
    "tests/test_boot_attach.py",
    "tests/test_boot_rails.py",
    "tests/test_node_rails.py",
    "tests/test_stage7_fixes.py",
    "tests/test_command.py",
    "tests/test_v1.py",
    "tests/test_wave4.py",
)

CHILD = r'''
import importlib.util, runpy, sys
impl, suite, cosmos_dir = sys.argv[1], sys.argv[2], sys.argv[3]
# The proposed module still imports its SIBLINGS (cosmos_clock, cosmos_ledger)
# from the live tree - it is one file swapped into an otherwise untouched
# package, which is exactly the shape COW would apply.
sys.path.insert(0, cosmos_dir)
spec = importlib.util.spec_from_file_location("cosmos_registry", impl)
mod = importlib.util.module_from_spec(spec)
sys.modules["cosmos_registry"] = mod
spec.loader.exec_module(mod)
assert sys.modules["cosmos_registry"].__file__ == impl, "binding lost"
sys.argv = [suite]
try:
    runpy.run_path(suite, run_name="__main__")
except SystemExit as e:
    raise SystemExit(e.code if e.code is not None else 0)
'''


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", action="store_true",
                    help="bind cosmos/cosmos_registry.py (control run)")
    a = ap.parse_args(argv)
    impl = LIVE if a.live else PROPOSED

    rows, bad = [], []
    for suite in SUITES:
        p = REPO / suite
        if not p.exists():
            rows.append({"suite": suite, "rc": None, "state": "ABSENT"})
            bad.append(suite)
            continue
        r = subprocess.run([sys.executable, "-c", CHILD, str(impl), str(p),
                            str(REPO / "cosmos")],
                           cwd=str(REPO), capture_output=True, text=True)
        tail = [ln for ln in (r.stdout or "").splitlines() if "SELFTEST" in ln]
        if not tail:
            tail = (r.stderr or "").strip().splitlines()
        rows.append({"suite": suite, "rc": r.returncode,
                     "state": "PASS" if r.returncode == 0 else "FAIL",
                     "last": tail[-1] if tail else ""})
        if r.returncode != 0:
            bad.append(suite)
            print("----- %s stderr tail -----" % suite)
            print("\n".join((r.stderr or "").splitlines()[-15:]))

    print("IMPL %s" % impl)
    for row in rows:
        print("  %-5s rc=%-4s %s" % (row["state"], row["rc"], row["suite"]))
        if row.get("last"):
            print("        %s" % row["last"][:150])
    print("SUITES %d/%d PASS" % (len(rows) - len(bad), len(rows)))
    print("live_value " + json.dumps({
        "impl": str(impl), "suites": len(rows),
        "passed": len(rows) - len(bad), "failed": bad,
    }))
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
