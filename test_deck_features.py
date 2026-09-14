#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Repo-root entry for cDeck FEATURE_PROBE static gate (builds/cdeck/)."""
from __future__ import annotations

import runpy
import sys
from pathlib import Path

TARGET = Path(__file__).resolve().parent / "builds" / "cdeck" / "test_deck_features.py"

if __name__ == "__main__":
    if not TARGET.is_file():
        print(f"REFUSED: missing {TARGET}")
        raise SystemExit(2)
    raise SystemExit(runpy.run_path(str(TARGET), run_name="__main__") or 0)
