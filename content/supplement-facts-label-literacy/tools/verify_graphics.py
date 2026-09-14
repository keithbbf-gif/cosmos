#!/usr/bin/env python3
"""Fail closed if article figures reference missing assets."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = re.compile(r'src="([^"]+)"')


def main() -> int:
    missing: list[str] = []
    for md in (ROOT / "articles").glob("*.md"):
        text = md.read_text(encoding="utf-8")
        if "<figure" not in text:
            continue
        for src in SRC.findall(text):
            if src.startswith("http"):
                continue
            path = (md.parent / src).resolve()
            if not path.is_file():
                missing.append(f"{md.name}: {src}")
    if missing:
        print("Missing figure assets:", file=sys.stderr)
        for line in missing:
            print(" ", line, file=sys.stderr)
        return 1
    print("OK: all embedded figure paths resolve")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
