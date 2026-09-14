#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest: gem-free satellite. Fake HTTP. No live vendor, no authority ledger."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "cosmos"))

from cosmos_gem_free_rail import _selftest  # noqa: E402


def test_gem_free_rail():
    assert _selftest() == 0


if __name__ == "__main__":
    sys.exit(_selftest())
