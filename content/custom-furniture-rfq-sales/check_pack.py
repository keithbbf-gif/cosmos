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
DISCLAIMER = "not a quote, not a contract, and not legal advice"
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
    r"Whether you’re",
    r"rapidly evolving",
    r"It's important to note",
    r"It’s important to note",
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
    r"the key takeaway",
    r"let's dive in",
    r"let’s dive in",
    r"at the end of the day",
    r"shop now",
    r"buy now",
    r"add to cart",
    r"limited time",
    r"act now",
    r"don't miss out",
    r"don’t miss out",
    r"call today for a free",
    r"book your consult",
    r"investment piece",
)
BRAND = (r"Bradley Brand Furniture", r"ElitElixir", r"Unilever")


def body_words(text: str) -> int:
    body = text.split("---", 2)[-1] if text.count("---") >= 2 else text
    return len(re.findall(r"\b[\w']+\b", body))


def main() -> int:
    arts = sorted(ART.glob("*.md"))
    issues: list[str] = []
    words_total = 0
    print(f"articles={len(arts)} (need >= 40)")
    if len(arts) < 40:
        issues.append(f"count {len(arts)} < 40")
    for path in arts:
        text = path.read_text(encoding="utf-8")
        words = body_words(text)
        words_total += words
        print(f"  {words:5d}  {path.name}")
        if words < 600:
            issues.append(f"{path.name}: short body ({words} < 600)")
        for key in REQUIRED_FM:
            if key not in text:
                issues.append(f"{path.name}: missing {key}")
        if DISCLAIMER.lower() not in text.lower():
            issues.append(f"{path.name}: missing educational disclaimer")
        body = text.split("---", 2)[-1] if text.count("---") >= 2 else text
        for pat in BANS:
            if re.search(pat, body, re.I):
                issues.append(f"{path.name}: style ban {pat}")
        for pat in BRAND:
            if re.search(pat, body):
                issues.append(f"{path.name}: brand {pat}")
    print(f"words_total={words_total}")
    print(f"issues={len(issues)}")
    for item in issues:
        print(f"FAIL {item}")
    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
