#!/usr/bin/env python3
"""CI hook: staged desk / hallway / entryway drafts stay valid."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "tools" / "check_desk_entryway_drafts.py"


def main() -> int:
    if not CHECKER.is_file():
        print(f"FAIL missing {CHECKER}")
        return 1
    proc = subprocess.run(
        [sys.executable, str(CHECKER)],
        cwd=ROOT,
        check=False,
    )
    return proc.returncode


if __name__ == "__main__":
    sys.exit(main())
