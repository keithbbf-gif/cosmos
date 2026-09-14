#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cDeck Profiles tab contract pins (repo root).

Run:  py -3.14 test_deck_features.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

UI = Path(__file__).resolve().parent / "builds" / "cdeck" / "ui"
RESULTS: list[tuple[str, bool, str]] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    RESULTS.append((label, bool(ok), str(detail)[:400]))


def _read(name: str) -> str:
    p = UI / name
    return p.read_text(encoding="utf-8") if p.is_file() else ""


def main() -> int:
    prof = _read("deck_profiles.js")
    header = _read("header.js")
    tabs = _read("deck_tabs.js")

    check(
        "header exposes apiGet/apiPost for pane code (no bare fetch in deck_profiles)",
        "apiGet" in header
        and "apiPost" in header
        and "fetch(" not in prof,
    )

    check(
        "deck_tabs wires profile child tabs to onProfilesDeckTab",
        "onProfilesDeckTab" in tabs and "profiles" in tabs,
    )

    check(
        "Profiles GET uses documented path with profile query",
        bool(re.search(r'apiGet\s*\(\s*["\']/api/v1/profiles\?profile=', prof)),
    )

    check(
        "SAVE SETUP uses POST /api/v1/profiles body — not MOTIF driver",
        'apiPost("/api/v1/profiles"' in prof
        and "watchdog" not in prof.lower()
        and "motif/start" not in prof.lower(),
    )

    check(
        "harvestPage collects form before SAVE (not noop)",
        "function harvestPage" in prof
        and "pf-page-define" in prof
        and "harvestPage(box, pid" in prof
        and "en.define.text" in prof,
    )

    check(
        "seven occupancy profile ids in PROFILE_ORDER",
        all(f'"{pid}"' in prof for pid in (
            "forge", "crucible", "diligence", "docket", "ups", "differentiator", "website"
        )),
    )

    passed = sum(1 for _, ok, _ in RESULTS if ok)
    total = len(RESULTS)
    for label, ok, detail in RESULTS:
        mark = "PASS" if ok else "FAIL"
        line = f"  {mark}  {label}"
        if detail and not ok:
            line += f"  — {detail}"
        print(line)
    print(f"\n{passed}/{total} passed")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
