#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hermetic fence check for content/adaptogens-history-claims-guarded/."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LINT = ROOT / "content" / "adaptogens-history-claims-guarded" / "tools" / "lint_claims.py"


def main() -> int:
    if not LINT.is_file():
        print("FAIL missing lint_claims.py")
        return 1
    proc = subprocess.run(
        [sys.executable, str(LINT)],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    sys.stdout.write(proc.stdout)
    sys.stderr.write(proc.stderr)
    if proc.returncode != 0:
        print("FAIL adaptogens claims lint")
        return 1
    print("PASS adaptogens claims lint")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
