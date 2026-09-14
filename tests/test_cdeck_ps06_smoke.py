#!/usr/bin/env python3
"""PS-06 smoke pins (full cDeck lives in builds/cdeck gitlink submodule)."""
from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COSMOS = ROOT / "cosmos"


class TestCdeckPs06Smoke(unittest.TestCase):
    def test_attribution_wiring(self):
        assert (COSMOS / "cosmos_portfolio_attribution.py").is_file()
        spend = (COSMOS / "cosmos_spend.py").read_text(encoding="utf-8")
        assert "audit_by_product" in spend
        ops = (COSMOS / "cosmos_runs_ops.py").read_text(encoding="utf-8")
        assert "by_product" in ops
        svc = (COSMOS / "cosmos_service.py").read_text(encoding="utf-8")
        assert 'product=d.get("product")' in svc


if __name__ == "__main__":
    unittest.main()
