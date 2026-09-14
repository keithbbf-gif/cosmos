#!/usr/bin/env python3
"""Repo-root runner for builds/cdeck/test_kdash_working.py."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_TARGET = Path(__file__).resolve().parent / "builds" / "cdeck" / "test_kdash_working.py"
if __name__ == "__main__":
    spec = importlib.util.spec_from_file_location("test_kdash_working_cdeck", _TARGET)
    if spec is None or spec.loader is None:
        raise SystemExit(f"cannot load {_TARGET}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    raise SystemExit(mod.main())
