#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cDeck extra-pane occupancy pins (string/substring gates on builds/cdeck/ui).

Run: py -3.14 builds/cdeck/test_kdash_working.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
UI = Path(__file__).resolve().parent / "ui"
RESULTS: list[tuple[str, bool, str]] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    RESULTS.append((label, bool(ok), detail[:240]))


def _read(*names: str) -> str:
    parts = []
    for n in names:
        p = UI / n
        if p.is_file():
            parts.append(p.read_text(encoding="utf-8", errors="replace"))
    return "\n".join(parts)


def main() -> int:
    skit = _read("deck_session_kit.js")
    more = _read("deck_more.html", "index.html")
    tabs = _read("deck_tabs.js")
    blob = skit + "\n" + more + "\n" + tabs

    check(
        "SESSIONS: Open Sessions suite panes + leftover strip/DOI named",
        "Open Sessions suite" in skit
        and all(v in skit for v in (
            "scan", "load", "convert", "diff", "check", "anonymize", "crash-recover"))
        and "leftover strip" in skit
        and "DOI named" in skit
        and "session-suite-pane" in skit,
        "deck_session_kit.js",
    )

    check(
        "SESSIONS: COS panes + autosave 5/10/20/30 + auto-resession triggers",
        all(c in skit for c in ("rold", "tidyup", "tu2", "bu"))
        and all(str(m) in skit for m in (5, 10, 20, 30))
        and "auto-resession" in skit
        and "on_compaction" in skit
        and "on_token_count" in skit
        and "context_tokens" in skit
        and "/api/v1/session_kit" in skit,
        "session kit pane",
    )

    check(
        "SESSIONS: suite verbs are CLI, no GET /api/v1/session_tools poll",
        "session_tools.py" in skit
        and "POST /api/v1/session_tools" in skit
        and "no GET /api/v1/session_tools poll" in skit
        and 'apiGet("/api/v1/session_tools' not in skit
        and 'apiGet("/api/v1/session_tools' not in blob
        and not re.search(
            r"setInterval\s*\([^)]*session_tools", skit, re.I),
        "CLI POST only",
    )

    check(
        "SESSIONS: suite POST collects verb path args (not verb-only)",
        "SUITE_FIELDS" in skit
        and "session-suite-form" in skit
        and "bodyFromSuiteForm" in skit
        and 'apiPost("/api/v1/session_tools", { verb: verb })' not in skit,
        "session_tools verb args",
    )

    appjs = _read("app.js")
    check(
        "SESSIONS: Recents GET + OPENED card + explicit empty (app.js)",
        "paintRecentsTab" in appjs
        and 'apiGet("/api/v1/recents")' in appjs
        and "recents-opened-card" in appjs
        and "OPENED" in appjs
        and "explicit-empty" in appjs
        and "#nav-session-list" not in appjs,
        "recents tab",
    )

    check(
        "SESSIONS: ROLLED timeline when Core serves /api/v1/rolled",
        'apiGet("/api/v1/rolled")' in skit
        and "rolled-event/1" in skit
        and "ROLLED.md not present" in skit
        and "paintRolledTimeline" in skit,
        "rolled timeline",
    )

    failed = [r for r in RESULTS if not r[1]]
    for label, ok, detail in RESULTS:
        print("  %s  %s%s" % ("PASS" if ok else "FAIL", label,
                              (" — " + detail) if detail and not ok else ""))
    print("%d/%d pass" % (len(RESULTS) - len(failed), len(RESULTS)))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
