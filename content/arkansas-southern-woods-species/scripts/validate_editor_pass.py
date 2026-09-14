#!/usr/bin/env python3
"""Post-editor validation for Arkansas / Southern furniture-woods drafts."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

BANNED = re.compile(
    r"\b(delve|delving|robust|leverage|unlock|journey|game-changer|supercharge|"
    r"moreover|furthermore|rapidly evolving|cutting-edge|holistic|unpack|"
    r"elevate|empower|seamless)\b",
    re.I,
)

# Metaphorical "landscape" only — allow grain figure "a landscape" in walnut crotch piece.
BANNED_LANDSCAPE = re.compile(
    r"\b(?:in today's|it's important to note|whether you're|in conclusion|"
    r"at the end of the day|rich tapestry)\b",
    re.I,
)


def body(text: str) -> str:
    if text.startswith("---"):
        parts = text.split("---", 2)
        return parts[2] if len(parts) > 2 else text
    return text


def main() -> int:
    errors: list[str] = []
    drafts = sorted(ROOT.glob("[0-9]*.md"))
    if len(drafts) != 46:
        errors.append(f"expected 46 drafts, found {len(drafts)}")

    for path in drafts:
        text = path.read_text(encoding="utf-8")
        if "voice_check: edited" not in text:
            errors.append(f"{path.name}: missing voice_check: edited")
        b = body(text)
        if BANNED.search(b):
            errors.append(f"{path.name}: STYLE_GUIDE ban-list hit in body")
        if BANNED_LANDSCAPE.search(b):
            errors.append(f"{path.name}: banned filler phrase in body")

    if errors:
        for e in errors:
            print(e, file=sys.stderr)
        return 1
    print(f"OK: {len(drafts)} drafts passed editor validation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
