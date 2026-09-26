#!/usr/bin/env py -3.14
"""SGH Voice loop fold: status only, never POST /voice."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cosmos"))

from cosmos_voice_loop import _selftest as voice_selftest


def test_voice_loop_fold():
    assert voice_selftest() == 0


def test_service_names_voice_loop():
    src = (ROOT / "cosmos" / "cosmos_service.py").read_text(encoding="utf-8")
    assert 'parsed.path == "/api/v1/voice_loop"' in src
    assert "voice_loop_snapshot" in src
    assert "voice_sop_save" in src
    assert "action=drop" in src
    assert "Does not POST /voice" in src


if __name__ == "__main__":
    raise SystemExit(voice_selftest())
