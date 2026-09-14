#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cDeck Studio + static feature contract pins (repo root entry).

Run: py -3.14 test_deck_features.py
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


def _read(name: str) -> str:
    p = UI / name
    return p.read_text(encoding="utf-8") if p.is_file() else ""


def main() -> int:
    studio = _read("deck_studio.js")
    header = _read("header.js")

    check(
        "STUDIO-1 pane uses header apiGet/apiPost kit (no bare fetch in studio)",
        "apiGet" in header
        and "apiPost" in header
        and "fetch(" not in studio,
        "header_kit=%s studio_fetch=%s"
        % ("apiGet" in header, "fetch(" in studio),
    )
    check(
        "STUDIO-2 saveStage POST body is config-only; IMPLEMENT note path",
        "saveStage" in studio
        and 'post("/api/v1/studio"' in studio.replace(" ", "")
        or '.post("/api/v1/studio"' in studio,
        "saveStage=%s" % ("saveStage" in studio),
    )
    check(
        "STUDIO-3 heat maps motif stage numbers from jukebox rows",
        "stageFromJobRow" in studio and "paintHeatFromJukebox" in studio,
        "heat_fn=%s" % ("paintHeatFromJukebox" in studio),
    )
    check(
        "STUDIO-4 JUKEBOX_WORDS frozen set matches Core scheduler vocabulary",
        all(w in studio for w in ("QUEUED", "RUNNING", "BROKE", "CLEAN", "FINDINGS")),
        "words=%s"
        % all(w in studio for w in ("QUEUED", "RUNNING", "BROKE", "CLEAN", "FINDINGS")),
    )
    check(
        "STUDIO-5 DEFINE textarea binds pack.define.text load path",
        "define_text" in studio and "pack.define" in studio,
        "define_bind=%s" % ("define_text" in studio),
    )
    check(
        "STUDIO-6 exported DeckStudio.mount for tab host",
        "DeckStudio" in studio
        and re.search(r"mount\s*:\s*mount", studio) is not None,
        "export=%s" % ("DeckStudio" in studio),
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
