#!/usr/bin/env py -3.14
"""orthogonal porosity tensor: pair vectors, no invented scores."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cosmos"))

from cosmos_porosity import _selftest  # noqa: E402


def test_porosity_selftest():
    assert _selftest() == 0


def test_service_declares_porosity_routes():
    src = (ROOT / "cosmos" / "cosmos_service.py").read_text(encoding="utf-8")
    assert 'parsed.path == "/api/v1/porosity"' in src
    assert "POST /api/v1/porosity" in src
    assert "GET never mkdir" in src
    assert "cosmos_porosity" in src
    assert "complement" in src.lower()


def test_forge_facilitate_hooks_porosity():
    src = (ROOT / "cosmos" / "cosmos_forge_bg.py").read_text(encoding="utf-8")
    assert "hook_trial" in src
    assert "cosmos_porosity" in src


if __name__ == "__main__":
    raise SystemExit(_selftest())
