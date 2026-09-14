#!/usr/bin/env py -3.14
"""profiles: Website GC MOTIF skins, IMPLEMENT dest, no auto-MOTIF."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cosmos"))

from cosmos_profiles import (  # noqa: E402
    MOTIF_STAGES,
    TRANSITION_EVENT,
    _selftest,
    motif_transition_edges,
    transition_contract,
)


class ProfilesTests(unittest.TestCase):
    def test_profiles_selftest(self):
        self.assertEqual(_selftest(), 0)

    def test_service_declares_profiles_routes(self):
        src = (ROOT / "cosmos" / "cosmos_service.py").read_text(encoding="utf-8")
        self.assertIn('parsed.path == "/api/v1/profiles"', src)
        self.assertIn("profiles_save", src)
        self.assertIn("Does not start MOTIF", src)
        self.assertIn("Does not publish", src)
        self.assertIn("kernel=kernel", src)
        self.assertIn("action=transition", src)

    def test_transition_catalog_is_nine_adjacent_edges(self):
        edges = motif_transition_edges()
        self.assertEqual(len(edges), len(MOTIF_STAGES))
        self.assertEqual(edges[0]["id"], "define_to_research")
        self.assertEqual(edges[-1]["id"], "iterate_to_define")
        self.assertTrue(all(e["requires_keith"] for e in edges))
        c = transition_contract()
        self.assertEqual(c["event"], TRANSITION_EVENT)
        self.assertEqual(c["allowed_edges"], edges)


if __name__ == "__main__":
    raise SystemExit(_selftest())
