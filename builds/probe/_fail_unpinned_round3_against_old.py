#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""New round-3 probe pins MUST FAIL against a stripped predecessor.

Staged at builds/probe/_delme/predispose_unpinned_round3_20260831T135200Z/

  * mode="resumed" + TidyUP set_by/reason is HOLD because unrecognised
    mode is checked BEFORE the ARM branch. Strip that check and the
    same flag becomes ARM — a wrong resume (M10).

    py -3.14 builds/probe/_fail_unpinned_round3_against_old.py
"""
from __future__ import annotations

import json
import sys
import types
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "_fail_unpinned_round3_against_old.json"
OLD = HERE / "_delme" / "predispose_unpinned_round3_20260831T135200Z"

NEEDLE = '''    if mode != "hold":
        return {"class": "HOLD",
                "why": f"unrecognised mode={mode!r} - fail-closed to HOLD"}
'''


def _exec(path: Path, name: str, src: str | None = None):
    mod = types.ModuleType(name)
    mod.__file__ = str(path)
    sys.modules[name] = mod
    text = src if src is not None else path.read_text(encoding="utf-8")
    exec(compile(text, str(path), "exec"), mod.__dict__)
    return mod


def main() -> int:
    failed = []
    ran = []
    src = (OLD / "cosmos_resession.py").read_text(encoding="utf-8")
    if NEEDLE not in src:
        failed.append("unrecognised_mode:needle_not_found")
    stripped = src.replace(NEEDLE, "    # STRIPPED unrecognised-mode HOLD\n")
    old = _exec(OLD / "cosmos_resession.py", "cr_old_r3", stripped)

    flag = {"state": "PAUSED", "mode": "resumed",
            "set_by": "COW", "reason": "TidyUP + resession"}
    ran.append("resumed_tidy_HOLD")
    cls = old.classify_pause(flag)
    if cls.get("class") == "HOLD":
        failed.append("resumed_tidy_HOLD:still_HOLD")
    else:
        failed.append(f"resumed_tidy_HOLD:{cls.get('class')}")

    out = {
        "schema": "cosmos-fail-against-old/1",
        "what": "round3 probe pins FAIL against stripped unrecognised-mode HOLD",
        "predecessor": str(OLD),
        "ran": ran,
        "failed": failed,
        "stripped_class": cls.get("class"),
        "all_new_pins_failed": bool(ran) and all(
            not f.endswith(":still_HOLD") and "needle_not_found" not in f
            for f in failed
        ) and len(failed) == len(ran),
    }
    # failed entries here ARE the proof the pin would not hold on old:
    # resumed_tidy_HOLD:ARM means the new pin (expects HOLD) FAILs.
    out["all_new_pins_failed"] = (
        bool(ran)
        and "needle_not_found" not in "".join(failed)
        and cls.get("class") != "HOLD"
    )
    OUT.write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=1))
    return 0 if out["all_new_pins_failed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
