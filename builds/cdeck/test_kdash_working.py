#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cDeck occupancy pins — layout + Surfaces tab (canon rows).

Run: py -3.14 builds/cdeck/test_kdash_working.py
"""
from __future__ import annotations

import re
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


def _read(name: str) -> str:
    path = UI / name
    if not path.is_file():
        raise FileNotFoundError(str(path))
    return path.read_text(encoding="utf-8")


def _check_window() -> bool:
    css = _read("header.css")
    return bool(re.search(
        r"#cdeck-cockpit\s*\{[^}]*height\s*:\s*100vh",
        css, re.DOTALL,
    ))


def _check_tabs() -> bool:
    css = _read("header.css")
    return bool(re.search(
        r"\.tab-rail\s*\{[^}]*overflow-y\s*:\s*(auto|scroll)",
        css, re.DOTALL,
    ))


def _check_panes() -> bool:
    css = _read("header.css")
    m = re.search(r"grid-template-columns\s*:\s*([^;]+)", css)
    if not m:
        return False
    return len(m.group(1).strip().split()) >= 2


def _surfaces_js() -> str:
    return _read("app.js")


check("WINDOW", _check_window)
check("TABS", _check_tabs)
check("PANES", _check_panes)

check(
    "SURFACES canon five rows ROLD ITC GDX ODX TB1",
    lambda: all(n in _surfaces_js() for n in ("ROLD", "ITC", "GDX", "ODX", "TB1"))
    and "CANON_SURFACES" in _surfaces_js(),
)
check(
    "SURFACES renderSurfaces GET /api/v1/surfaces",
    lambda: "renderSurfaces" in _surfaces_js()
    and "/api/v1/surfaces" in _surfaces_js(),
)
check(
    "SURFACES missing payload UNMEASURED never omitted",
    lambda: "UNMEASURED" in _surfaces_js()
    and "CANON_SURFACES.forEach" in _surfaces_js(),
)
check(
    "SURFACES off-canon separate block",
    lambda: "surfaces-off-canon" in _surfaces_js()
    and "offCanon" in _surfaces_js(),
)
check(
    "SURFACES tab wires loadSurfacesPane",
    lambda: "loadSurfacesPane" in _read("app.js")
    and "loadSurfacesPane" in _read("deck_tabs.js"),
)
check(
    "SURFACES check control",
    lambda: "surfaces-check-btn" in _surfaces_js()
    and "surfaces-check" in _surfaces_js(),
)


def main() -> int:
    passed = sum(1 for _, ok, _ in RESULTS if ok)
    total = len(RESULTS)
    for label, ok, detail in RESULTS:
        status = "PASS" if ok else "FAIL"
        line = f"  {status}  {label}"
        if detail:
            line += f"  — {detail}"
        print(line)
    print(f"\n{passed}/{total} passed")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
