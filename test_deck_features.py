#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Static feature pins for Sessions tab (deck_session_kit.js + app.js recents).

Run: py -3.14 test_deck_features.py
"""
from __future__ import annotations

import sys
from pathlib import Path

UI = Path(__file__).resolve().parent / "builds" / "cdeck" / "ui"
RESULTS: list[tuple[str, bool, str]] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    RESULTS.append((label, bool(ok), detail[:240]))


def _read(name: str) -> str:
    p = UI / name
    if not p.is_file():
        raise FileNotFoundError(str(p))
    return p.read_text(encoding="utf-8", errors="replace")


def main() -> int:
    app = _read("app.js")
    skit = _read("deck_session_kit.js")

    check(
        "RECENTS: list uses GET /api/v1/recents (not nav-session-list)",
        'apiGet("/api/v1/recents")' in app
        and "paintRecentsTab" in app
        and "#nav-session-list" not in app,
    )
    check(
        "RECENTS: OPENED card paints kind OPENED transcript",
        "recents-opened-card" in app
        and 'rec.kind !== "OPENED"' in app
        and "open=1" in app
        and "paintCoworkRecents" in app
        and "recents-opened-head" in app,
    )
    check(
        "RECENTS: empty list is explicit (not silent blank)",
        "explicit-empty" in app and "recents-empty" in app,
    )
    check(
        "SESSION KIT: POST session_tools + session_kit paths wired",
        "/api/v1/session_kit" in skit and "/api/v1/session_tools" in skit,
    )
    check(
        "ROLLED: timeline fetch + explicit empty copy",
        'apiGet("/api/v1/rolled")' in skit
        and "COSMOS_ROLLED_FEED" in skit
        and "explicit empty" in skit
        and "parseRolledFeeds" in skit,
    )
    check(
        "ROLLED: no GET poll loop on session_tools or rolled",
        "setInterval" not in skit
        and not any(
            "setInterval" in line and "rolled" in line.lower()
            for line in skit.splitlines()
        ),
    )

    failed = [r for r in RESULTS if not r[1]]
    for label, ok, detail in RESULTS:
        print("  %s  %s%s" % ("PASS" if ok else "FAIL", label,
                              (" — " + detail) if detail and not ok else ""))
    print("%d/%d pass" % (len(RESULTS) - len(failed), len(RESULTS)))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
