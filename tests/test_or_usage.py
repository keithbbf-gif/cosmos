#!/usr/bin/env py -3.14
"""OpenRouter usage accounting: native tokens/cost, no invented scores."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cosmos"))

from cosmos_openrouter_rail import _selftest  # noqa: E402


def test_openrouter_usage_selftest():
    assert _selftest() == 0


def test_service_declares_usage_routes():
    src = (ROOT / "cosmos" / "cosmos_service.py").read_text(encoding="utf-8")
    assert 'parsed.path == "/api/v1/usage"' in src
    assert "POST /api/v1/usage" in src
    assert "usage.include" in src
    assert "cosmos_openrouter_rail" in src


if __name__ == "__main__":
    raise SystemExit(_selftest())
