#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cDeck occupancy + Studio tab pins (repo root entry).

Run: py -3.14 test_kdash_working.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent
UI = REPO / "builds" / "cdeck" / "ui"
RESULTS: list[tuple[str, bool, str]] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    RESULTS.append((label, bool(ok), str(detail)[:400]))


def _read(*names: str) -> str:
    parts = []
    for name in names:
        p = UI / name
        if p.is_file():
            parts.append(p.read_text(encoding="utf-8"))
    return "\n".join(parts)


def main() -> int:
    css = _read("header.css", "deck_more.css", "app.css")
    html = _read("index.html", "deck_more.html")
    studio = _read("deck_studio.js")
    tabs = _read("deck_tabs.js")
    blob = css + "\n" + html + "\n" + studio + "\n" + tabs

    check(
        "WINDOW: #cdeck-cockpit height:100vh splits MESH and extra panes",
        bool(re.search(r"#cdeck-cockpit\s*\{[^}]*height\s*:\s*100vh", css, re.S)),
        "cockpit_vh=%s" % bool(re.search(r"height\s*:\s*100vh", css)),
    )
    check(
        "TABS: .tab-rail scrolls inside #cdeck-more",
        bool(re.search(r"\.tab-rail\s*\{[^}]*overflow-y\s*:\s*(auto|scroll)", css, re.S)),
        "tab_rail_scroll=%s" % ("tab-rail" in blob),
    )
    check(
        "PANES: cockpit grid has at least two columns",
        bool(re.search(r"grid-template-columns\s*:\s*\S+\s+\S+", css)),
        "grid_cols=%s" % bool(re.search(r"grid-template-columns", css)),
    )
    check(
        "STUDIO: index loads deck_studio.js",
        "deck_studio.js" in html,
        "script_tag=%s" % ("deck_studio.js" in html),
    )
    check(
        "STUDIO: MOTIF STAGES 1–9 DEFINE through ITERATE",
        studio.count("name:") >= 9
        and "DEFINE" in studio
        and "ITERATE" in studio
        and "STAGES" in studio,
        "stages_block=%s" % ("STAGES" in studio),
    )
    check(
        "STUDIO: load/save uses GET/POST /api/v1/studio via apiGet/apiPost",
        '"/api/v1/studio"' in studio
        and "apiGet" in studio
        and "apiPost" in studio
        and "fetch(" not in studio,
        "fetch_free=%s" % ("fetch(" not in studio),
    )
    check(
        "STUDIO: heat overlay uses GET /api/v1/jukebox queue words only",
        '"/api/v1/jukebox"' in studio
        and "QUEUED" in studio
        and "RUNNING" in studio
        and "FINDINGS" in studio
        and "BROKE" in studio
        and "CLEAN" in studio,
        "jukebox_path=%s" % ('"/api/v1/jukebox"' in studio),
    )
    check(
        "STUDIO: SAVE never IMPLEMENTs (no MOTIF start / no jobs POST)",
        "Does NOT start MOTIF" in studio
        and "never runs IMPLEMENT" in studio
        and "/api/v1/jobs" not in studio
        and "/api/v1/motif" not in studio,
        "motif_jobs_absent=%s"
        % ("/api/v1/jobs" not in studio and "/api/v1/motif" not in studio),
    )
    check(
        "STUDIO: deck_tabs mounts DeckStudio on studio tab",
        "DeckStudio" in tabs and 'activateTab("studio")' in tabs,
        "mount=%s" % ("DeckStudio" in tabs),
    )
    check(
        "TAB SMOKE: FILL_TABS includes studio and forge",
        "studio:" in tabs and "forge:" in tabs,
        "fill=%s" % ("FILL_TABS" in tabs),
    )

    failed = [r for r in RESULTS if not r[1]]
    for label, ok, detail in RESULTS:
        mark = "OK  " if ok else "FAIL"
        print("  %s  %s%s" % (mark, label, ("  [" + detail + "]") if detail and not ok else ""))
    passed = len(RESULTS) - len(failed)
    print("\n%d/%d passed" % (passed, len(RESULTS)))
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
