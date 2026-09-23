#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""py_compile, ruff, mypy, and pytest record a row each before WOMBAT."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROC = subprocess.run(
    [sys.executable, str(ROOT / "cosmos" / "cosmos_code_checks.py"), "--selftest"],
    cwd=str(ROOT),
)
raise SystemExit(PROC.returncode)
