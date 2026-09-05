#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest: COSMOS Cursor Cloud Agents rail.

Isolated from the live runtime root and the live Cursor API. Fake HTTP.
Proves: probe is GET /v1/me; dispatch is opt-in POST /v1/agents; missing key
is UNREACHABLE; Dispatcher ledgers RAIL_DISPATCH/RAIL_RESULT at $0 marginal;
spec/probe files never bake the secret; --gate PASS quotes apiKeyName.
Does not POST a real Cloud Agent and does not write the authority ledger.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "cosmos"))

from cosmos_cursor_rail import _selftest, main as _unused_main  # noqa: F401


def test_cursor_rail():
    assert _selftest() == 0


if __name__ == "__main__":
    sys.exit(_selftest())
