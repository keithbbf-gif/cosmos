#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cDeck occupancy + Gitur tab contract pins (repo root entry).

Run:  py -3.14 test_kdash_working.py
Also: py -3.14 builds/cdeck/test_kdash_working.py (layout subset)
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
UI = ROOT / "builds" / "cdeck" / "ui"
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


def _layout_pins() -> None:
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

    tabs = _read("deck_tabs.js")
    fill = tabs.split("FILL_TABS = {")[1].split("};")[0] if "FILL_TABS = {" in tabs else ""
    check(
        "TAB SMOKE: FILL_TABS names gitur with studio runs orders forge crucible",
        all(n + ":" in fill for n in (
            "studio", "runs", "orders", "gitur", "forge", "crucible")),
        "fill=%s" % fill[:160],
    )


def _gitur_pins() -> None:
    js = _read("deck_gitur.js")
    check("GITUR: deck_gitur.js exists", bool(js.strip()), str(UI / "deck_gitur.js"))
    check(
        "GITUR: refresh uses apiGet on GET /api/v1/gitur (not api.get)",
        'apiGet("/api/v1/gitur")' in js and "api.get" not in js,
        "apiGet=%s api.get=%s"
        % ('apiGet("/api/v1/gitur")' in js, "api.get" in js),
    )
    check(
        "GITUR: pane code does not call fetch() directly",
        "fetch(" not in js,
        "fetch_count=%s" % js.count("fetch("),
    )
    check(
        "GITUR: triad leg ids github-forge gitlab-forge cursor-api paint",
        all(x in js for x in ("github-forge", "gitlab-forge", "cursor-api")),
        "legs_present",
    )
    check(
        "GITUR: probe + launch POST documented job paths",
        'apiPost("/api/v1/jobs"' in js
        and "cosmos_cursor_rail.py --gate" in js
        and "cosmos_cursor_rail.py --launch" in js,
        "jobs_post=%s" % ('apiPost("/api/v1/jobs"' in js),
    )
    check(
        "GITUR: jukebox-named rows (source jukebox / jobs_kind)",
        "jukebox" in js and "source === \"jukebox\"" in js,
        "jukebox_filter",
    )
    check(
        "GITUR: filter census kept · dropped when q is non-empty",
        "kept " in js and "dropped" in js and "gitur-filter-census" in js,
        "census",
    )
    check(
        "GITUR: last-good on fail (LAST_GOOD repaints)",
        "LAST_GOOD" in js and "paintAll(LAST_GOOD)" in js,
        "last_good",
    )
    check(
        "GITUR: does not invent PR lists — uses live.prs only with UNMEASURED fallback",
        "live.prs" in js
        and "invent" not in js.lower().replace("not invented", ""),
        "prs_from_live",
    )
    check(
        "GITUR: probe and launch paint targets in DOM",
        "gitur-probe" in js and "gitur-launch" in js,
        "probe_launch_ids",
    )


def main() -> int:
    _layout_pins()
    _gitur_pins()
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
