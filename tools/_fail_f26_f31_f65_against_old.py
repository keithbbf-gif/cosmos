#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prove F-26/F-31/F-65 pins FAIL against the staged predecessor.

Loads `_delme/predispose_f26_f31_f65_20260831T140415Z/` by path.
all_new_pins_failed is the bite. Does not import the live newai scout.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OLD = REPO / "_delme" / "predispose_f26_f31_f65_20260831T140415Z"
OUT = REPO / "cosmos" / "_fail_f26_f31_f65_against_old.json"


def load(name: str, filename: str):
    sys.path.insert(0, str(REPO / "cosmos"))
    spec = importlib.util.spec_from_file_location(name, OLD / filename)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    clocks = load("own_clocks_old", "cosmos_own_clocks.py")
    crit = load("crit_old", "cosmos_crit_consumer.py")
    bucket = load("bucket_old", "cosmos_bucket_daemon.py")
    ids = [c.get("id") for c in clocks.CLOCKS]
    pins = {
        "clock_20_critconsumer": any(
            c.get("id") == 20 and c.get("task") == "COSMOS CritConsumer"
            for c in clocks.CLOCKS),
        "clock_21_grok_bucket": any(
            c.get("id") == 21 and "Grok Bucket" in str(c.get("task"))
            for c in clocks.CLOCKS),
        "clock_22_gem_bucket": any(
            c.get("id") == 22 and "GEM Bucket" in str(c.get("task"))
            for c in clocks.CLOCKS),
        "clock_23_newai_scout": any(
            c.get("id") == 23 and c.get("script") == "cosmos_newai_scout.py"
            for c in clocks.CLOCKS),
        "crit_clock_id_20": getattr(crit, "CLOCK_ID", None) == 20,
        "crit_has_plan_task_argv": hasattr(crit, "plan_task_argv"),
        "bucket_has_plan_task_argv": hasattr(bucket, "plan_task_argv"),
        "bucket_clock_ids": getattr(bucket, "CLOCK_IDS", None) == {
            "grok": 21, "gem": 22},
        "newai_scout_in_staged": (OLD / "cosmos_newai_scout.py").is_file(),
    }
    rec = {
        "schema": "cosmos-f26-f31-f65-fail-old/1",
        "old_dir": str(OLD),
        "old_clock_count": len(clocks.CLOCKS),
        "old_max_id": max(ids) if ids else None,
        "old_ids": ids,
        "pins": pins,
        "all_new_pins_failed": all(v is False for v in pins.values()),
    }
    OUT.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(rec, indent=1))
    return 0 if rec["all_new_pins_failed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
