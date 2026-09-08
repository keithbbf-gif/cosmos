#!/usr/bin/env py -3.14
"""Tools kit: COSMOS components + local callables + other. GET only."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cosmos"))

from cosmos_tools_kit import _selftest as kit_selftest  # noqa: E402


def test_tools_kit_fold():
    assert kit_selftest() == 0


def test_service_names_tools_kit():
    src = (ROOT / "cosmos" / "cosmos_service.py").read_text(encoding="utf-8")
    assert 'parsed.path == "/api/v1/tools_kit"' in src
    assert "tools_kit_snapshot" in src
    assert "tools_kit_save" not in src


if __name__ == "__main__":
    raise SystemExit(kit_selftest())
