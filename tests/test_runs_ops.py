#!/usr/bin/env py -3.14
"""Runs ops fold: GET only, never invents tokens or vendor PR lists."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cosmos"))

from cosmos_runs_ops import _selftest as runs_ops_selftest  # noqa: E402


def test_runs_ops_fold():
    assert runs_ops_selftest() == 0


class TestRunsOps(unittest.TestCase):
    def test_runs_ops_fold(self):
        test_runs_ops_fold()

    def test_service_names_runs_ops(self):
        test_service_names_runs_ops()

    def test_portfolio_projection_wired(self):
        test_portfolio_projection_wired()


def test_service_names_runs_ops():
    src = (ROOT / "cosmos" / "cosmos_service.py").read_text(encoding="utf-8")
    assert 'parsed.path == "/api/v1/runs_ops"' in src
    assert "runs_ops_snapshot" in src
    assert "GET /api/v1/runs_ops" in src
    assert "runs_ops_save" not in src
    assert "portfolio" in src


def test_portfolio_projection_wired():
    profiles = (ROOT / "cosmos" / "cosmos_profiles.py").read_text(encoding="utf-8")
    runs = (ROOT / "cosmos" / "cosmos_runs_ops.py").read_text(encoding="utf-8")
    service = (ROOT / "cosmos" / "cosmos_service.py").read_text(encoding="utf-8")
    assert "PORTFOLIO_PRODUCT_IDS" in profiles
    assert "portfolio_projection" in profiles
    assert "refuse_inference_after" in profiles
    assert "UNATTRIBUTED" in profiles
    assert "portfolio_projection" in runs
    assert 'ledger=getattr(kernel, "ledger", None)' in service
    assert "portfolio_studio" in profiles


if __name__ == "__main__":
    raise SystemExit(runs_ops_selftest())
