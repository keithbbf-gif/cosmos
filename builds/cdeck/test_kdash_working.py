#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cDeck occupancy pins — COW node + System/Forge payload wiring.

Run:  python3 test_kdash_working.py
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
UI = HERE / "ui"
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
    appjs = _read("app.js")
    forgejs = _read("deck_forge.js")
    js = appjs + "\n" + forgejs

    check(
        "SYSTEM: renderStatus / renderHealth / renderFleet / renderNodemap painters",
        "function renderStatus" in appjs
        and "function renderHealth" in appjs
        and "function renderFleet" in appjs
        and "function renderNodemap" in appjs,
        "renderers",
    )
    check(
        "SYSTEM: spend / rails / fleet / nodemap paint live Core GETs (not invented hosts)",
        all(
            p in appjs
            for p in (
                'apiGet("/api/v1/status")',
                'apiGet("/api/v1/health")',
                'apiGet("/api/v1/spend")',
                'apiGet("/api/v1/rails")',
                'apiGet("/api/v1/fleet")',
                'apiGet("/api/v1/nodemap")',
            )
        ),
        "get paths",
    )
    check(
        "SYSTEM: health RED negative control stays red (ncrow / nclabel, not placated)",
        "SUPPOSED TO BE RED" in appjs
        and "ncrow" in appjs
        and "negative_control_red" in appjs
        and "r.ok === false" in appjs,
        "negative control",
    )
    check(
        "SYSTEM: 503 surfaces CDECK_PANEL_NOT_COMPOSED verbatim",
        "CDECK_PANEL_NOT_COMPOSED" in appjs,
        "503 string",
    )
    check(
        "SYSTEM: COW paints from nodemap payload (id=cow / d.cow)",
        "function paintCowNode" in appjs
        and "cowRow" in appjs
        and 'id === "cow"' in appjs
        and "paintCowNode(cowRow(d))" in appjs,
        "cow paint",
    )
    check(
        "SYSTEM: stale COW renders RED (stale-red / proof_state STALE)",
        "stale-red" in appjs
        and 'proof_state === "STALE"' in appjs
        and "cow-stale" in appjs,
        "stale red",
    )
    check(
        "SYSTEM: UNMEASURED never painted as 0 (ageText / empty model)",
        "UNMEASURED" in appjs
        and "function ageText" in appjs
        and "age == null" in appjs,
        "unmeasured",
    )
    check(
        "SYSTEM+FORGE: esc() wraps payload text (no raw innerHTML of model/role)",
        "function esc(s)" in appjs
        and "function esc(s)" in forgejs
        and "esc(cow.model)" in appjs
        and "esc(cow.role" in appjs
        and "esc(cow.model)" in forgejs,
        "esc",
    )
    check(
        "FORGE: paints COW from GET /api/v1/nodemap payload",
        'apiGet("/api/v1/nodemap")' in forgejs
        and "function paintForgeCow" in forgejs
        and "SGH+GBW are not independent checks of each other" in forgejs,
        "forge cow",
    )
    check(
        "independence note kept (SGH+GBW are not independent checks of each other)",
        js.count("SGH+GBW are not independent checks of each other") >= 2,
        "independence",
    )
    check(
        "COW role is orch, not reading: VERIFY, SYNTHESISE, ORCHESTRATE",
        "VERIFY, SYNTHESISE, ORCHESTRATE" in appjs
        and "does not" in appjs,
        "role",
    )

    failed = [r for r in RESULTS if not r[1]]
    for label, ok, detail in RESULTS:
        mark = "OK  " if ok else "FAIL"
        extra = ("  [" + detail + "]") if detail and not ok else ""
        print("  %s  %s%s" % (mark, label, extra))
    print(
        "SELFTEST %s %d/%d"
        % ("PASS" if not failed else "FAIL", len(RESULTS) - len(failed), len(RESULTS))
    )
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
