#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prove the new F-36 2.1a pins FAIL against the staged CORE_RESTRUCTURE.md.

Required before belief: all_new_pins_failed == true.

    py -3.14 builds/probe/_fail_f36_against_old.py
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
STAGE = (REPO / "docs" / "_delme" /
         "predispose_core_restructure_f36_20260831T155400Z" /
         "CORE_RESTRUCTURE.md")
OUT = HERE / "_fail_f36_against_old.json"

NEW_PINS = (
    "has_work_order_21a",
    "names_flip_streak_target",
    "names_keith_or_cow_as_flip_actor",
    "flip_ready_is_advice",
    "2_3_names_open_sites",
)


def pins_on(text: str) -> dict:
    lower = text.lower()
    return {
        "has_work_order_21a": "Work order 2.1a" in text,
        "names_flip_streak_target": "FLIP_STREAK_TARGET" in text and "96" in text,
        "names_keith_or_cow_as_flip_actor": "Keith or COW" in text,
        "flip_ready_is_advice": "advice, never an action" in lower,
        "2_3_names_open_sites": (
            "parse_tracker_markdown" in text
            and "wd2_dhx_haystack" in text
            and "critique_filename_stage" in text
        ),
    }


def main() -> int:
    text = STAGE.read_text(encoding="utf-8")
    pins = pins_on(text)
    rec = {
        "what": "new F-36 2.1a / whose-judgement pins FAIL against predecessor canon",
        "staged": str(STAGE),
        "pins": pins,
        "failed_pins": [k for k in NEW_PINS if pins[k] is False],
        "passed_pins": [k for k in NEW_PINS if pins[k] is True],
    }
    rec["all_new_pins_failed"] = (
        all(pins[k] is False for k in NEW_PINS)
        and len(rec["failed_pins"]) == len(NEW_PINS)
    )
    OUT.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({
        "all_new_pins_failed": rec["all_new_pins_failed"],
        "failed": rec["failed_pins"],
        "passed": rec["passed_pins"],
    }, indent=2))
    return 0 if rec["all_new_pins_failed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
