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

    mesh_blob = html + "\n" + appjs

    check(
        "JUKE: renderJukebox hosts #jukeEl with audio planets/*.mp3 (no iframe)",
        "function renderJukebox" in appjs
        and 'id="jukeEl"' in html
        and "planets/" in appjs
        and "<iframe" not in mesh_blob.lower()
        and "youtube.com" not in mesh_blob.lower()
        and "ytplayer" not in mesh_blob.lower()
        and '<audio id="jukeAudio"' in appjs,
        "render=%s audio=%s"
        % ("function renderJukebox" in appjs, "planets/" in appjs),
    )

    check(
        "JUKE: play/pause/next controls wired in app.js",
        "btnJukePlay" in appjs
        and "btnJukePause" in appjs
        and "btnJukeNext" in appjs
        and "jukeAudio.play" in appjs
        and "jukeAudio.pause" in appjs
        and "loadPlanet(jukeIdx + 1" in appjs,
        "play=%s pause=%s next=%s"
        % ("btnJukePlay" in appjs, "btnJukePause" in appjs, "btnJukeNext" in appjs),
    )

    check(
        "JUKE: now-playing and volume pct track HTMLAudioElement (honest)",
        "jukeNowPlaying" in appjs
        and "paintNowPlaying" in appjs
        and "jukeAudio.volume" in appjs
        and "paintVolumePct" in appjs
        and "Math.round(jukeAudio.volume" in appjs,
        "now=%s vol=%s"
        % ("paintNowPlaying" in appjs, "paintVolumePct" in appjs),
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
