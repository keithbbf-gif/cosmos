#!/usr/bin/env py -3.14
"""Runs ops fold: GET only, never invents tokens or vendor PR lists."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cosmos"))

from cosmos_runs_ops import _selftest as runs_ops_selftest  # noqa: E402


import unittest  # noqa: E402


class TestRunsOps(unittest.TestCase):
    def test_runs_ops_fold(self):
        assert runs_ops_selftest() == 0

    def test_runs_ops_exposes_product_spend_fold(self):
        src = (ROOT / "cosmos" / "cosmos_runs_ops.py").read_text(encoding="utf-8")
        assert "by_product" in src
        assert "audit_by_product" in src
        assert "scheduler_jobs" in src

    def test_service_names_runs_ops(self):
        src = (ROOT / "cosmos" / "cosmos_service.py").read_text(encoding="utf-8")
        assert 'parsed.path == "/api/v1/runs_ops"' in src
        assert "runs_ops_snapshot" in src
        assert "GET /api/v1/runs_ops" in src
        assert "runs_ops_save" not in src


if __name__ == "__main__":
    unittest.main()
