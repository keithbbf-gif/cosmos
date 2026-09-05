#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bite: CORE_RESTRUCTURE.md had no work order 2.1a (whose judgement).

Required before belief. Staged incumbent:
docs/_delme/predispose_core_restructure_f36_20260831T155400Z/CORE_RESTRUCTURE.md

    py -3.14 builds/probe/_bite_f36_judgement.py
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
STAGE = (REPO / "docs" / "_delme" /
         "predispose_core_restructure_f36_20260831T155400Z" /
         "CORE_RESTRUCTURE.md")
OUT = HERE / "_bite_f36_judgement.json"


def main() -> int:
    text = STAGE.read_text(encoding="utf-8") if STAGE.is_file() else ""
    rec = {
        "staged": str(STAGE),
        "staged_exists": STAGE.is_file(),
        "bytes": STAGE.stat().st_size if STAGE.is_file() else 0,
        "has_work_order_21a": "Work order 2.1a" in text,
        "names_flip_streak_target": "FLIP_STREAK_TARGET" in text,
        "names_keith_or_cow": "Keith or COW" in text,
        "names_flip_ready_advice": "advice, never an action" in text.lower()
        or "advice, never an action" in text,
        "still_says_json_becomes_source": "JSON becomes source" in text,
        "2_3_names_open_sites": "wd2_dhx_haystack" in text,
    }
    rec["all_bite"] = (
        rec["staged_exists"] is True
        and rec["has_work_order_21a"] is False
        and rec["names_flip_streak_target"] is False
        and rec["names_keith_or_cow"] is False
        and rec["2_3_names_open_sites"] is False
        and rec["still_says_json_becomes_source"] is True
    )
    OUT.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({
        "all_bite": rec["all_bite"],
        "has_work_order_21a": rec["has_work_order_21a"],
        "staged_exists": rec["staged_exists"],
        "bytes": rec["bytes"],
    }, indent=2))
    return 0 if rec["all_bite"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
