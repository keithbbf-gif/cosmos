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
    js = _read("app.js")
    blob = css + "\n" + html + "\n" + js

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
        "VOICE B7-010: renderVoiceLoop wires GET /api/v1/voice_loop and loop controls",
        "function renderVoiceLoop" in js
        and 'get("/api/v1/voice_loop")' in js
        and 'post("/api/v1/voice_loop"' in js
        and 'action: "new_sop"' in js
        and "btnVoiceRefresh" in js,
        "render=%s get=%s post=%s"
        % (
            "function renderVoiceLoop" in js,
            'get("/api/v1/voice_loop")' in js,
            'post("/api/v1/voice_loop"' in js,
        ),
    )

    check(
        "VOICE B7-010: Voice loop never auto-runs on load (explicit tab / Refresh only)",
        "no auto-run on load" in js
        and "function boot()" in js
        and not re.search(
            r"DOMContentLoaded[\s\S]{0,400}renderVoiceLoop\s*\(",
            js,
        )
        and not re.search(r"setInterval\s*\([\s\S]{0,120}voice_loop", js),
        "hint=%s boot=%s dom_autorender=%s"
        % (
            "no auto-run on load" in js,
            "function boot()" in js,
            bool(
                re.search(
                    r"DOMContentLoaded[\s\S]{0,400}renderVoiceLoop\s*\(",
                    js,
                )
            ),
        ),
    )

    talk_block = js.split("function renderTalk")[1].split("function renderVoiceLoop")[0] if "function renderTalk" in js else ""
    voice_block = js.split("function renderVoiceLoop")[1].split("var PANE_RENDER")[0] if "function renderVoiceLoop" in js else ""
    check(
        "VOICE B7-010: micHint mic state surfaces on Talk only, not on Voice tab",
        'id="micHint"' in talk_block
        and "setMicHint" in talk_block
        and 'id="micHint"' not in voice_block
        and "mic state is on Talk only" in js,
        "talk_micHint=%s voice_micHint=%s"
        % ('id="micHint"' in talk_block, 'id="micHint"' in voice_block),
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
