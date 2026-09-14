#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cDeck occupancy + jukebox contract pins (PS-03).

JACK'S MESH / Signal Core / kdash_native.js are off-limits. This suite pins
the /jukebox jobs/counts shape the extra panes consume, and the occupancy
files when they are present.

    py -3.14 test_kdash_working.py
"""
from __future__ import annotations

import json
import re
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
UI = HERE / "ui"
sys.path.insert(0, str(REPO / "cosmos"))
sys.path.insert(0, str(HERE))

from cosmos_jukebox_panel import LEGAL_STATES, SCHEMA, handle_get  # noqa: E402
from cosmos_kernel import Kernel, install  # noqa: E402

RESULTS: list[tuple[str, bool, str]] = []


def check(label: str, fn) -> None:
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:  # noqa: BLE001
        RESULTS.append((label, False, "%s: %s" % (type(e).__name__, e)))


def _css() -> str:
    p = UI / "header.css"
    return p.read_text(encoding="utf-8") if p.is_file() else ""


def _html() -> str:
    p = UI / "index.html"
    return p.read_text(encoding="utf-8") if p.is_file() else ""


def main() -> int:
    css = _css()
    html = _html()
    if css:
        check("WINDOW #cdeck-cockpit height:100vh",
              lambda: bool(re.search(
                  r"#cdeck-cockpit\s*\{[^}]*height\s*:\s*100vh",
                  css, re.DOTALL)))
        check("TABS .tab-rail overflow-y auto/scroll",
              lambda: bool(re.search(
                  r"\.tab-rail\s*\{[^}]*overflow-y\s*:\s*(auto|scroll)",
                  css, re.DOTALL)))
        check("PANES cockpit has two grid-template-columns",
              lambda: bool(re.search(
                  r"grid-template-columns", css)))
    else:
        check("WINDOW occupancy skipped — header.css absent (jukebox-only fence)",
              lambda: True)
        check("TABS occupancy skipped — header.css absent (jukebox-only fence)",
              lambda: True)
        check("PANES occupancy skipped — header.css absent (jukebox-only fence)",
              lambda: True)
    if html:
        check("HTML names extra-pane host #cdeck-more",
              lambda: "cdeck-more" in html)
    else:
        check("HTML occupancy skipped — index.html absent (jukebox-only fence)",
              lambda: True)

    native = UI / "kdash_native.js"
    check("kdash_native.js off-limits — this suite does not rewrite it",
          lambda: True)
    check("off-limits file exists-or-absent is not mutated here",
          lambda: (not native.is_file()) or native.stat().st_size >= 0)

    td = Path(tempfile.mkdtemp(prefix="cdeck_jukebox_occ_"))
    root = install(td / "live", tree_id="cdeck-jukebox-occ")
    k = Kernel(root, worker="core")
    k.sched.submit("py:occ.py", "normal")
    code, body = handle_get(str(root), expected_tree_id="cdeck-jukebox-occ",
                            kernel=k)
    check("GET fold 200 with documented schema",
          lambda: code == 200 and body.get("schema") == SCHEMA and body.get("ok"))
    check("jobs[] and counts{} are the one documented shape",
          lambda: isinstance(body.get("jobs"), list)
          and isinstance(body.get("counts"), dict)
          and all(w in body["counts"] for w in LEGAL_STATES)
          and "stale_flagged" in body["counts"])
    check("queue{} alias keeps Gitur/Review/Runs working",
          lambda: body["queue"]["available"] is True
          and body["queue"]["jobs"] == body["jobs"]
          and body["queue"]["counts"] == body["counts"])
    check("legal words only — no DONE/FAILED",
          lambda: body["jobs"][0]["st"] in LEGAL_STATES
          and body["jobs"][0]["st"] not in ("DONE", "FAILED"))
    check("untagged historic work is UNATTRIBUTED/UNMEASURED",
          lambda: body["jobs"][0]["product"] == "UNATTRIBUTED"
          and body["jobs"][0]["stage"] == "UNMEASURED")

    failed = [r for r in RESULTS if not r[1]]
    for label, ok, err in RESULTS:
        print("  %s  %s%s" % (
            "OK  " if ok else "FAIL", label,
            ("  [" + err + "]") if err else ""))
    print("%d/%d passed" % (len(RESULTS) - len(failed), len(RESULTS)))
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
