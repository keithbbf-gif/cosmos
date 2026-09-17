#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Focused tests for cosmos_packets (KEEP_PACKETS CAS fold)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cosmos"))

from cosmos_packets import _selftest  # noqa: E402


def test_packets_selftest():
    assert _selftest() == 0


if __name__ == "__main__":
    raise SystemExit(_selftest())
