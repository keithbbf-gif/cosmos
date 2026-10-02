#!/usr/bin/env py -3.14
"""Resession close, ask ladder, autosave, and the ROLD pointer index."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cosmos"))

from cosmos_rold_index import _selftest as rold_selftest  # noqa: E402
from cosmos_session_kit import _selftest as kit_selftest  # noqa: E402
from cosmos_session_procedures import _selftest as proc_selftest  # noqa: E402


def test_rold_index():
    assert rold_selftest() == 0


def test_session_procedures():
    assert proc_selftest() == 0


def test_session_kit_ladder():
    assert kit_selftest() == 0


if __name__ == "__main__":
    raise SystemExit(rold_selftest() or proc_selftest() or kit_selftest())
