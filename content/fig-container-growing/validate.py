#!/usr/bin/env python3
"""Structural check for the staged fig-container-growing draft set."""
from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
MIN_DRAFTS = 47
MIN_WORDS = 380
SLOP = (
    "it's important to note",
    "whether you're a beginner",
    "in today's world",
    "delve ",
    "unlock the",
    "comprehensive guide",
    "in the world of",
    "game-changer",
    "robust",
    "leverage",
    "holistic approach",
)


def body_of(text: str) -> str:
    if not text.startswith("---"):
        return text
    end = text.find("\n---", 3)
    return text[end + 4 :] if end != -1 else text


def main() -> int:
    files = sorted(HERE.glob("[0-9][0-9]-*.md"))
    errors: list[str] = []

    if len(files) < MIN_DRAFTS:
        errors.append(f"draft count {len(files)} < {MIN_DRAFTS}")

    for path in files:
        text = path.read_text(encoding="utf-8")
        low = text.lower()
        if "status: staged" not in text:
            errors.append(f"{path.name}: missing status: staged")
        if "culture: pot" not in text:
            errors.append(f"{path.name}: missing culture: pot")
        if "voice_check: edited" not in text:
            errors.append(f"{path.name}: missing voice_check: edited")
        if "series: fig-container-growing" not in text:
            errors.append(f"{path.name}: missing series")
        words = len(body_of(text).split())
        if words < MIN_WORDS:
            errors.append(f"{path.name}: {words} words < {MIN_WORDS}")
        for phrase in SLOP:
            if phrase in low:
                errors.append(f"{path.name}: slop phrase '{phrase}'")
        if re.search(r"even a\n[aeiou]", text, re.I):
            errors.append(f"{path.name}: broken 'even a' line break")

    if errors:
        print("validate.py FAILED:")
        for e in errors:
            print(" ", e)
        return 1
    print(f"validate.py OK — {len(files)} drafts, voice_check edited, min words {MIN_WORDS}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
