#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""New HEALTH_BOARD.node pin MUST FAIL against the staged predecessor.

Run: py -3.14 cosmos/_fail_follow_health_against_old.py
"""
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "cosmos"))
from cosmos_kernel import Kernel, install  # noqa: E402

PRE = REPO / "_delme" / "predispose_follow_health_20260831T132220Z" / "cosmos"
OUT = REPO / "cosmos" / "_fail_follow_health_against_old.json"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load " + str(path))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    if not (PRE / "cosmos_health.py").is_file():
        print("REFUSING: staged predecessor missing at %s" % PRE)
        return 2
    old = _load("old_cosmos_health_fail", PRE / "cosmos_health.py")
    td = Path(tempfile.mkdtemp(prefix="cosmos_fail_health_"))
    k = Kernel(install(td / "live", tree_id="fail-health"), worker="core")
    old.HealthBoard(k).run()
    p = next(r for r in k.ledger.verify()
             if r["event"] == "HEALTH_BOARD")["payload"]
    # The NEW pin: node must equal sentinel.system. Old writer lacks it.
    pin_ok = p.get("node") == k.paths.sentinel.system
    evidence = {
        "ok": (not pin_ok),  # required: the new pin FAILS on old code
        "all_new_pins_failed": (not pin_ok),
        "pin": "HEALTH_BOARD.node == sentinel.system",
        "old_payload": p,
        "sentinel_system": k.paths.sentinel.system,
        "old_node": p.get("node"),
        "pin_passed_on_old": pin_ok,
        "prechange_path": str(PRE),
    }
    OUT.write_text(json.dumps(evidence, indent=1), encoding="utf-8")
    print("pin_passed_on_old=%s (want False)" % pin_ok)
    print("old_payload=%s" % p)
    print("EVIDENCE %s" % OUT)
    return 0 if evidence["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
