#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest: GitHub SGH drop ingest clock. Isolated from the live tree.

Proves: valid drop files call drop_order; README and non-json skipped;
duplicate sha skipped; comma Context source split; colon filename sanitized;
PAUSE idle. Fake list/fetch — no network, no live-tree writes.
Does not invoke the work-order runner or any agent rail.
"""
from __future__ import annotations

import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
_root = _here.parent
sys.path.insert(0, str(_root))
sys.path.insert(0, str(_root / "cosmos"))
_repo_cosmos = _root.parent.parent / "cosmos"
if _repo_cosmos.is_dir():
    sys.path.append(str(_repo_cosmos))

from cosmos_sgh_drop_ingest import _selftest  # noqa: E402


def test_sgh_drop_ingest():
    assert _selftest() == 0


if __name__ == "__main__":
    sys.exit(_selftest())
