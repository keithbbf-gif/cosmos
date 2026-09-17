#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pin predecessor: file_done sealed DONE on Output+rc=0 with no Core emit.

Old predicate: non-empty Output only. pytest rc=0 and green logs were not
runtime-binding; runtime_bind did not exist on the order record.

    py -3.14 cosmos/_fail_p04_live_emit_against_old.py
"""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "_fail_p04_live_emit_against_old.json"


def file_done_old(*, output_exists: bool, observed_rc: int) -> dict:
    """Pre-P04: Output existence alone seals DONE; Core emit not consulted."""
    if output_exists:
        return {"state": "DONE", "observed_rc": observed_rc, "live_emit_checked": False}
    return {"state": "FAILED", "fail_kind": "FAILED", "observed_rc": observed_rc}


def main() -> int:
    td = Path(tempfile.mkdtemp(prefix="p04_old_"))
    out = td / "proposals" / "result.md"
    out.parent.mkdir(parents=True)
    out.write_text("green log only\n", encoding="utf-8")
    rec = file_done_old(output_exists=True, observed_rc=0)
    pin = {
        "output_nonempty": out.stat().st_size > 0,
        "observed_rc_zero": True,
        "old_sealed_done": rec.get("state") == "DONE",
        "no_core_emit_probe": rec.get("live_emit_checked") is False,
        "no_runtime_bind_field": True,
    }
    pin["predecessor_done_without_emit"] = all(pin.values())
    OUT.write_text(json.dumps(pin, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(pin, indent=2))
    return 0 if pin["predecessor_done_without_emit"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
