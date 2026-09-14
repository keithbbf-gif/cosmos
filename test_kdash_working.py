#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cDeck occupancy + Profiles pane pins (repo root).

Run:  py -3.14 test_kdash_working.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

UI = Path(__file__).resolve().parent / "builds" / "cdeck" / "ui"
RESULTS: list[tuple[str, bool, str]] = []


def check(label: str, fn) -> None:
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:  # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


def _read(*names: str) -> str:
    out = []
    for name in names:
        p = UI / name
        if p.is_file():
            out.append(p.read_text(encoding="utf-8"))
    return "\n".join(out)


def main() -> int:
    css = _read("header.css", "deck_more.css")
    html = _read("index.html", "deck_more.html")
    prof = _read("deck_profiles.js")
    blob = css + "\n" + html + "\n" + prof

    check(
        "WINDOW: cockpit grid splits tab shell and MESH with a vh floor",
        lambda: bool(re.search(r"#cdeck-cockpit\s*\{[^}]*height\s*:\s*100vh", css, re.S))
        and "#cdeck-more" in blob,
    )

    check(
        "TABS: tab rail scrolls inside the extra-pane shell",
        lambda: bool(re.search(r"\.tab-rail\s*\{[^}]*overflow-y\s*:\s*(auto|scroll)", css, re.S)),
    )

    check(
        "PANES: grid declares at least two columns for cockpit split",
        lambda: bool(re.search(r"grid-template-columns\s*:\s*(\S+\s+\S+)", css)),
    )

    for pid in (
        "forge", "crucible", "diligence", "docket", "ups", "differentiator", "website"
    ):
        check(
            f"PROFILES child page target pfPage-{pid} exists",
            lambda p=pid: f'id="pfPage-{p}"' in blob,
        )

    check(
        "PROFILES schematic paints MOTIF pipe from GET /api/v1/profiles",
        lambda: "pf-schematic" in prof
        and "pf-pipe" in prof
        and "/api/v1/profiles" in prof
        and "apiGet" in prof,
    )

    check(
        "PROFILE_SKINS chooser stub kept (data-stub=profile-skin)",
        lambda: "PROFILE_SKINS" in prof
        and 'data-stub="profile-skin"' in prof
        and "profile-skin-stub" in prof,
    )

    check(
        "Skin wallpapers reference ui/skins",
        lambda: "skins/forge-engineroom.jpg" in prof or "SKIN_WALLPAPERS" in prof,
    )

    check(
        "SAVE SETUP posts profiles only — never starts MOTIF",
        lambda: "SAVE SETUP" in prof
        and 'apiPost("/api/v1/profiles"' in prof
        and not re.search(r"/api/v1/motif", prof)
        and "does not start motif" in prof.lower(),
    )

    check(
        "Each child tab can paint via ensureProfilePage",
        lambda: "ensureProfilePage" in prof and "paintProfilePage" in prof,
    )

    passed = sum(1 for _, ok, _ in RESULTS if ok)
    total = len(RESULTS)
    for label, ok, detail in RESULTS:
        mark = "PASS" if ok else "FAIL"
        line = f"  {mark}  {label}"
        if detail and not ok:
            line += f"  — {detail}"
        print(line)
    print(f"\n{passed}/{total} passed")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
