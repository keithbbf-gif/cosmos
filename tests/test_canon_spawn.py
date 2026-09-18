#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest: CANON spawn layers. Isolated from the live tree.

3 VERIFY: missing role fills default CODER; concat CTX refuses;
grok argv refuses. Does not spawn grok.exe and does not write the live tree.
"""
from __future__ import annotations

import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
_root = _here.parent
sys.path.insert(0, str(_root))
sys.path.insert(0, str(_root / "cosmos"))

from cosmos_spawn import _selftest  # noqa: E402


def test_canon_spawn():
    assert _selftest() == 0


if __name__ == "__main__":
    sys.exit(_selftest())
