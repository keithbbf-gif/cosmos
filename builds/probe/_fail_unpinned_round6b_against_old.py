#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""New round-6b pause pins MUST FAIL against the staged predecessor.

Staged at builds/probe/_delme/predispose_unpinned_round6b_20260831T161500Z/

Predecessor classify_pause([]) / classify_pause("hold") AttributeError
on .get. Anything unrecognised must be HOLD (docstring), never a crash.

CLOSE_REFUSED is still never raised — not in this fail set.

    py -3.14 builds/probe/_fail_unpinned_round6b_against_old.py
"""
from __future__ import annotations

import json
import sys
import types
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "_fail_unpinned_round6b_against_old.json"
OLD = HERE / "_delme" / "predispose_unpinned_round6b_20260831T161500Z"


def _exec(path: Path, name: str) -> types.ModuleType:
    mod = types.ModuleType(name)
    mod.__file__ = str(path)
    sys.modules[name] = mod
    exec(compile(path.read_text(encoding="utf-8"), str(path), "exec"),
         mod.__dict__)
    return mod


def main() -> int:
    failed = []
    ran = []
    if not (OLD / "cosmos_resession.py").is_file():
        raise SystemExit(f"missing predecessor {OLD}")
    old_rs = _exec(OLD / "cosmos_resession.py", "cosmos_resession_old_r6b")

    def _want_hold(label, fn):
        ran.append(label)
        try:
            got = fn()
            cls = got.get("class") if isinstance(got, dict) else None
            if cls != "HOLD":
                failed.append(f"{label}:returned:{got!r}"[:120])
        except Exception as e:                                        # noqa: BLE001
            failed.append(f"{label}:{type(e).__name__}")

    _want_hold("pause_array_is_HOLD", lambda: old_rs.classify_pause([]))
    _want_hold("pause_str_is_HOLD", lambda: old_rs.classify_pause("hold"))
    _want_hold("pause_true_is_HOLD", lambda: old_rs.classify_pause(True))

    rec = {
        "schema": "cosmos-bite/1",
        "what": "new round6b classify_pause pins FAIL against predecessor",
        "predecessor": str(OLD),
        "tests_run": len(ran),
        "failed_names": failed,
        "ran_names": ran,
        "all_new_pins_failed": (len(ran) > 0 and len(failed) == len(ran)),
    }
    OUT.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(rec, indent=2))
    return 0 if rec["all_new_pins_failed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
