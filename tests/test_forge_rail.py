#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest: github-forge + gitlab-forge satellite. Fake CLI. No live vendor."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "cosmos"))

from cosmos_forge_rail import _selftest  # noqa: E402


def test_forge_rail():
    assert _selftest() == 0


if __name__ == "__main__":
    sys.exit(_selftest())
