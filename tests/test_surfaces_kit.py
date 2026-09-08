#!/usr/bin/env py -3.14
"""Surfaces kit: storage + channels + callable tools. GET only."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cosmos"))

from cosmos_surfaces_kit import _selftest as kit_selftest  # noqa: E402


def test_surfaces_kit_fold():
    assert kit_selftest() == 0


def test_service_names_surfaces_kit():
    src = (ROOT / "cosmos" / "cosmos_service.py").read_text(encoding="utf-8")
    assert 'parsed.path == "/api/v1/surfaces_kit"' in src
    assert "surfaces_kit_snapshot" in src
    assert "surfaces_kit_save" not in src


if __name__ == "__main__":
    raise SystemExit(kit_selftest())
