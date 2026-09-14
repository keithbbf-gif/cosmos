#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Occupancy-pin selftest for cDeck extra-pane tabs and pane geometry.

Reads static JS files under ui/ and pins that specific strings and values
are present (or absent). A value only the correct source can emit — not a
green-log claim.

Run:  py -3.14 builds/cdeck/test_kdash_working.py
      (from the repo root)
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
UI = HERE / "ui"
RESULTS: list[tuple[str, bool, str]] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    RESULTS.append((label, bool(ok), str(detail)[:240]))


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _read(name: str) -> str:
    p = UI / name
    if not p.is_file():
        return ""
    return p.read_text(encoding="utf-8", errors="replace")


def _fill_tabs_block(js: str) -> str:
    """Return the contents of `FILL_TABS = {…};` or ''."""
    if "FILL_TABS = {" not in js:
        return ""
    return js.split("FILL_TABS = {")[1].split("};")[0]


def _pane_defaults_block(js: str) -> str:
    """Return the contents of `PANE_DEFAULTS = {…};` or ''."""
    if "PANE_DEFAULTS = {" not in js:
        return ""
    return js.split("PANE_DEFAULTS = {")[1].split("};")[0]


def _system_wh(block: str) -> tuple[int | None, int | None]:
    """Extract w and h for the system pane from PANE_DEFAULTS block."""
    m = re.search(
        r"\bsystem\b\s*:\s*\{\s*w\s*:\s*(\d+)\s*,\s*h\s*:\s*(\d+)",
        block,
    )
    if not m:
        return None, None
    return int(m.group(1)), int(m.group(2))


# ---------------------------------------------------------------------------
# SYSTEM: pane geometry
# ---------------------------------------------------------------------------

tabs_js = _read("deck_tabs.js")

check("deck_tabs.js exists and is non-empty",
      bool(tabs_js),
      "path=%s" % (UI / "deck_tabs.js"))

pane_block = _pane_defaults_block(tabs_js)
check("PANE_DEFAULTS block found in deck_tabs.js",
      bool(pane_block),
      "block=%s" % pane_block[:60])

sys_w, sys_h = _system_wh(pane_block)
check("SYSTEM: system pane has w and h defined",
      sys_w is not None and sys_h is not None,
      "w=%s h=%s" % (sys_w, sys_h))

# Reference size: w=640, h=340. Doubled would be w=1280, h=680.
# The check fails when both w > 800 AND h > 500 (doubled-in-both-axes).
check("SYSTEM: default pane sizes do not double in x and y",
      sys_w is not None and sys_h is not None and sys_w <= 800 and sys_h <= 500,
      "w=%s h=%s (doubled would be 1280x680)" % (sys_w, sys_h))

# ---------------------------------------------------------------------------
# TAB SMOKE: FILL_TABS completeness
# ---------------------------------------------------------------------------

fill = _fill_tabs_block(tabs_js)
check("FILL_TABS block found in deck_tabs.js",
      bool(fill),
      "fill_start=%s" % fill[:40])

# Required tabs that must be present (not just the old extra-pane short-list).
REQUIRED_TABS = (
    "studio", "runs", "orders", "gitur", "forge", "crucible",
    "surfaces", "voice", "settings",
)
for tab in REQUIRED_TABS:
    check("FILL_TABS has %s:" % tab,
          tab + ":" in fill,
          "fill=%s" % fill[:80])

# The old "extra-pane set" was: recents, clock, runs, backup, tools, system, open —
# only those seven. The smoke check verifies the required primary tabs are present,
# meaning FILL_TABS is no longer limited to just the stale short-list.
old_set = {"recents", "clock", "runs", "backup", "tools", "system", "open"}
present = {t for t in old_set if t + ":" in fill}
new_tabs_present = any(t + ":" in fill for t in REQUIRED_TABS if t not in old_set)
check("TAB SMOKE: FILL_TABS not limited to the stale extra-pane set",
      new_tabs_present,
      "old_set_present=%s new_present=%s" % (sorted(present), new_tabs_present))

# ---------------------------------------------------------------------------
# report
# ---------------------------------------------------------------------------

bad = [(l, d) for l, ok, d in RESULTS if not ok]
for label, ok, detail in RESULTS:
    print("  %s  %s%s" % (
        "OK  " if ok else "FAIL",
        label,
        ("  [" + detail + "]") if detail and not ok else "",
    ))
print("SELFTEST %s — %d/%d pass (extra-pane occupancy pins)"
      % ("PASS" if not bad else "FAIL",
         len(RESULTS) - len(bad), len(RESULTS)))
return_code = 0 if not bad else 1


def test_kdash_working() -> None:
    assert return_code == 0, "test_kdash_working: %d checks failed" % len(bad)


if __name__ == "__main__":
    sys.exit(return_code)
