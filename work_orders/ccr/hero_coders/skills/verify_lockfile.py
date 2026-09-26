"""Skill: fail-closed lockfile / pin check before tests. Python tree, not npm."""
from __future__ import annotations

import json
import sys
from pathlib import Path


def verify_lockfile(lockfile_path: str) -> bool:
    p = Path(lockfile_path)
    if not p.is_file():
        sys.stderr.write(f"Lockfile missing: {p}\n")
        return False
    try:
        if p.suffix == ".json":
            json.loads(p.read_text(encoding="utf-8"))
        else:
            text = p.read_text(encoding="utf-8")
            if not text.strip():
                sys.stderr.write("Lockfile empty\n")
                return False
        return True
    except Exception as e:
        sys.stderr.write(f"Lockfile integrity check failed: {e}\n")
        return False


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "requirements.txt"
    raise SystemExit(0 if verify_lockfile(target) else 1)
