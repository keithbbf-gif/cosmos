#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest: gdx-drive satellite. Injected about.get. No live vendor, no authority."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "cosmos"))

from cosmos_gdx_drive_rail import _selftest  # noqa: E402


def test_gdx_drive_rail():
    assert _selftest() == 0


if __name__ == "__main__":
    sys.exit(_selftest())
