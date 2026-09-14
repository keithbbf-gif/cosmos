#!/usr/bin/env python3
"""Inventory + voice/claims gates for this pack. Not a publisher."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ART = ROOT / "articles"

REQUIRED_FM = (
    "title:",
    "slug:",
    "meta_description:",
    "tags:",
    "era_focus:",
    "citations:",
    "status: draft",
    "voice_check: human",
)
DSHEA = "not intended to diagnose"
BANS = (
    r"\bdelve\b",
    r"\brobust\b",
    r"\bleverage\b",
    r"\bunlock\b",
    r"cutting-edge",
    r"game-chang",
    r"In conclusion",
    r"\bFurthermore\b",
    r"\bMoreover\b",
    r"Whether you're",
    r"rapidly evolving",
    r"It's important to note",
    r"\bnavigate\b",
    r"tapestry",
    r"plethora",
    r"\butilize\b",
    r"\bharness\b",
    r"elevate your",
    r"the future of",
    r"at the forefront",
    r"holistic approach",
    r"\bempower\b",
    r"in this article we will",
)
BRAND = (r"ElitElixir", r"Unilever")


def main() -> int:
    arts = sorted(ART.glob("*.md"))
    issues: list[str] = []
    words_total = 0
    print(f"articles={len(arts)} (need >= 40)")
    if len(arts) < 40:
        issues.append(f"count {len(arts)} < 40")
    for path in arts:
        text = path.read_text(encoding="utf-8")
        words = len(re.findall(r"\b[\w']+\b", text))
        words_total += words
        print(f"  {words:5d}  {path.name}")
        for key in REQUIRED_FM:
            if key not in text:
                issues.append(f"{path.name}: missing {key}")
        if DSHEA.lower() not in text.lower():
            issues.append(f"{path.name}: missing DSHEA sentence")
        body = text.split("---", 2)[-1] if text.count("---") >= 2 else text
        for pat in BANS:
            if re.search(pat, body, re.I):
                issues.append(f"{path.name}: style ban {pat}")
        for pat in BRAND:
            if re.search(pat, text):
                issues.append(f"{path.name}: brand {pat}")
    print(f"words_total={words_total}")
    print(f"issues={len(issues)}")
    for item in issues:
        print(f"FAIL {item}")
    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
