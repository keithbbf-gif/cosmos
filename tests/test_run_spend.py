#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Run spend: chars/4 until vendor usage, dollars from the Model Rater price table."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROC = subprocess.run(
    [sys.executable, str(ROOT / "cosmos" / "cosmos_run_spend.py"), "--selftest"],
    cwd=str(ROOT),
)
raise SystemExit(PROC.returncode)
