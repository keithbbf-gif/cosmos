#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Suite wrapper for cosmos_inflight.selftest().

Exists so the selftest clock (builds/selftest_clock) discovers the lease store
like any other gate. The checks live with the module; this only runs them.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "cosmos"))

from cosmos_inflight import selftest  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(selftest())
