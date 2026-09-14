#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Repo-root runner for builds/cdeck/test_deck_features.py (py -3.14 test_deck_features.py)."""
from __future__ import annotations

import sys
from pathlib import Path

TARGET = Path(__file__).resolve().parent / "builds" / "cdeck" / "test_deck_features.py"
if __name__ == "__main__":
    import subprocess
    raise SystemExit(subprocess.call([sys.executable, str(TARGET)] + sys.argv[1:]))
