#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cDeck occupancy pins — string checks on ui/ sources.

Run:  py -3.14 builds/cdeck/test_kdash_working.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent
UI = REPO / "ui"
RESULTS: list[tuple[str, bool, str]] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    RESULTS.append((label, bool(ok), str(detail)[:400]))


def _read(*names: str) -> str:
    parts = []
    for name in names:
        path = UI / name
        if path.is_file():
            parts.append(path.read_text(encoding="utf-8"))
    return "\n".join(parts)


def main() -> int:
    css = _read("header.css", "deck_more.css", "app.css")
    html = _read("index.html", "deck_more.html")
    blob = css + "\n" + html

    check(
        "WINDOW: MESH and extra panes share the viewport; no vh floor clips the tab rail",
        "#cdeck-viewport" in blob
        and "#cdeck-mesh-fold" in css
        and "#cdeck-more" in css
        and "min-height: 0" in css
        and not re.search(r"min-height:\s*\d+vh", css),
        "viewport=%s min0=%s vh_min=%s"
        % (
            "#cdeck-viewport" in blob,
            "min-height: 0" in css,
            bool(re.search(r"min-height:\s*\d+vh", css)),
        ),
    )

    check(
        "TABS: left rail scrolls inside the extra-pane shell so the lowest tab is reachable",
        "extra-pane-shell" in blob
        and "deck-tabs-rail" in blob
        and bool(
            re.search(
                r"\.deck-tabs-rail[^{]*\{[^}]*overflow-y:\s*(auto|scroll)",
                css,
                re.S | re.I,
            )
        )
        and "min-height: 0" in css,
        "shell=%s rail=%s"
        % ("extra-pane-shell" in blob, "deck-tabs-rail" in blob),
    )

    check(
        "PANES: the tab shell gets the whole fold, not one cockpit grid column",
        "deck-tab-shell" in blob
        and "deck-more-fold" in blob
        and "grid-column: 1 / -1" in css,
        "tab_shell=%s grid_span=%s"
        % ("deck-tab-shell" in blob, "grid-column: 1 / -1" in css),
    )

    app_js = _read("app.js")
    tabs_js = _read("deck_tabs.js")
    js = app_js + "\n" + tabs_js

    check(
        "CLOCK: renderClockPane GETs /api/v1/fleet and paints UNMEASURED without fake rows",
        "renderClockPane" in app_js
        and "/api/v1/fleet" in app_js
        and "UNMEASURED" in app_js
        and "schtasks" not in app_js.lower()
        and "cosmos_own_clocks" not in app_js
        and "CLOCKS =" not in app_js
        and app_js.count("UNMEASURED") >= 3,
        "app.js fleet binding",
    )

    check(
        "CLOCK: deck_tabs wires clock tab to renderClockPane (not a stub fill only)",
        "clock:" in js
        and "renderClockPane" in js
        and 'slot === "clock"' in js,
        "deck_tabs.js",
    )

    backup_js = _read("deck_backup.js")
    check(
        "BACKUP: paintClock GETs /api/v1/backup only (deck_backup.js)",
        "paintClock" in backup_js
        and "/api/v1/backup" in backup_js
        and "UNMEASURED" in backup_js,
        "deck_backup.js",
    )

    check(
        "BACKUP: deck_tabs wires backup tab to paintClock",
        'slot === "backup"' in js
        and "paintClock" in js,
        "deck_tabs backup",
    )

    failed = [r for r in RESULTS if not r[1]]
    for label, ok, detail in RESULTS:
        mark = "OK  " if ok else "FAIL"
        print("  %s  %s%s" % (mark, label, ("  [" + detail + "]") if detail and not ok else ""))
    print(
        "SELFTEST %s %d/%d"
        % ("PASS" if not failed else "FAIL", len(RESULTS) - len(failed), len(RESULTS))
    )
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
