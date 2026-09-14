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

    open_js = _read("deck_open.js")
    hdr_js = _read("header.js")
    open_blob = open_js + "\n" + hdr_js + "\n" + html

    check(
        "OPEN tab: paints via Core GET /api/v1/openwork (not /tui/open-sessions)",
        "/api/v1/openwork" in open_js
        and "/tui/open-sessions" not in open_blob
        and "cdeckPaneOpen" in open_js,
        "api=%s tui=%s"
        % ("/api/v1/openwork" in open_js, "/tui/open-sessions" in open_blob),
    )

    check(
        "OPEN tab: LIVE chip + focus control; no hardcoded OpenWork port",
        "open-live" in open_js
        and "owFocusBtn" in open_js
        and re.search(r'action\s*:\s*["\']focus["\']', open_js)
        and not re.search(r":57383|:61512|:8770/health", open_js),
        "chip=%s focus=%s"
        % ("open-live" in open_js, "owFocusBtn" in open_js),
    )

    check(
        "OPEN tab: header uses same-origin apiGet (no default :8770 base)",
        "127.0.0.1:8770" not in hdr_js
        and "__CDECK_CFG" in hdr_js
        and "function apiGet" in hdr_js,
        "hardcoded=%s cfg=%s"
        % ("127.0.0.1:8770" in hdr_js, "__CDECK_CFG" in hdr_js),
    )

    check(
        "OPEN tab: index loads deck_open.js before deck_tabs.js",
        "deck_open.js" in html and html.index("deck_open.js") < html.index("deck_tabs.js"),
        "order ok=%s"
        % (
            "deck_open.js" in html
            and "deck_tabs.js" in html
            and html.index("deck_open.js") < html.index("deck_tabs.js")
        ),
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
