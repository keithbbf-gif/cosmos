#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prove the F-29 compose pins FAIL against the staged predecessor kernel.

Loads `_delme/predispose_cosmos_kernel_f29_20260831T130051Z/cosmos_kernel.py`
by path so live cosmos_* siblings still resolve. Writes
`cosmos/_fail_f29_against_old.json`. all_new_pins_failed is the bite.
"""
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OLD = REPO / "_delme" / "predispose_cosmos_kernel_f29_20260831T130051Z" / "cosmos_kernel.py"
OUT = REPO / "cosmos" / "_fail_f29_against_old.json"


def load_old():
    sys.path.insert(0, str(REPO / "cosmos"))
    sys.path.insert(0, str(REPO))
    spec = importlib.util.spec_from_file_location("cosmos_kernel_f29_old", OLD)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    old = load_old()
    td = Path(tempfile.mkdtemp(prefix="cosmos_f29_old_"))
    root = old.install(td / "live", tree_id="f29-old")
    k = old.Kernel(root, worker="f29-old")
    composed = list((k.rails_compose or {}).get("composed") or [])
    pins = {
        "tools_surface_in_composed": "tools-surface" in composed,
        "kernel_tools_bound": getattr(k, "tools", None) is not None,
        "tools_compose_invoked_false": (
            getattr(k, "tools_compose", None) or {}
        ).get("invoked") is False,
        "inventory_xai_openai": False,
    }
    tools = getattr(k, "tools", None)
    if tools is not None:
        pins["inventory_xai_openai"] = (
            {r["name"] for r in tools.inventory()} == {"xai-docs", "openai-docs"}
        )
    rec = {
        "schema": "cosmos-f29-fail-old/1",
        "old_kernel": str(OLD),
        "old_bytes": OLD.stat().st_size,
        "ready": bool(k.ready),
        "composed": composed,
        "pins": pins,
        "all_new_pins_failed": all(v is False for v in pins.values()),
    }
    OUT.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(rec, indent=1))
    return 0 if rec["all_new_pins_failed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
