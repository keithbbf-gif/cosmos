#!/usr/bin/env py -3.14
"""WOMB pick_pair: high-orth low-porosity under GAC. Never invents."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cosmos"))

from cosmos_womb import _selftest  # noqa: E402


def test_womb_selftest():
    assert _selftest() == 0


def test_service_declares_womb_seat_route():
    src = (ROOT / "cosmos" / "cosmos_service.py").read_text(encoding="utf-8")
    assert 'parsed.path == "/api/v1/womb/seat"' in src
    assert "GET /api/v1/womb/seat" in src
    assert "GET never mkdir" in src
    assert "cosmos_womb" in src
    assert "404 UNMEASURED" in src
    assert "does not rewrite math" in src


def test_porosity_t_formula_untouched():
    src = (ROOT / "cosmos" / "cosmos_porosity.py").read_text(encoding="utf-8")
    assert 'SCHEMA = "cosmos-porosity-tensor/5"' in src
    assert "signed = round((xor_r - cofail) * w, 6)" in src


if __name__ == "__main__":
    raise SystemExit(_selftest())
