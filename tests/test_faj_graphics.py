"""Pack graphics validation for furniture-advanced-joinery."""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATE = ROOT / "content" / "furniture-advanced-joinery" / "scripts" / "validate_faj_graphics.py"


def test_faj_graphics_pack():
    proc = subprocess.run(
        [sys.executable, str(VALIDATE)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
