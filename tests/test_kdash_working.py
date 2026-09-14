#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cDeck Sessions panel — three working-contract checks.

SESSIONS: Open Sessions suite panes + leftover strip/DOI named
SESSIONS: COS panes + autosave 5/10/20/30 + auto-resession triggers
SESSIONS: suite verbs are CLI, no GET /api/v1/session_tools poll

These run without a live COSMOS root (no tempdir, no network).
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cosmos"))

RESULTS: list[tuple[str, bool, str]] = []


def check(label: str, fn) -> None:
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:  # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


def main() -> int:
    # ── 1. Open Sessions panes + leftover verbs named ──────────────────────
    from cosmos_session_tools_kit import (  # noqa: E402
        PANES, SUITE_VERBS, UNMEASURED_VERBS, snapshot,
    )
    snap = snapshot(None)
    check(
        "SESSIONS: Open Sessions suite panes + leftover strip/DOI named",
        lambda: (
            any(p["id"] == "open_sessions" for p in snap["panes"])
            and any(p["id"] == "suite" for p in snap["panes"])
            and "strip" in snap["verbs"]
            and "doi" in snap["verbs"]
            and "strip" in snap["unmeasured"]
            and "doi" in snap["unmeasured"]
        ),
    )

    # ── 2. COS panes + autosave catalog + resession triggers ───────────────
    from cosmos_session_kit import (  # noqa: E402
        AUTOSAVE_MIN, COS_PANES, COS_IDS, default_kit,
    )
    kit = default_kit()
    check(
        "SESSIONS: COS panes + autosave 5/10/20/30 + auto-resession triggers",
        lambda: (
            # four named COS panes
            set(COS_IDS) == {"rold", "tidyup", "tu2", "bu"}
            # autosave choices are exactly 5 / 10 / 20 / 30
            and tuple(AUTOSAVE_MIN) == (5, 10, 20, 30)
            and kit["autosave_catalog"] == [5, 10, 20, 30]
            # resession triggers present
            and "on_compaction" in kit["resession"]
            and "on_token_count" in kit["resession"]
            and kit["resession"]["on_compaction"] is True
            and kit["resession"]["on_token_count"] is True
        ),
    )

    # ── 3. Suite verbs are CLI; GET /api/v1/session_tools is not a poll ────
    cli_src = (ROOT / "builds" / "session-tools" / "session_tools.py").read_text(
        encoding="utf-8"
    )
    svc_src = (ROOT / "cosmos" / "cosmos_service.py").read_text(encoding="utf-8")
    check(
        "SESSIONS: suite verbs are CLI, no GET /api/v1/session_tools poll",
        lambda: (
            # CLI has the canonical verb subparsers
            'sub.add_parser("scan")' in cli_src
            and 'sub.add_parser("convert")' in cli_src
            and 'sub.add_parser("check")' in cli_src
            # service GET uses snapshot(), not a polling loop
            and 'snapshot as session_tools_snapshot' in svc_src
            # snapshot note explicitly says no GET poll
            and "no GET poll" in snap["note"]
            # strip/doi are NOT in the CLI subparsers (they are future/UNMEASURED)
            and 'sub.add_parser("strip")' not in cli_src
            and 'sub.add_parser("doi")' not in cli_src
        ),
    )

    bad = [(lbl, err) for lbl, ok, err in RESULTS if not ok]
    for label, ok, err in RESULTS:
        print("  %s  %s%s" % (
            "OK  " if ok else "FAIL",
            label,
            (f"  [{err}]") if err else "",
        ))
    print("SELFTEST %s - %d checks (cDeck Sessions)"
          % ("PASS" if not bad else "FAIL", len(RESULTS)))
    return 0 if not bad else 1


def test_sessions_open_panes():
    """Open Sessions suite panes + leftover strip/DOI named."""
    RESULTS.clear()
    rc = main()
    label = "SESSIONS: Open Sessions suite panes + leftover strip/DOI named"
    row = next((r for r in RESULTS if r[0] == label), None)
    assert row is not None, f"check {label!r} not found"
    assert row[1], f"FAIL  {label}  [{row[2]}]"


def test_sessions_cos_panes():
    """COS panes + autosave 5/10/20/30 + auto-resession triggers."""
    RESULTS.clear()
    rc = main()
    label = "SESSIONS: COS panes + autosave 5/10/20/30 + auto-resession triggers"
    row = next((r for r in RESULTS if r[0] == label), None)
    assert row is not None, f"check {label!r} not found"
    assert row[1], f"FAIL  {label}  [{row[2]}]"


def test_sessions_suite_verbs_cli():
    """Suite verbs are CLI, no GET /api/v1/session_tools poll."""
    RESULTS.clear()
    rc = main()
    label = "SESSIONS: suite verbs are CLI, no GET /api/v1/session_tools poll"
    row = next((r for r in RESULTS if r[0] == label), None)
    assert row is not None, f"check {label!r} not found"
    assert row[1], f"FAIL  {label}  [{row[2]}]"


if __name__ == "__main__":
    raise SystemExit(main())
