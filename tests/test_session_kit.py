#!/usr/bin/env py -3.14
"""session kit + backup fold: config only, never fire."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cosmos"))

from cosmos_backup_fold import _selftest as backup_selftest  # noqa: E402
from cosmos_session_kit import _selftest as kit_selftest  # noqa: E402


def test_session_kit():
    assert kit_selftest() == 0


def test_backup_fold():
    assert backup_selftest() == 0


def test_service_names_routes():
    src = (ROOT / "cosmos" / "cosmos_service.py").read_text(encoding="utf-8")
    assert 'parsed.path == "/api/v1/backup"' in src
    assert 'parsed.path == "/api/v1/session_kit"' in src
    assert "session_kit_save" in src


if __name__ == "__main__":
    raise SystemExit(kit_selftest() or backup_selftest())
