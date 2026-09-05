#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""New round-5 probe pins MUST FAIL against the staged predecessor.

Staged at builds/probe/_delme/predispose_unpinned_round5_20260831T143821Z/

Predecessor:
  * scout sentinel `[]` AttributeError
  * maker_hands `{not json` JSONDecodeError
  * maker_hands `[]` AttributeError

    py -3.14 builds/probe/_fail_unpinned_round5_against_old.py
"""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
import types
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "_fail_unpinned_round5_against_old.json"
OLD = HERE / "_delme" / "predispose_unpinned_round5_20260831T143821Z"


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
    tmp = Path(tempfile.mkdtemp(prefix="cosmos_failold_r5p_"))
    try:
        old_s = _exec(OLD / "cosmos_newai_scout.py", "scout_old_r5")
        old_h = _exec(OLD / "maker_hands_probe.py", "hands_old_r5")

        arr = tmp / "arr_root"
        arr.mkdir()
        (arr / ".cosmos-root.json").write_text("[]", encoding="utf-8")
        ran.append("scout_array_is_NO_ROOT")
        try:
            old_s.verify_root(arr)
            failed.append("scout_array_is_NO_ROOT:did_not_raise")
        except old_s.ScoutRefusal as e:
            if e.kind != "NO_ROOT":
                failed.append(f"scout_array_is_NO_ROOT:{e.kind}")
        except Exception as e:                                        # noqa: BLE001
            failed.append(f"scout_array_is_NO_ROOT:{type(e).__name__}")

        garbage = tmp / "hands_garbage"
        garbage.mkdir()
        (garbage / ".cosmos-root.json").write_text("{not json", encoding="utf-8")
        ran.append("hands_garbage_is_BAD_SENTINEL")
        try:
            old_h._verify_root(str(garbage))
            failed.append("hands_garbage_is_BAD_SENTINEL:did_not_raise")
        except old_h.ProbeRefusal as e:
            if getattr(e, "kind", None) != "BAD_SENTINEL":
                failed.append(f"hands_garbage_is_BAD_SENTINEL:{getattr(e, 'kind', None)}")
        except Exception as e:                                        # noqa: BLE001
            failed.append(f"hands_garbage_is_BAD_SENTINEL:{type(e).__name__}")

        harr = tmp / "hands_arr"
        harr.mkdir()
        (harr / ".cosmos-root.json").write_text("[]", encoding="utf-8")
        ran.append("hands_array_is_BAD_SENTINEL")
        try:
            old_h._verify_root(str(harr))
            failed.append("hands_array_is_BAD_SENTINEL:did_not_raise")
        except old_h.ProbeRefusal as e:
            if getattr(e, "kind", None) != "BAD_SENTINEL":
                failed.append(f"hands_array_is_BAD_SENTINEL:{getattr(e, 'kind', None)}")
        except Exception as e:                                        # noqa: BLE001
            failed.append(f"hands_array_is_BAD_SENTINEL:{type(e).__name__}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    rec = {
        "schema": "cosmos-fail-old/1",
        "what": "round5 probe pins against predecessor",
        "ran": ran,
        "failed": failed,
        "n_ran": len(ran),
        "n_failed": len(failed),
        "all_new_pins_failed": len(failed) == len(ran) and len(ran) > 0,
    }
    OUT.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(rec, indent=1))
    return 0 if rec["all_new_pins_failed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
