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

    forge = _read("deck_forge.js")
    check(
        "FORGE: CCr seat painted from GET /api/v1/model_rater into panel-forge-ccr",
        "panel-forge-ccr" in forge
        and 'apiGet("/api/v1/model_rater")' in forge
        and "paintCcr" in forge
        and 's.seat === "ccr"' in forge,
        "ccr_panel=%s model_rater_get=%s"
        % ("panel-forge-ccr" in forge, 'apiGet("/api/v1/model_rater")' in forge),
    )
    check(
        "FORGE: adversarial seats assign/unassign via POST /api/v1/model_rater/seat",
        'apiPost("/api/v1/model_rater/seat"' in forge
        and 'action: "add"' in forge
        and 'action: "remove"' in forge
        and "removeAdversary" in forge
        and "panel-forge-adv" in forge,
        "seat_post=%s add=%s remove=%s"
        % (
            'apiPost("/api/v1/model_rater/seat"' in forge,
            'action: "add"' in forge,
            'action: "remove"' in forge,
        ),
    )
    check(
        "FORGE: job token estimate POST /api/v1/model_rater/job_estimate",
        'apiPost("/api/v1/model_rater/job_estimate"' in forge
        and "saveJobEstimate" in forge
        and "panel-forge-job" in forge,
        "job_post=%s panel=%s"
        % (
            'apiPost("/api/v1/model_rater/job_estimate"' in forge,
            "panel-forge-job" in forge,
        ),
    )
    check(
        "FORGE: porosity GET /api/v1/porosity?profile=forge",
        'apiGet("/api/v1/porosity?profile=forge")' in forge
        and "paintPorosity" in forge
        and "panel-forge-porosity" in forge,
        "porosity_get=%s paint=%s"
        % (
            'apiGet("/api/v1/porosity?profile=forge")' in forge,
            "paintPorosity" in forge,
        ),
    )
    check(
        "FORGE: REFUSED surfaces in pane (.errbox) and addConsole",
        "REFUSED" in forge
        and "_surfaceRefused" in forge
        and "addConsole" in forge
        and "panel-forge-" in forge,
        "refusal_helper=%s errbox=%s"
        % ("_surfaceRefused" in forge, "errbox" in forge),
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
