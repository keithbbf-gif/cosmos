#!/usr/bin/env py -3.14
"""profiles: Website GC MOTIF skins, Portfolio Studio, no auto-MOTIF."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cosmos"))

from cosmos_profiles import (  # noqa: E402
    PORTFOLIO_PRODUCT_IDS,
    PORTFOLIO_PRODUCTS_SCHEMA,
    PORTFOLIO_STUDIO_SCHEMA,
    _selftest,
    portfolio_projection,
    portfolio_studio_live_is_honest,
    snapshot,
)


def test_profiles_selftest():
    assert _selftest() == 0


def test_service_declares_profiles_routes():
    src = (ROOT / "cosmos" / "cosmos_service.py").read_text(encoding="utf-8")
    assert 'parsed.path == "/api/v1/profiles"' in src
    assert "profiles_save" in src
    assert "Does not start MOTIF" in src
    assert "Does not publish" in src
    assert 'ledger=getattr(kernel, "ledger", None)' in src


class TestPortfolioProjection(unittest.TestCase):
    def test_seven_canonical_ids_docs_order(self):
        self.assertEqual(
            list(PORTFOLIO_PRODUCT_IDS),
            ["ups", "forge", "crucible", "differentiator",
             "diligence", "docket", "website"],
        )

    def test_empty_root_is_unmeasured_not_zero(self):
        from cosmos_kernel import install
        from cosmos_paths import CosmosPaths

        td = Path(tempfile.mkdtemp(prefix="cosmos_pf_empty_"))
        root = install(td / "live", tree_id="spike-portfolio-empty")
        paths = CosmosPaths(root)
        snap = snapshot(paths, profile="website")
        ps = snap["portfolio_studio"]
        self.assertEqual(ps["schema"], PORTFOLIO_STUDIO_SCHEMA)
        self.assertTrue(portfolio_studio_live_is_honest(ps["live"]))
        pf = snap["portfolio"]
        self.assertEqual(pf["schema"], PORTFOLIO_PRODUCTS_SCHEMA)
        self.assertEqual(pf["n_products"], 7)
        for row in pf["products"]:
            self.assertIsNone(row["stage"]["n"])
            self.assertEqual(row["stage"]["kind"], "UNMEASURED")
            self.assertNotEqual(row["stage"]["n"], 0)
            self.assertIn("refuse_inference_after", row)

    def test_ledger_measurement_carries_refuse_watermark(self):
        from cosmos_kernel import Kernel, install
        from cosmos_paths import CosmosPaths

        td = Path(tempfile.mkdtemp(prefix="cosmos_pf_ledger_"))
        root = install(td / "live", tree_id="spike-portfolio-ledger")
        paths = CosmosPaths(root)
        k = Kernel(root, worker="test-portfolio")
        rec = k.ledger.append("MOTIF_STAGE", {
            "profile": "crucible", "stage": "critics", "stage_n": 6,
        })
        pf = portfolio_projection(paths, ledger=k.ledger)
        row = next(p for p in pf["products"] if p["id"] == "crucible")
        self.assertEqual(row["stage"]["kind"], "MEASURED")
        self.assertEqual(row["stage"]["n"], 6)
        self.assertEqual(row["stage"]["id"], "critics")
        self.assertEqual(row["refuse_inference_after"]["seq"], rec["seq"])
        self.assertEqual(row["refuse_inference_after"]["t"], rec["t"])
        # Sibling products stay non-invented.
        ups = next(p for p in pf["products"] if p["id"] == "ups")
        self.assertIn(ups["stage"]["kind"], ("UNMEASURED", "UNATTRIBUTED"))
        self.assertIsNone(ups["stage"]["n"])


if __name__ == "__main__":
    raise SystemExit(_selftest())
