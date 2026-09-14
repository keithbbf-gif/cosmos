#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Repo-root runner for cDeck FEATURE_PROBE static gate.

Run:  py -3.14 test_deck_features.py
"""
from __future__ import annotations

import runpy
import sys
from pathlib import Path

TARGET = Path(__file__).resolve().parent / "builds" / "cdeck" / "test_deck_features.py"

if __name__ == "__main__":
    if not TARGET.is_file():
        print(f"FAIL  missing {TARGET}")
        raise SystemExit(1)
    sys.path.insert(0, str(TARGET.parent))
    raise SystemExit(runpy.run_path(str(TARGET), run_name="__main__") or 0)
