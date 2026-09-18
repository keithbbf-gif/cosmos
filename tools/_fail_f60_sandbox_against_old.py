#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prove the F-60 env-inherited schtasks-sandbox pins FAIL against the predecessor.

Loads `_delme/predispose_f60_sandbox_20260831T183526Z/` so the new pins
are measured against the clock that still spawned schtasks.exe from a
Python --once child (the health suite leftover). Writes
`cosmos/_fail_f60_sandbox_against_old.json`. all_new_pins_failed is the bite.

Does not invoke schtasks.exe. Source pins + a subprocess spy on the old
run_schtasks (OSError, never the native binary).
"""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OLD_DIR = REPO / "_delme" / "predispose_f60_sandbox_20260831T183526Z"
OLD_CLOCK = OLD_DIR / "cosmos_clock.py"
OLD_GUARD = OLD_DIR / "cosmos_test_guard.py"
OLD_FENCE = OLD_DIR / "test_live_write_fence.py"
OUT = REPO / "cosmos" / "_fail_f60_sandbox_against_old.json"


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    if not OLD_CLOCK.is_file() or not OLD_GUARD.is_file() or not OLD_FENCE.is_file():
        rec = {"ok": False, "kind": "NO_PREDECESSOR", "old": str(OLD_DIR)}
        OUT.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
        print(json.dumps(rec, indent=1))
        return 2
    old_c = OLD_CLOCK.read_text(encoding="utf-8")
    old_g = OLD_GUARD.read_text(encoding="utf-8")
    old_f = OLD_FENCE.read_text(encoding="utf-8")

    # Runtime: old run_schtasks with the sandbox env still calls subprocess.
    old_mod = _load(OLD_CLOCK, "old_cosmos_clock_f60_sandbox")
    calls = []
    real = subprocess.run

    def spy(*a, **kw):
        calls.append({"argv": a[0] if a else None})
        raise OSError("f60-sandbox-bite: do not invoke schtasks.exe")

    prev = os.environ.get("COSMOS_SCHTASKS_SANDBOX")
    os.environ["COSMOS_SCHTASKS_SANDBOX"] = "1"
    subprocess.run = spy
    rec_query = None
    err = None
    try:
        rec_query = old_mod.run_schtasks(
            ["schtasks", "/query", "/tn", "COSMOS Health Watchdog"])
    except OSError as e:
        err = f"{type(e).__name__}: {e}"
    finally:
        subprocess.run = real
        if prev is None:
            os.environ.pop("COSMOS_SCHTASKS_SANDBOX", None)
        else:
            os.environ["COSMOS_SCHTASKS_SANDBOX"] = prev

    pins = {
        "clock_names_sandbox_env": "COSMOS_SCHTASKS_SANDBOX" in old_c,
        "clock_has_schtasks_sandbox_on": "schtasks_sandbox_on" in old_c,
        "guard_sets_sandbox_env": 'COSMOS_SCHTASKS_SANDBOX' in old_g,
        "fence_sets_sandbox_env": 'COSMOS_SCHTASKS_SANDBOX' in old_f,
        "fence_pins_health_unfenced_empty":
            "no native unfenced spawns (F-60)" in old_f,
        "old_query_under_env_did_not_spawn": len(calls) == 0,
    }
    rec = {
        "schema": "cosmos-f60-sandbox-fail-old/1",
        "old_dir": str(OLD_DIR),
        "old_clock_bytes": OLD_CLOCK.stat().st_size,
        "old_guard_bytes": OLD_GUARD.stat().st_size,
        "old_fence_bytes": OLD_FENCE.stat().st_size,
        "pins": pins,
        "old_query_calls": len(calls),
        "old_query_err": err,
        "old_query_ok": None if rec_query is None else rec_query.get("ok"),
        "old_query_sandbox": None if rec_query is None else rec_query.get("sandbox"),
        "all_new_pins_failed": all(v is False for v in pins.values()),
        "failed_pin_count": sum(1 for v in pins.values() if v is False),
    }
    OUT.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(rec, indent=1))
    return 0 if rec["all_new_pins_failed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
