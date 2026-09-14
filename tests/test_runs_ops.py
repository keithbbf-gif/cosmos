#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Runs ops fold: GET only, never invents tokens or vendor PR lists."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cosmos"))

from cosmos_runs_ops import _selftest as runs_ops_selftest  # noqa: E402


class TestRunsOps(unittest.TestCase):
    def test_runs_ops_fold(self):
        self.assertEqual(runs_ops_selftest(), 0)

    def test_runs_ops_exposes_product_spend_fold(self):
        src = (ROOT / "cosmos" / "cosmos_runs_ops.py").read_text(encoding="utf-8")
        self.assertIn("by_product", src)
        self.assertIn("audit_by_product", src)
        self.assertIn("scheduler_jobs", src)
        self.assertIn("UNATTRIBUTED", src)

    def test_service_names_runs_ops(self):
        src = (ROOT / "cosmos" / "cosmos_service.py").read_text(encoding="utf-8")
        self.assertIn('parsed.path == "/api/v1/runs_ops"', src)
        self.assertIn("runs_ops_snapshot", src)
        self.assertIn("GET /api/v1/runs_ops", src)
        self.assertNotIn("runs_ops_save", src)


if __name__ == "__main__":
    unittest.main()
