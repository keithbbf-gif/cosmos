#!/usr/bin/env python3
"""Verify wired figure img paths exist and SVG titles are present."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DRAFTS = ROOT / "drafts"
FIG = re.compile(
    r'<figure[^>]*>.*?<img\s+src="(\.\./assets/[^"]+)"',
    re.S,
)
TITLE = re.compile(r"<title[^>]*>", re.I)


def main() -> int:
    errors: list[str] = []
    wired = 0
    for path in sorted(DRAFTS.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        for rel in FIG.findall(text):
            wired += 1
            asset = (path.parent / rel).resolve()
            if not asset.is_file():
                errors.append(f"{path.name}: missing asset {rel}")
            else:
                body = asset.read_text(encoding="utf-8")
                if not TITLE.search(body):
                    errors.append(f"{asset.relative_to(ROOT)}: missing SVG <title>")
    index = (ROOT / "GRAPHICS_INDEX.md").read_text(encoding="utf-8")
    for line in index.splitlines():
        if line.strip().startswith("|") and "`assets/" in line:
            m = re.search(r"`(assets/[^`]+)`", line)
            if m and not (ROOT / m.group(1)).is_file():
                errors.append(f"GRAPHICS_INDEX lists missing file {m.group(1)}")
    print(f"figures_wired={wired}")
    if errors:
        print("FAIL")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
