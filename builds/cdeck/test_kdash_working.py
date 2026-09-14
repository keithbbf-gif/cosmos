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

    studio = _read("deck_studio.js")
    appjs = _read("app.js")
    runs_blob = studio + "\n" + appjs

    check(
        "RUNS: list+detail painter loads from GET /api/v1/jukebox (not /jobs)",
        'apiGet("/api/v1/jukebox")' in runs_blob
        and "function paintRunsList" in studio
        and "function rowHtml" in studio
        and "function renderJobs" in appjs
        and '"/api/v1/jobs"' not in studio.split("fileNewJob")[0],
        "jukebox=%s paint=%s render=%s"
        % (
            'apiGet("/api/v1/jukebox")' in runs_blob,
            "paintRunsList" in studio,
            "renderJobs" in appjs,
        ),
    )

    check(
        "RUNS: JOB_ORDER includes FINDINGS and chip can filter FINDINGS when Core sends it",
        "JOB_ORDER" in studio
        and re.search(r'JOB_ORDER\s*=\s*\[[^\]]*"FINDINGS"', studio) is not None
        and "findingsInEmit" in studio
        and 'chipHtml("FINDINGS"' in studio,
        "findings_chip=%s" % ('FINDINGS' in studio),
    )

    check(
        "RUNS: filter chips survive the 10s poll (runsFilter module state, not reset on refresh)",
        "runsFilter" in studio
        and "10000" in appjs
        and "setInterval" in appjs
        and "paintRunsList(lastBody" in studio,
        "runsFilter=%s poll=%s"
        % ("runsFilter" in studio, "10000" in appjs),
    )

    check(
        "RUNS: file NEW job POSTs /api/v1/jobs without re-submitting a job_id",
        "file NEW job" in studio
        and 'apiPost("/api/v1/jobs"' in studio
        and "job_id" not in studio.split("function fileNewJob")[1].split("}")[0],
        "post=%s" % ('apiPost("/api/v1/jobs"' in studio),
    )

    mr = _read("model_rater.js")
    html_full = _read("index.html")
    check(
        "MODEL RATER: catalog from GET /api/v1/model_rater (no fake local catalog)",
        'apiGet("/api/v1/model_rater' in mr
        and "FAKE_CATALOG" not in mr
        and "fake catalog" not in mr.lower()
        and not re.search(r"var\s+CATALOG\s*=\s*\[", mr),
        "get=%s fake=%s"
        % ('apiGet("/api/v1/model_rater' in mr, "FAKE_CATALOG" in mr),
    )
    check(
        "MODEL RATER: seats + estimate POST /api/v1/model_rater/*",
        'apiPost("/api/v1/model_rater/seat"' in mr
        and 'apiPost("/api/v1/model_rater/estimate"' in mr
        and 'apiPost("/api/v1/model_rater/job_estimate"' in mr
        and 'apiPost("/api/v1/model_rater/refresh"' in mr,
        "estimate=%s job=%s refresh=%s"
        % (
            'apiPost("/api/v1/model_rater/estimate"' in mr,
            'apiPost("/api/v1/model_rater/job_estimate"' in mr,
            'apiPost("/api/v1/model_rater/refresh"' in mr,
        ),
    )
    check(
        "MODEL RATER: bench_defs + blend paint from Core snapshot",
        "bench_defs" in mr
        and "paintBlend" in mr
        and "paintBenchDefs" in mr
        and "blended_per_m" in mr,
        "bench=%s blend=%s"
        % ("bench_defs" in mr, "paintBlend" in mr),
    )
    check(
        "HEADER MODEL RATER drawer wired",
        "btnModelRater" in html_full and "model-rater-drawer" in html_full,
        "header drawer",
    )

    scroll_js = _read("deck_scroll.js")
    html_pan = _read("index.html")
    check(
        "PAGE PAN: deck_scroll module exists and persists horizontal offset per page id",
        scroll_js
        and (UI / "deck_scroll.js").is_file()
        and "deck.pagePan:" in scroll_js
        and "localStorage" in scroll_js
        and "writePagePan" in scroll_js
        and "composedPath" in scroll_js
        and "deck-page-pan" in html_pan
        and "deck_scroll.js" in html_pan,
        "module=%s persist=%s wired=%s"
        % (
            bool(scroll_js),
            "deck.pagePan:" in scroll_js,
            "deck_scroll.js" in html_pan,
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
