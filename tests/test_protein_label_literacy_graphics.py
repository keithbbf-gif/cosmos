#!/usr/bin/env python3
"""Gate wired SVG figures for the protein label-literacy pack."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VERIFY = ROOT / "content" / "protein-supplements-label-literacy" / "qa" / "verify_graphics.py"


def test_verify_graphics_passes() -> None:
    proc = subprocess.run(
        [sys.executable, str(VERIFY)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr


if __name__ == "__main__":
    test_verify_graphics_passes()
    print("PASS")
