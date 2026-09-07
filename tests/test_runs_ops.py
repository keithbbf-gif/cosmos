#!/usr/bin/env py -3.14
"""Runs ops fold: GET only, never invents tokens or vendor PR lists."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cosmos"))

from cosmos_runs_ops import _selftest as runs_ops_selftest  # noqa: E402


def test_runs_ops_fold():
    assert runs_ops_selftest() == 0


def test_service_names_runs_ops():
    src = (ROOT / "cosmos" / "cosmos_service.py").read_text(encoding="utf-8")
    assert 'parsed.path == "/api/v1/runs_ops"' in src
    assert "runs_ops_snapshot" in src
    assert "GET /api/v1/runs_ops" in src
    assert "runs_ops_save" not in src


if __name__ == "__main__":
    raise SystemExit(runs_ops_selftest())
