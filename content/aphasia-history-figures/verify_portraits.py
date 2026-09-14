#!/usr/bin/env python3
"""Fail if a cleared portrait raster lacks RIGHTS.md or PORTRAIT_SOURCES row."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LEDGER = ROOT / "PORTRAIT_SOURCES.md"
PORTRAITS = ROOT / "assets" / "portraits"
FILE_RE = re.compile(r"`(assets/portraits/[^`]+\.jpg)`")
CLEARED_RE = re.compile(r"\|\s*yes\s*\|\s*$")


def main() -> int:
    text = LEDGER.read_text(encoding="utf-8")
    cleared: set[str] = set()
    for line in text.splitlines():
        if not line.startswith("|") or "portrait_id" in line or "---" in line:
            continue
        if not CLEARED_RE.search(line):
            continue
        m = FILE_RE.search(line)
        if m:
            cleared.add(m.group(1))
    errors: list[str] = []
    for rel in sorted(cleared):
        path = ROOT / rel
        rights = PORTRAITS / f"{Path(rel).stem}.RIGHTS.md"
        if not path.is_file():
            errors.append(f"cleared ledger path missing: {rel}")
        if not rights.is_file():
            errors.append(f"missing RIGHTS.md for {rel}")
    for path in PORTRAITS.glob("*.jpg"):
        rel = f"assets/portraits/{path.name}"
        rights = path.with_suffix(".RIGHTS.md")
        if rel not in cleared:
            errors.append(f"raster on disk not cleared in ledger: {rel}")
        if not rights.is_file():
            errors.append(f"missing RIGHTS.md for {rel}")
    print(f"cleared={len(cleared)} rasters={len(list(PORTRAITS.glob('*.jpg')))}")
    if errors:
        print("FAIL")
        for e in errors:
            print(" ", e)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
