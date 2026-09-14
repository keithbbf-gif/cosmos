#!/usr/bin/env python3
"""Fail if a cleared portrait raster lacks RIGHTS.md or PORTRAIT_SOURCES row."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LEDGER = ROOT / "PORTRAIT_SOURCES.md"
PORTRAITS = ROOT / "assets" / "portraits"
FILE_RE = re.compile(r"`(assets/portraits/[^`]+\.(?:jpg|JPG|png))`")


def row_cleared(line: str) -> bool:
    if not line.startswith("|"):
        return False
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    if not cells:
        return False
    last = cells[-1].lower()
    return last.startswith("yes")


def main() -> int:
    text = LEDGER.read_text(encoding="utf-8")
    cleared: set[str] = set()
    for line in text.splitlines():
        if "portrait_id" in line or line.startswith("| ---"):
            continue
        if not row_cleared(line):
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
    for path in PORTRAITS.glob("*"):
        if path.suffix.lower() not in {".jpg", ".jpeg", ".png"}:
            continue
        rel = f"assets/portraits/{path.name}"
        rights = path.with_suffix(".RIGHTS.md")
        if not rights.is_file():
            errors.append(f"missing RIGHTS.md for {rel}")
        if rel not in cleared:
            errors.append(f"raster on disk not cleared in ledger: {rel}")
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
