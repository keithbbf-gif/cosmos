#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cDeck layout + Settings popup occupancy pins — builds/cdeck/test_kdash_working.py

Layout (header.css + index.html):
  WINDOW — #cdeck-cockpit height:100vh floor
  TABS   — .tab-rail overflow-y:auto
  PANES  — grid-template-columns ≥2

Settings (deck_settings.js + index.html):
  SET-1  — #cdeck-settings-pop; GET /api/v1/status|usage|spend|cred via apiGet
  SET-2  — token fields UNMEASURED until n_obs (no invented 0)
  SET-3  — payment rows = vendor docs/homepage links; Keith does money

Run: py -3.14 builds/cdeck/test_kdash_working.py
     py -3.14 test_kdash_working.py   (repo-root wrapper)
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


def _css() -> str:
    p = UI / "header.css"
    if not p.is_file():
        raise FileNotFoundError(f"header.css not found at {p}")
    return p.read_text(encoding="utf-8")


def _html() -> str:
    p = UI / "index.html"
    if not p.is_file():
        raise FileNotFoundError(f"index.html not found at {p}")
    return p.read_text(encoding="utf-8")


def _js(name: str) -> str:
    p = UI / name
    if not p.is_file():
        raise FileNotFoundError(f"{name} not found at {p}")
    return p.read_text(encoding="utf-8")


def _check_window() -> bool:
    css = _css()
    return bool(re.search(
        r"#cdeck-cockpit\s*\{[^}]*height\s*:\s*100vh",
        css, re.DOTALL,
    ))


def _check_tabs() -> bool:
    css = _css()
    return bool(re.search(
        r"\.tab-rail\s*\{[^}]*overflow-y\s*:\s*(auto|scroll)",
        css, re.DOTALL,
    ))


def _check_panes() -> bool:
    css = _css()
    m = re.search(r"grid-template-columns\s*:\s*([^;]+)", css)
    if not m:
        return False
    tokens = m.group(1).strip().split()
    return len(tokens) >= 2


def _check_settings_pop() -> bool:
    html = _html()
    return 'id="cdeck-settings-pop"' in html and "deck_settings.js" in html


def _check_settings_get_paths() -> bool:
    js = _js("deck_settings.js")
    for path in (
        "/api/v1/status",
        "/api/v1/usage",
        "/api/v1/spend",
        "/api/v1/cred",
    ):
        if path not in js:
            return False
    return "apiGet" in js and "cdeckHeader" in js


def _check_settings_cards() -> bool:
    html = _html()
    js = _js("deck_settings.js")
    return (
        'id="set-card-status"' in html
        and 'id="set-card-usage"' in html
        and 'id="set-card-spend"' in html
        and "paintStatus" in js
        and "paintUsage" in js
        and "paintSpend" in js
    )


def _check_tokens_unmeasured_until_n_obs() -> bool:
    js = _js("deck_settings.js")
    return (
        "n_obs" in js
        and "UNMEASURED" in js
        and re.search(r"nObs\s*<\s*1", js) is not None
        and "tokField" in js
        and 'return "UNMEASURED"' in js
    )


def _check_payment_vendor_homepages() -> bool:
    js = _js("deck_settings.js")
    return (
        "paintPayments" in js
        and "s.docs" in js
        and "set-pay-row" in js
        and "Keith does money" in js
        and "complete a charge" in js
        and "/api/v1/cred" in js
        and "POST /api/v1/spend" not in js
    )


check("WINDOW", _check_window)
check("TABS", _check_tabs)
check("PANES", _check_panes)
check("SET-1 settings popup + deck_settings.js", _check_settings_pop)
check("SET-1 Core GET paths via apiGet", _check_settings_get_paths)
check("SET-1 status usage spend cards", _check_settings_cards)
check("SET-2 tokens UNMEASURED until n_obs", _check_tokens_unmeasured_until_n_obs)
check("SET-3 payment rows vendor homepages", _check_payment_vendor_homepages)


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


def test_layout_window():
    assert _check_window()


def test_layout_tabs():
    assert _check_tabs()


def test_layout_panes():
    assert _check_panes()


def test_settings_contract():
    assert _check_settings_pop()
    assert _check_settings_get_paths()
    assert _check_settings_cards()
    assert _check_tokens_unmeasured_until_n_obs()
    assert _check_payment_vendor_homepages()


if __name__ == "__main__":
    sys.exit(main())
