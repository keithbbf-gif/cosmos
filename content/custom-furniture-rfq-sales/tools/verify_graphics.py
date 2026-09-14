#!/usr/bin/env python3
"""Fail closed if embedded figures reference missing assets."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = re.compile(r'src="([^"]+)"')


def main() -> int:
    missing: list[str] = []
    for md in ROOT.rglob("*.md"):
        if "tools" in md.parts:
            continue
        text = md.read_text(encoding="utf-8")
        if "<figure" not in text:
            continue
        for src in SRC.findall(text):
            if src.startswith("http"):
                continue
            path = (md.parent / src).resolve()
            if not path.is_file():
                missing.append(f"{md.relative_to(ROOT)}: {src}")
    if missing:
        for line in missing:
            print("MISSING", line)
        return 1
    print("OK: custom-furniture-rfq-sales figure paths resolve")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
