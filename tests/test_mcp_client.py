#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest: COSMOS MCP client. Fake stdio. No child process, no network."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "cosmos"))

from cosmos_mcp_client import _selftest  # noqa: E402


def test_mcp_client():
    assert _selftest() == 0


if __name__ == "__main__":
    sys.exit(_selftest())
