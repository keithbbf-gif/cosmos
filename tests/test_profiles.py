#!/usr/bin/env py -3.14
"""profiles: Website GC MOTIF skins, IMPLEMENT dest, no auto-MOTIF."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cosmos"))

from cosmos_profiles import _selftest  # noqa: E402
import unittest  # noqa: E402


class TestProfiles(unittest.TestCase):
    def test_profiles_selftest(self):
        self.assertEqual(_selftest(), 0)

    def test_service_declares_profiles_routes(self):
        src = (ROOT / "cosmos" / "cosmos_service.py").read_text(encoding="utf-8")
        self.assertIn('parsed.path == "/api/v1/profiles"', src)
        self.assertIn("profiles_save", src)
        self.assertIn("Does not start MOTIF", src)
        self.assertIn("Does not publish", src)
        self.assertIn("kernel=kernel", src)
        prof = (ROOT / "cosmos" / "cosmos_profiles.py").read_text(encoding="utf-8")
        self.assertIn("PROFILE_MOTIF_STAGE_TRANSITION", prof)


if __name__ == "__main__":
    raise SystemExit(unittest.main())
