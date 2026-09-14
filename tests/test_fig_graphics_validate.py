"""Tests for fig-history graphics validator."""

from pathlib import Path

import subprocess
import sys


def test_fig_graphics_validate_pack_ok():
    root = Path(__file__).resolve().parents[1]
    pack = root / "content" / "fig-history-ancient-to-today"
    script = root / "tools" / "fig_graphics_validate.py"
    proc = subprocess.run(
        [sys.executable, str(script), str(pack)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr + proc.stdout
