#!/usr/bin/env python3
"""Editor gate for staged fig-grafting-budding drafts."""
from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
MIN_DRAFTS = 50
MIN_WORDS = 420
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
    drafts = sorted(p for p in HERE.glob("stage-*/*.md") if p.name != "README.md")
    errors: list[str] = []

    if len(drafts) < MIN_DRAFTS:
        errors.append(f"draft count {len(drafts)} < {MIN_DRAFTS}")

    for path in drafts:
        text = path.read_text(encoding="utf-8")
        low = text.lower()
        if "status: staged" not in text:
            errors.append(f"{path.name}: missing status: staged")
        if "zone: 8a" not in text:
            errors.append(f"{path.name}: missing zone: 8a")
        if "voice_check: edited" not in text:
            errors.append(f"{path.name}: missing voice_check: edited")
        words = len(re.findall(r"[A-Za-z0-9']+", body_of(text)))
        if words < MIN_WORDS:
            errors.append(f"{path.name}: {words} words < {MIN_WORDS}")
        for phrase in SLOP:
            if phrase in low:
                errors.append(f"{path.name}: slop phrase '{phrase}'")
        if re.search(r"even a\n[aeiou]", text, re.I):
            errors.append(f"{path.name}: broken 'even a' line break")
        if re.search(r"\bA 8a\b", text):
            errors.append(f"{path.name}: grammar 'A 8a' (want An 8a)")

    if errors:
        print("validate.py FAILED:")
        for e in errors:
            print(" ", e)
        return 1
    print(
        f"validate.py OK — {len(drafts)} drafts, voice_check edited, min words {MIN_WORDS}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
