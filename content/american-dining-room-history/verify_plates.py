#!/usr/bin/env python3
"""Fail if a cleared plate raster lacks RIGHTS.md or PLATE_SOURCES row."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LEDGER = ROOT / "PLATE_SOURCES.md"
PLATES_DIR = ROOT / "plates"
DRAFTS = ROOT / "drafts"
SLUG_RE = re.compile(r"^\| `([^`]+)` \|")
FIGURE_RE = re.compile(r"<figure class=\"bbf-figure", re.I)


def ledger_slugs() -> set[str]:
    text = LEDGER.read_text(encoding="utf-8")
    slugs: set[str] = set()
    for line in text.splitlines():
        m = SLUG_RE.match(line)
        if m and "yes" in line:
            slugs.add(m.group(1))
    return slugs


def main() -> int:
    if not LEDGER.is_file():
        print("FAIL: missing PLATE_SOURCES.md — run furniture_plates_pass.py")
        return 1
    cleared = ledger_slugs()
    errors: list[str] = []
    for slug in sorted(cleared):
        folder = PLATES_DIR / slug
        rights = folder / "RIGHTS.md"
        rasters = list(folder.glob("plate.*"))
        if not rights.is_file():
            errors.append(f"missing RIGHTS.md for {slug}")
        if not rasters:
            errors.append(f"missing raster for {slug}")
        draft = DRAFTS / f"{slug}.md"
        if not draft.is_file():
            errors.append(f"missing draft {slug}.md")
        elif not FIGURE_RE.search(draft.read_text(encoding="utf-8")):
            errors.append(f"draft {slug}.md missing <figure> block")
    for folder in PLATES_DIR.iterdir():
        if not folder.is_dir():
            continue
        slug = folder.name
        if list(folder.glob("plate.*")) and slug not in cleared:
            errors.append(f"raster on disk not in ledger: {slug}")
    print(f"cleared={len(cleared)} plate_folders={len(list(PLATES_DIR.iterdir()))}")
    if errors:
        print("FAIL")
        for e in errors:
            print(" ", e)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
