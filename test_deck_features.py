#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Repo-root runner for cDeck feature contract pins (delegates to builds/cdeck)."""
from __future__ import annotations

import runpy
import sys
from pathlib import Path

TARGET = Path(__file__).resolve().parent / "builds" / "cdeck" / "test_deck_features.py"

if __name__ == "__main__":
    if not TARGET.is_file():
        print("REFUSING: missing %s" % TARGET, file=sys.stderr)
        raise SystemExit(1)
    runpy.run_path(str(TARGET), run_name="__main__")
