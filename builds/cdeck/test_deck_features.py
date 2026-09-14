#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cDeck Profiles / Portfolio Studio static contract pins.

Run: cd builds/cdeck && py -3.14 test_deck_features.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
UI = HERE / "ui"
RESULTS: list[tuple[str, bool, str]] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    RESULTS.append((label, bool(ok), str(detail)[:400]))


def _read(name: str) -> str:
    p = UI / name
    return p.read_text(encoding="utf-8") if p.is_file() else ""


def _profiles_contract_via_core() -> tuple[bool, str]:
    sys.path.insert(0, str(REPO / "cosmos"))
    import tempfile

    from cosmos_kernel import install
    from cosmos_paths import CosmosPaths
    from cosmos_profiles import (
        portfolio_studio_live_is_honest,
        snapshot,
    )

    td = Path(tempfile.mkdtemp(prefix="cdeck_ps_contract_"))
    root = install(td / "live", tree_id="cdeck-ps-contract")
    paths = CosmosPaths(root)
    snap = snapshot(paths, profile="website")
    ps = snap.get("portfolio_studio") or {}
    ok = (
        snap.get("does_not_start_motif") is True
        and snap.get("does_not_publish") is True
        and len(snap.get("stages") or []) == 9
        and isinstance(snap.get("profiles"), list)
        and portfolio_studio_live_is_honest(ps.get("live") or {})
    )
    return ok, "legacy+live=%s" % ok


def main() -> int:
    profiles = _read("deck_profiles.js")

    check(
        "PROFILES-1 esc() on all user text in deck_profiles.js",
        "function esc(" in profiles
        and profiles.count(".replace(/&/g") >= 1,
        "esc=%s" % ("function esc(" in profiles),
    )
    check(
        "PROFILES-2 GET uses /api/v1/profiles (live Core route)",
        "/api/v1/profiles" in profiles and "apiGet" in profiles,
        "route=%s" % ("/api/v1/profiles" in profiles),
    )
    check(
        "PROFILES-3 POST save does not invent MOTIF start",
        "Does not start MOTIF" in profiles or "does not start MOTIF" in profiles.lower(),
        "save_copy=%s" % ("start MOTIF" in profiles),
    )
    check(
        "PROFILES-4 client does not paint fake queue heat (no studio-heat in profiles pane)",
        "studio-heat" not in profiles and "queue_word" not in profiles,
        "invented_heat=%s" % ("studio-heat" in profiles),
    )
    check(
        "PROFILES-5 legacy stages[] + engine from GET payload",
        "rec.stages" in profiles and "rec.engine" in profiles,
        "bind=%s" % ("rec.stages" in profiles),
    )

    ok_core, detail = _profiles_contract_via_core()
    check("PROFILES-6 Core portfolio_studio live UNMEASURED contract", ok_core, detail)

    failed = [r for r in RESULTS if not r[1]]
    for label, ok, detail in RESULTS:
        mark = "OK  " if ok else "FAIL"
        print("  %s  %s%s" % (mark, label, ("  [" + detail + "]") if detail and not ok else ""))
    passed = len(RESULTS) - len(failed)
    print("\n%d/%d passed" % (passed, len(RESULTS)))
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
