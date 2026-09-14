#!/usr/bin/env python3
"""Fail if a raster in the four packs is missing from its source ledger."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKS = [
    (
        ROOT / "content/ai-history-retrospective",
        ROOT / "content/ai-history-retrospective/PORTRAIT_SOURCES.md",
        (".jpg", ".jpeg", ".png", ".gif"),
    ),
    (
        ROOT / "content/slpwow-speech-pathology-history",
        ROOT / "content/slpwow-speech-pathology-history/PORTRAIT_SOURCES.md",
        (".jpg", ".jpeg", ".png", ".gif"),
    ),
    (
        ROOT / "content/wowtherapies-therapy-history",
        ROOT / "content/wowtherapies-therapy-history/PORTRAIT_SOURCES.md",
        (".jpg", ".jpeg", ".png", ".gif"),
    ),
    (
        ROOT / "content/fig-history-ancient-to-today",
        ROOT / "content/fig-history-ancient-to-today/IMAGE_SOURCES.md",
        (".jpg", ".jpeg", ".png", ".gif"),
    ),
]
ROW_RE = re.compile(
    r"`(assets/[-./A-Za-z0-9_]+\.(?:jpg|jpeg|png|gif|svg))`"
)


def main() -> int:
    errors: list[str] = []
    listed = 0
    rasters = 0
    placeholders = 0
    for pack, ledger, suffixes in PACKS:
        text = ledger.read_text(encoding="utf-8")
        mentioned = set(ROW_RE.findall(text))
        listed += len(mentioned)
        for path in pack.rglob("*"):
            if not path.is_file():
                continue
            rel = path.relative_to(pack).as_posix()
            if path.suffix.lower() == ".svg" and path.name.endswith(".placeholder.svg"):
                placeholders += 1
                if rel not in mentioned:
                    errors.append(f"placeholder not in ledger: {rel}")
                continue
            if path.suffix.lower() not in suffixes:
                continue
            rasters += 1
            if rel not in mentioned:
                errors.append(f"raster not in ledger: {rel}")
        for rel in mentioned:
            if not (pack / rel).is_file():
                errors.append(f"ledger path missing on disk: {rel} ({ledger.name})")
    print(f"ledgers_rows={listed} rasters={rasters} placeholders={placeholders}")
    if errors:
        print("FAIL")
        for e in errors:
            print(" ", e)
        return 1
    print("OK every raster and placeholder is in a source ledger")
    return 0


if __name__ == "__main__":
    sys.exit(main())
