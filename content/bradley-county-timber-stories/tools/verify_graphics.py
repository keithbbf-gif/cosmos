#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = re.compile(r'src="([^"]+)"')


def main() -> int:
    missing = []
    for md in (ROOT / "drafts").glob("*.md"):
        text = md.read_text(encoding="utf-8")
        if "<figure" not in text:
            continue
        for src in SRC.findall(text):
            if src.startswith("http"):
                continue
            if not (md.parent / src).resolve().is_file():
                missing.append(f"{md.name}: {src}")
    if missing:
        for line in missing:
            print(line, file=sys.stderr)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
