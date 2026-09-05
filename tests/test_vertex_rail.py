#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest: COSMOS Vertex Express rail. Fake HTTP. No live vendor, no key print."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "cosmos"))

from cosmos_vertex_rail import _selftest  # noqa: E402


def test_vertex_rail():
    assert _selftest() == 0


if __name__ == "__main__":
    sys.exit(_selftest())
