#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Repo-root entry: cDeck feature contract pins (delegates to builds/cdeck/)."""
from __future__ import annotations

import runpy
import sys
from pathlib import Path

_TARGET = Path(__file__).resolve().parent / "builds" / "cdeck" / "test_deck_features.py"

if __name__ == "__main__":
    if not _TARGET.is_file():
        print("missing %s" % _TARGET, file=sys.stderr)
        raise SystemExit(2)
    runpy.run_path(str(_TARGET), run_name="__main__")
