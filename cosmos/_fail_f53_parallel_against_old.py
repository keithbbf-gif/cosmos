#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prove the F-53 PARALLEL-drives-MOTIF pins FAIL against the staged predecessor.

The leftover: PARALLEL was mailbox-ping + drop 0 while COW was fresh —
a failover satellite, not a second orchestrator. New pins require a
MOTIF work-order drop on an empty bucket, a flood guard, and spawn
only when a drop happened.

A pin that PASSES on the old module is not a pin.

  py -3.14 cosmos/_fail_f53_parallel_against_old.py
"""
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
OLD_DIR = REPO / "_delme" / "predispose_f53_parallel_20260831T161219Z"
OLD = OLD_DIR / "cosmos_prepaid_orch.py"
OUT = HERE / "_fail_f53_parallel_against_old.json"

sys.path.insert(0, str(HERE))


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    from cosmos_kernel import install

    if not OLD.is_file():
        rec = {"ok": False, "kind": "NO_PREDECESSOR", "old": str(OLD)}
        OUT.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
        print(json.dumps(rec, indent=1))
        return 2

    old = _load(OLD, "cosmos_prepaid_orch_old_f53")
    td = Path(tempfile.mkdtemp(prefix="cosmos_fail_f53par_"))
    root = install(td / "live", tree_id="fail-f53-parallel")
    control = root / "state" / "control"
    control.mkdir(parents=True, exist_ok=True)
    (control / "COW_HEARTBEAT.json").write_text(json.dumps({
        "last_run_epoch": time.time() - 5,
        "worker": "cow",
        "pid": 1,
    }), encoding="utf-8")

    pins = []

    def pin(name, fn):
        try:
            ok = bool(fn())
            err = ""
        except Exception as e:  # noqa: BLE001
            ok = False
            err = "%s: %s" % (type(e).__name__, e)
        pins.append({"name": name, "passed_on_old": ok, "err": err})

    spawned = []

    def _which_grok(name):
        return r"C:\fake\grok.exe" if name == "grok" else None

    rec = old.poll_once(str(root), which=_which_grok, spawn=spawned.append)
    orders = list((root / "state" / "work_orders" / "bucket").glob("*.json"))
    src = OLD.read_text(encoding="utf-8")

    pin("PARALLEL empty-bucket drops one MOTIF work-order",
        lambda: rec.get("state") == "PARALLEL" and rec.get("dropped") == 1)
    pin("PARALLEL empty-bucket writes a DROPPED order file",
        lambda: rec.get("state") == "PARALLEL" and len(orders) == 1)
    pin("PARALLEL spawn-injected fires once when it drops",
        lambda: rec.get("dropped") == 1 and len(spawned) == 1
        and spawned[0][0] == "grok")
    pin("open_prepaid_orders is a callable flood guard",
        lambda: callable(getattr(old, "open_prepaid_orders", None)))
    pin("PARALLEL readme is not mailbox-only failover",
        lambda: "mailbox only" not in str(rec.get("_readme") or "").lower())
    pin("source names the flood guard",
        lambda: "def open_prepaid_orders" in src)

    failed = [p for p in pins if not p["passed_on_old"]]
    out = {
        "schema": "cosmos-f53-fail-old/1",
        "old": str(OLD),
        "old_bytes": OLD.stat().st_size,
        "old_state": rec.get("state"),
        "old_dropped": rec.get("dropped"),
        "old_spawned": rec.get("spawned"),
        "old_order_count": len(orders),
        "old_readme": rec.get("_readme"),
        "pins": pins,
        "pin_count": len(pins),
        "failed_on_old": len(failed),
        "all_new_pins_failed": len(failed) == len(pins) and len(pins) > 0,
    }
    OUT.write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=1))
    return 0 if out["all_new_pins_failed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
