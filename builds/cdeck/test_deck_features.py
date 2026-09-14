#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cDeck Surfaces tab contract pins (static ui/ sources).

Run: py -3.14 builds/cdeck/test_deck_features.py
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
UI = HERE / "ui"
RESULTS: list[tuple[str, bool, str]] = []


def check(label: str, fn) -> None:
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:  # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


def _app() -> str:
    return (UI / "app.js").read_text(encoding="utf-8")


CANON = ("ROLD", "ITC", "GDX", "ODX", "TB1")

check(
    "B7-008 CANON_SURFACES lists five canon names in order",
    lambda: _app().split("CANON_SURFACES = [")[1].split("]")[0].count('"') // 2 == 5
    and all(c in _app() for c in CANON),
)
check(
    "B7-008 renderSurfaces exported on window",
    lambda: "window.renderSurfaces = renderSurfaces" in _app(),
)
check(
    "B7-008 GET path is /api/v1/surfaces not surfaces_kit",
    lambda: 'apiGet("/api/v1/surfaces")' in _app()
    and "/api/v1/surfaces_kit" not in _app(),
)
check(
    "B7-008 UNMEASURED literal for absent measurements",
    lambda: _app().count("UNMEASURED") >= 2,
)
check(
    "B7-008 off-canon section class surfaces-off-canon",
    lambda: "surfaces-off-canon" in _app() and "surfaces-canon" in _app(),
)
check(
    "B7-008 503 surfaces Core error string not swallowed",
    lambda: "CDECK_PANEL_NOT_COMPOSED" in _app() or "j.error" in _app(),
)
check(
    "B7-008 check button id surfaces-check-btn",
    lambda: "surfaces-check-btn" in _app(),
)
check(
    "ODX payload fields reachable/free_gb/age_s/qualified via byId, null=UNMEASURED",
    lambda: "byId[name]" in _app()
    and "cellQual" in _app()
    and _app().count("UNMEASURED") >= 3
    and "ODX" in _app(),
)


def main() -> int:
    passed = sum(1 for _, ok, _ in RESULTS if ok)
    total = len(RESULTS)
    for label, ok, detail in RESULTS:
        print(f"  {'PASS' if ok else 'FAIL'}  {label}" + (f"  — {detail}" if detail else ""))
    print(f"\n{passed}/{total} passed")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
