#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""orthogonal porosity tensor: pair vectors, no invented scores."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cosmos"))

from cosmos_kernel import install  # noqa: E402
from cosmos_paths import CosmosPaths  # noqa: E402
from cosmos_porosity import _selftest, record_pair  # noqa: E402
from cosmos_portfolio_attribution import UNATTRIBUTED, read_tags  # noqa: E402


class TestPorosity(unittest.TestCase):
    def test_porosity_selftest(self):
        self.assertEqual(_selftest(), 0)

    def test_porosity_tags_when_profile_and_stage_are_canon(self):
        td = Path(tempfile.mkdtemp(prefix="ps06_por_"))
        root = install(td / "live", tree_id="ps06-por")
        paths = CosmosPaths(root)
        snap = record_pair(
            paths, "model-a", "model-b",
            axis="coding", disagree=True,
            profile="forge", stage="consensus1",
        )
        last = snap["last"]
        self.assertEqual(last.get("product"), "forge")
        self.assertEqual(last.get("stage"), "consensus1")
        self.assertEqual(read_tags(last)["attribution"], "TAGGED")

    def test_porosity_empty_stage_stays_unattributed(self):
        td = Path(tempfile.mkdtemp(prefix="ps06_por_u_"))
        root = install(td / "live", tree_id="ps06-por-u")
        paths = CosmosPaths(root)
        snap = record_pair(
            paths, "model-a", "model-b",
            axis="coding", disagree=False,
            profile="forge", stage="",
        )
        last = snap["last"]
        self.assertNotIn("product", last)
        self.assertEqual(read_tags(last)["attribution"], UNATTRIBUTED)

    def test_service_declares_porosity_routes(self):
        src = (ROOT / "cosmos" / "cosmos_service.py").read_text(encoding="utf-8")
        self.assertIn('parsed.path == "/api/v1/porosity"', src)
        self.assertIn("POST /api/v1/porosity", src)
        self.assertIn("GET never mkdir", src)
        self.assertIn("cosmos_porosity", src)
        self.assertIn("complement", src.lower())
        self.assertIn("tensors[agent][vs][axis]", src)
        self.assertIn('authority=d.get("authority")', src)
        self.assertIn('action=d.get("audit_action")', src)
        self.assertIn('agent_id=d.get("agent_id")', src)

    def test_forge_facilitate_hooks_porosity(self):
        src = (ROOT / "cosmos" / "cosmos_forge_bg.py").read_text(encoding="utf-8")
        self.assertIn("hook_trial", src)
        self.assertIn("cosmos_porosity", src)
        self.assertIn('authority="crew:forge"', src)
        self.assertIn('action="facilitate"', src)

    def test_crucible_and_runner_hook_porosity(self):
        cru = (ROOT / "cosmos" / "cosmos_crucible.py").read_text(encoding="utf-8")
        self.assertIn("hook_returns", cru)
        self.assertIn('authority="crew:crucible"', cru)
        critics = (ROOT / "cosmos" / "cosmos_crucible_critics.py").read_text(
            encoding="utf-8")
        self.assertIn("hook_returns", critics)
        run = (ROOT / "cosmos" / "cosmos_runner.py").read_text(encoding="utf-8")
        self.assertIn('cmd.startswith("crucible:round")', run)
        self.assertIn("spend_round", run)
        pool = (ROOT / "cosmos" / "cosmos_pool.py").read_text(encoding="utf-8")
        self.assertIn("runner.paths = paths", pool)


if __name__ == "__main__":
    unittest.main()
