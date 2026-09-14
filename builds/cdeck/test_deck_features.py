#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Static contract pins for cDeck events inspector + map pulse (EVT-1 / PULSE-1).

Run:  py -3.14 builds/cdeck/test_deck_features.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
UI = HERE / "ui"
RESULTS: list[tuple[str, bool, str]] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    RESULTS.append((label, bool(ok), str(detail)[:400]))


def _read(name: str) -> str:
    path = UI / name
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def main() -> int:
    html = _read("index.html")
    js = _read("app.js")
    css = _read("app.css")
    blob = html + "\n" + js + "\n" + css

    check(
        "EVT-1 the panel says the row is clickable and that scrolling pauses",
        "panel-events" in html
        and re.search(r"clickable", html, re.I)
        and re.search(r"scrolling pauses", html, re.I),
        "panel=%s clickable=%s scrolling_pauses=%s"
        % (
            "panel-events" in html,
            bool(re.search(r"clickable", html, re.I)),
            bool(re.search(r"scrolling pauses", html, re.I)),
        ),
    )

    check(
        "EVT-1 the inspector chrome exists in the DOM",
        'id="feed"' in html
        and 'id="feedJump"' in html
        and 'id="feedFollow"' in html
        and ".finspect" in blob
        and ".fevent" in blob,
        "feed=%s jump=%s follow=%s finspect=%s fevent=%s"
        % (
            'id="feed"' in html,
            'id="feedJump"' in html,
            'id="feedFollow"' in html,
            ".finspect" in blob,
            ".fevent" in blob,
        ),
    )

    check(
        "PULSE-1 a node the map does not already hold is NEVER created by an event",
        "PULSE_HOME" in js
        and re.search(
            r"a node the map does not already hold is NEVER created by an event",
            js,
            re.I,
        )
        and "nmapPulsePending" in js
        and "flushPendingPulses" in js
        and not re.search(r"function\s+pulse\w*[\s\S]{0,800}?addNode\s*\(", js),
        "PULSE_HOME=%s contract_line=%s queue=%s addNode_in_pulse=%s"
        % (
            "PULSE_HOME" in js,
            bool(
                re.search(
                    r"a node the map does not already hold is NEVER created by an event",
                    js,
                    re.I,
                )
            ),
            "nmapPulsePending" in js and "flushPendingPulses" in js,
            bool(re.search(r"function\s+pulse\w*[\s\S]{0,800}?addNode\s*\(", js)),
        ),
    )

    failed = [r for r in RESULTS if not r[1]]
    for label, ok, detail in RESULTS:
        mark = "OK  " if ok else "FAIL"
        print("  %s  %s%s" % (mark, label, ("  [" + detail + "]") if detail and not ok else ""))
    print("")
    print("  %d/%d passed" % (len(RESULTS) - len(failed), len(RESULTS)))
    return 1 if failed else 0


def test_deck_features_contract() -> None:
    assert main() == 0


if __name__ == "__main__":
    sys.exit(main())
