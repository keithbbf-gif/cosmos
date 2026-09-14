#!/usr/bin/env py -3.14
"""Surfaces kit: storage + channels + callable tools. GET only."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cosmos"))

from cosmos_surfaces_kit import _selftest as kit_selftest  # noqa: E402


class SurfacesKitTests(unittest.TestCase):
    def test_surfaces_kit_fold(self):
        self.assertEqual(kit_selftest(), 0)

    def test_service_names_surfaces_kit(self):
        src = (ROOT / "cosmos" / "cosmos_service.py").read_text(encoding="utf-8")
        self.assertIn('parsed.path == "/api/v1/surfaces_kit"', src)
        self.assertIn("surfaces_kit_snapshot", src)
        self.assertNotIn("surfaces_kit_save", src)

    def test_kit_storage_odx_unmeasured_without_dest(self):
        from cosmos_kernel import Kernel, install
        from cosmos_surfaces_kit import snapshot

        td = Path(tempfile.mkdtemp(prefix="cosmos_surfkit_odx_"))
        root = install(td / "live", tree_id="spike-surfkit-odx")
        k = Kernel(root, worker="core")
        rec = snapshot(k)
        rows = {r["id"]: r for r in rec["storage"]["rows"]}
        self.assertEqual(rec["storage"]["kind"], "OK")
        self.assertIn("ODX", rows)
        self.assertIsNone(rows["ODX"]["reachable"])
        self.assertIsNone(rows["ODX"]["free_gb"])
        self.assertIsNone(rows["ODX"]["age_s"])
        self.assertIsNone(rows["ODX"]["qualified"])
        self.assertEqual(rows["ODX"].get("write"), "cow")
        self.assertEqual(rows["ODX"].get("cop"), "metadata")


if __name__ == "__main__":
    raise SystemExit(unittest.main())
