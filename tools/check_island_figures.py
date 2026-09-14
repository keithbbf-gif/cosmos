#!/usr/bin/env python3
"""Fail closed if any kitchen-island draft lacks a lead <figure> with alt + figcaption."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DRAFTS = ROOT / "content" / "kitchen-island-design-guide" / "drafts"

FIG = re.compile(r"<figure>.*?</figure>", re.S | re.I)
ALT = re.compile(r'alt="[^"]{12,}"', re.I)
CAP = re.compile(r"<figcaption>.*?</figcaption>", re.S | re.I)


def main() -> int:
    problems: list[str] = []
    files = sorted(DRAFTS.glob("*.md"))
    for path in files:
        text = path.read_text(encoding="utf-8")
        figs = FIG.findall(text)
        if len(figs) != 1:
            problems.append(f"{path.name}: expected 1 <figure>, got {len(figs)}")
            continue
        block = figs[0]
        if not ALT.search(block):
            problems.append(f"{path.name}: missing or short alt text")
        if not CAP.search(block):
            problems.append(f"{path.name}: missing figcaption")
    print(f"drafts checked: {len(files)}")
    if problems:
        for p in problems:
            print(" -", p)
        return 1
    print("all drafts carry lead figures with alt + caption")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
