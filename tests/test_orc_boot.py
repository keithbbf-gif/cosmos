#!/usr/bin/env py -3.14
"""ORC BootUP inspect + recover. GET never mkdir."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cosmos"))

from cosmos_orc_boot import _selftest  # noqa: E402


def test_orc_boot_selftest():
    assert _selftest() == 0


def test_service_declares_orc_routes():
    src = (ROOT / "cosmos" / "cosmos_service.py").read_text(encoding="utf-8")
    assert 'parsed.path == "/api/v1/orc"' in src
    assert "POST /api/v1/orc" in src
    assert "GET never mkdir" in src
    assert "cosmos_orc_boot" in src


if __name__ == "__main__":
    raise SystemExit(_selftest())
