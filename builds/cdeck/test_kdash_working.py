#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cDeck occupancy pins — string checks on ui/ sources.

Run:  py -3.14 builds/cdeck/test_kdash_working.py
      py -3.14 test_kdash_working.py   (repo-root wrapper)
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
    header_js = _read("header.js")
    backup_js = _read("deck_backup.js")
    tabs_js = _read("deck_tabs.js")
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

    check(
        "HEADER: CONNECT runs automatically on load (connectOnLoad → doConnect)",
        "function connectOnLoad" in header_js
        and "connectOnLoad();" in header_js
        and "function doConnect" in header_js,
        "connectOnLoad=%s doConnect=%s"
        % ("connectOnLoad();" in header_js, "function doConnect" in header_js),
    )

    check(
        "HEADER: PAUSE/RESUME immediately refresh when leaving pause",
        "function onPauseClick" in header_js
        and "refreshAll(true)" in header_js
        and 'btn.textContent = paused ? "RESUME" : "PAUSE"' in header_js,
        "onPauseClick=%s refreshAll_true=%s"
        % ("function onPauseClick" in header_js, "refreshAll(true)" in header_js),
    )

    check(
        "HEADER: RELOAD clears tier holds and forces refreshAll(true)",
        'id="btnReload"' in html
        and "function onReloadClick" in header_js
        and "dueAt = Object.create(null)" in header_js,
        "btnReload_html=%s onReload=%s"
        % ('id="btnReload"' in html, "function onReloadClick" in header_js),
    )

    check(
        "HEADER: PAUSE/RELOAD stay disabled until CONNECT succeeds",
        'id="btnPause" disabled' in html
        and 'id="btnReload" disabled' in html
        and "function setRefreshControlsEnabled" in header_js
        and "bp.disabled = !on" in header_js
        and "br.disabled = !on" in header_js,
        "html_disabled=%s setter=%s"
        % ('id="btnPause" disabled' in html, "setRefreshControlsEnabled" in header_js),
    )

    check(
        "HEADER: deck_more.html matches index extra-pane skeleton",
        "extra-pane-shell" in _read("deck_more.html")
        and "deck-tabs-rail" in _read("deck_more.html")
        and "deck-tab-shell" in _read("deck_more.html"),
        "deck_more_fragment=%s" % ("extra-pane-shell" in _read("deck_more.html")),
    )

    check(
        "B7-013 BACKUP: deck_backup.js surfaces test/generate/scheduler/search/profiles/restore panels",
        all(
            pid in backup_js
            for pid in (
                "backup-panel-test",
                "backup-panel-generate",
                "backup-panel-scheduler",
                "backup-panel-search",
                "backup-panel-profiles",
                "backup-panel-restore",
            )
        ),
        "panels in deck_backup.js",
    )

    check(
        "B7-013 BACKUP: GET /api/v1/backup fold poll — GET never runs a backup",
        'apiGet("/api/v1/backup")' in backup_js
        and "GET never runs a backup" in backup_js
        and 'apiPost("/api/v1/backup"' in backup_js,
        "GET vs POST paths",
    )

    check(
        "B7-013 BACKUP: POST surface_test search restore generate wired",
        'action: "surface_test"' in backup_js
        and 'action: "search"' in backup_js
        and 'action: "restore"' in backup_js
        and 'action: "generate"' in backup_js
        and "measure_all" in backup_js,
        "POST verbs",
    )

    check(
        "B7-013 BACKUP: per-profile dest chips on backup tab",
        "profile-backup-dest-chip" in backup_js
        and "backup-panel-profiles" in backup_js,
        "dest chips",
    )

    check(
        "B7-013 BACKUP: backup tab in FILL_TABS and script loaded from index",
        "backup:" in tabs_js
        and "deck_backup.js" in html,
        "tab + script",
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
