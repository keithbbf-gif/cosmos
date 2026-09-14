"""Image embed gates for content/custom-furniture-rfq-sales."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_validate_images_passes() -> None:
    root = Path(__file__).resolve().parents[1] / "content" / "custom-furniture-rfq-sales"
    script = root / "validate_images.py"
    proc = subprocess.run(
        [sys.executable, str(script)],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr


def test_check_pack_passes() -> None:
    root = Path(__file__).resolve().parents[1] / "content" / "custom-furniture-rfq-sales"
    proc = subprocess.run(
        [sys.executable, str(root / "check_pack.py")],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
