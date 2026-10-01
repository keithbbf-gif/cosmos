#!/usr/bin/env py -3.14
"""profiles: Spidercaster MOTIF skins, IMPLEMENT dest, no auto-MOTIF."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cosmos"))

from cosmos_profiles import _selftest  # noqa: E402


def test_profiles_selftest():
    assert _selftest() == 0


def test_service_declares_profiles_routes():
    src = (ROOT / "cosmos" / "cosmos_service.py").read_text(encoding="utf-8")
    assert 'parsed.path == "/api/v1/profiles"' in src
    assert "profiles_save" in src
    assert "Does not start MOTIF" in src
    assert "Does not publish" in src


if __name__ == "__main__":
    raise SystemExit(_selftest())
