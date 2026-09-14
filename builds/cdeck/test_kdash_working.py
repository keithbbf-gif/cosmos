#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cDeck occupancy pins — CoP node wiring on System/Forge panes.

Run:  python3 builds/cdeck/test_kdash_working.py
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
    css = _read("header.css", "app.css")
    html = _read("index.html", "deck_more.html")
    blob = css + "\n" + html
    app = _read("app.js")
    forge = _read("deck_forge.js")
    tabs = _read("deck_tabs.js")
    nodemap = (REPO / "cosmos_nodemap_panel.py").read_text(encoding="utf-8")
    panes = app + "\n" + forge + "\n" + tabs

    check(
        "WINDOW: MESH and extra panes share the viewport; no vh floor clips the tab rail",
        "#cdeck-viewport" in blob
        and "#cdeck-mesh-fold" in css
        and "#cdeck-more" in css
        and "min-height: 0" in css
        and not re.search(r"min-height:\s*\d+vh", css),
    )
    check(
        "TABS: left rail scrolls inside the extra-pane shell so the lowest tab is reachable",
        "extra-pane-shell" in blob
        and "deck-tabs-rail" in blob
        and bool(re.search(r"overflow-y:\s*(auto|scroll)", css))
        and "min-height: 0" in css,
    )
    check(
        "PANES: the tab shell gets the whole fold, not one cockpit grid column",
        "deck-tab-shell" in blob
        and "deck-more-fold" in blob
        and "grid-column: 1 / -1" in css,
    )
    check(
        "SYSTEM: paintSystemTab GETs /api/v1/nodemap and /api/v1/fleet (no invented /cop)",
        "function paintSystemTab" in app
        and 'apiGet("/api/v1/nodemap")' in app
        and 'apiGet("/api/v1/fleet")' in app
        and 'apiGet("/api/v1/rails")' in app
        and "/api/v1/cop" not in panes,
    )
    check(
        "SYSTEM: renderNodemap paints cop-chat from payload; empty is explicit",
        "function renderNodemap" in app
        and "cop-chat" in app
        and "empty (not in payload)" in app
        and "function paintNodeRow" in app,
    )
    check(
        "STALE renders RED; UNMEASURED is never painted as 0",
        "stale-red" in app
        and "stale-red" in css
        and "UNMEASURED" in app
        and not re.search(r'UNMEASURED.*=\s*0', app),
    )
    check(
        "INDEPENDENCE: SGH+GBW are not independent checks of each other (System+Forge+nodemap)",
        "SGH+GBW are not independent checks of each other" in app
        and "SGH+GBW are not independent checks of each other" in forge
        and "SGH+GBW are not independent checks of each other" in nodemap,
    )
    check(
        "FORGE: paintForgeTab/refresh GETs /api/v1/nodemap and paints cop-chat",
        "paintForgeNodes" in forge
        and 'apiGet("/api/v1/nodemap")' in forge
        and "cop-chat" in forge
        and "stale-red" in forge,
    )
    check(
        "ESC: System and Forge escape all data text",
        "function esc" in app
        and "function esc" in forge
        and "esc(note)" in app
        and "esc(note)" in forge,
    )
    check(
        "TABS: system + forge shells exist; FILL_TABS names both",
        "ensureSystemShell" in tabs
        and "ensureForgeShell" in tabs
        and 'system: "system"' in tabs
        and 'forge: "forge"' in tabs,
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
