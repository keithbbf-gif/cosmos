#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest: ledger head-cache + mac_v:2 (Opus review #5+#6).

Closes CHANGES.md §4 row `ccr/ledger-head-cache-mac2`. The module's own
`--selftest` is the operator verb; this file is the suite wrapper so the
selftest clock discovers it.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "cosmos"))
from cosmos_ledger import _selftest  # noqa: E402


def test_ledger_mac2():
    assert _selftest() == 0


if __name__ == "__main__":
    sys.exit(_selftest())
