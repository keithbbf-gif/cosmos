#!/usr/bin/env py -3.14
"""P06 box$ vs token$ compare only after real obs.jsonl rows."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cosmos"))

from cosmos_p06_compare import _selftest  # noqa: E402


def test_p06_compare_selftest():
    assert _selftest() == 0


def test_service_declares_compare_action():
    src = (ROOT / "cosmos" / "cosmos_service.py").read_text(encoding="utf-8")
    assert 'act == "compare"' in src
    assert "compare_box_token" in src
