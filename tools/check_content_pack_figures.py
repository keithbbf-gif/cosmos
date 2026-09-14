#!/usr/bin/env python3
"""Fail closed if any draft in the three IMAGE+SEO packs lacks a lead figure."""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PACKS = [
    REPO / "content/cbt-history-deep/drafts",
    REPO / "content/custom-furniture-rfq-sales/articles",
]
ACT = REPO / "content/act-mindfulness-therapy-history"

FIG = re.compile(r"<figure[\s>]", re.I)
ALT = re.compile(r'alt="[^"]{12,}"', re.I)
CAP = re.compile(r"<figcaption>.*?</figcaption>", re.S | re.I)


def check_dir(pattern: Path, files: list[Path]) -> list[str]:
    problems: list[str] = []
    for path in files:
        text = path.read_text(encoding="utf-8")
        if not FIG.search(text):
            problems.append(f"{path}: missing <figure>")
            continue
        block = text[text.find("<figure") : text.find("</figure>") + 10]
        if not ALT.search(block):
            problems.append(f"{path}: short or missing alt")
        if not CAP.search(block):
            problems.append(f"{path}: missing figcaption")
    return problems


def main() -> int:
    problems: list[str] = []
    for d in PACKS:
        problems.extend(check_dir(d, sorted(d.glob("*.md"))))
    problems.extend(check_dir(ACT, sorted(ACT.glob("stage-*/*.md"))))
    total = sum(len(list(d.glob("*.md"))) for d in PACKS) + len(list(ACT.glob("stage-*/*.md")))
    print(f"drafts checked: {total}")
    if problems:
        for p in problems:
            print(" -", p)
        return 1
    print("all packs carry lead figures with alt + caption")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
