"""Pack graphics validation for drawer-construction-history."""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATE = ROOT / "content" / "drawer-construction-history" / "scripts" / "validate_dch_graphics.py"


def test_dch_graphics_pack():
    proc = subprocess.run(
        [sys.executable, str(VALIDATE)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
