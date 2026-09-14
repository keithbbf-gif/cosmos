#!/usr/bin/env python3
"""QA for wave-2 pack + school caseload figure SEO passes."""
from __future__ import annotations

import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_wave2_check_pack() -> None:
    script = ROOT / "content" / "slpwow-slp-news-wave2" / "check_pack.py"
    ns = runpy.run_path(str(script))
    assert ns["main"]() == 0


def test_caseload_check_pack() -> None:
    script = ROOT / "content" / "slp-school-caseload-practice-news" / "check_pack.py"
    ns = runpy.run_path(str(script))
    assert ns["main"]() == 0
