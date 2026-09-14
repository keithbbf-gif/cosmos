#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cDeck layout occupancy pins — builds/cdeck/test_kdash_working.py

Three layout constraints on the cDeck viewport split (header.css + index.html):

  WINDOW — #cdeck-cockpit has a height:100vh floor so MESH (.deck-stage) and
            the extra-pane shell (#cdeck-more) each occupy their own viewport
            column and do NOT share one unbounded scroll area.

  TABS   — .tab-rail carries overflow-y:auto so the left rail scrolls inside
            the extra-pane shell and the lowest tab is always reachable.

  PANES  — The cockpit grid declares at least two grid-template-columns so
            #cdeck-more is one column, not the whole fold.

Run: py -3.14 builds/cdeck/test_kdash_working.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
UI   = HERE / "ui"

RESULTS: list[tuple[str, bool, str]] = []


def check(label: str, fn) -> None:
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:                             # noqa: BLE001
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


# ── WINDOW ────────────────────────────────────────────────────────────────────
# The cockpit container (#cdeck-cockpit) must carry height:100vh so the
# viewport is split into fixed-height columns.  Without it MESH and extra
# panes share one unbounded scroll area and the tab rail has no floor.
def _check_window() -> bool:
    css = _css()
    return bool(re.search(
        r"#cdeck-cockpit\s*\{[^}]*height\s*:\s*100vh",
        css, re.DOTALL,
    ))


# ── TABS ──────────────────────────────────────────────────────────────────────
# .tab-rail must carry overflow-y:auto (or scroll) so the left rail scrolls
# inside the extra-pane shell (#cdeck-more).  Without it the tab list grows
# past the viewport and the lowest tab is unreachable.
def _check_tabs() -> bool:
    css = _css()
    return bool(re.search(
        r"\.tab-rail\s*\{[^}]*overflow-y\s*:\s*(auto|scroll)",
        css, re.DOTALL,
    ))


# ── PANES ─────────────────────────────────────────────────────────────────────
# The cockpit grid must declare at least two grid-template-columns so
# #cdeck-more occupies one column and .deck-stage occupies another.
# A single-column (or no-grid) layout gives the tab shell the whole fold.
def _check_panes() -> bool:
    css = _css()
    m = re.search(r"grid-template-columns\s*:\s*([^;]+)", css)
    if not m:
        return False
    # Must have at least two whitespace-separated tokens (two columns)
    tokens = m.group(1).strip().split()
    return len(tokens) >= 2


def _check_profiles_esc() -> bool:
    p = UI / "deck_profiles.js"
    if not p.is_file():
        return False
    src = p.read_text(encoding="utf-8")
    return "function esc(" in src and "esc(" in src


def _check_portfolio_studio_core_contract() -> bool:
    import tempfile

    sys.path.insert(0, str(REPO / "cosmos"))
    from cosmos_kernel import install
    from cosmos_paths import CosmosPaths
    from cosmos_profiles import portfolio_studio_live_is_honest, snapshot

    td = Path(tempfile.mkdtemp(prefix="kdash_ps_"))
    root = install(td / "live", tree_id="kdash-ps-contract")
    paths = CosmosPaths(root)
    snap = snapshot(paths, profile="website")
    ps = snap.get("portfolio_studio") or {}
    return (
        len(snap.get("stages") or []) == 9
        and isinstance(snap.get("profiles"), list)
        and snap.get("does_not_start_motif") is True
        and portfolio_studio_live_is_honest(ps.get("live") or {})
    )


# ── register checks ───────────────────────────────────────────────────────────
check("WINDOW", _check_window)
check("TABS",   _check_tabs)
check("PANES",  _check_panes)
check("PROFILES-ESC", _check_profiles_esc)
check("PORTFOLIO-STUDIO-CONTRACT", _check_portfolio_studio_core_contract)


# ── report ────────────────────────────────────────────────────────────────────
def main() -> int:
    passed = sum(1 for _, ok, _ in RESULTS if ok)
    total  = len(RESULTS)
    for label, ok, detail in RESULTS:
        status = "PASS" if ok else "FAIL"
        line   = f"  {status}  {label}"
        if detail:
            line += f"  — {detail}"
        print(line)
    print(f"\n{passed}/{total} passed")
    return 0 if passed == total else 1


def test_layout_window():
    assert _check_window(), (
        "WINDOW: #cdeck-cockpit must have height:100vh in header.css"
    )


def test_layout_tabs():
    assert _check_tabs(), (
        "TABS: .tab-rail must have overflow-y:auto or overflow-y:scroll in header.css"
    )


def test_layout_panes():
    assert _check_panes(), (
        "PANES: grid-template-columns must define ≥2 columns in header.css"
    )


if __name__ == "__main__":
    sys.exit(main())
