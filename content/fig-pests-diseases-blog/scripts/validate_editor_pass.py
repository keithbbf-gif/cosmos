#!/usr/bin/env python3
"""Post-editor validation for the fig pests & diseases draft pack."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DRAFTS = ROOT / "drafts"

BANNED = re.compile(
    r"\b(delve|delving|robust|leverage|unlock|journey|game-changer|supercharge|"
    r"moreover|furthermore|rapidly evolving)\b",
    re.I,
)

def body(text: str) -> str:
    if text.startswith("---"):
        parts = text.split("---", 2)
        return parts[2] if len(parts) > 2 else text
    return text


def main() -> int:
    errors: list[str] = []
    drafts = sorted(DRAFTS.glob("*.md"))
    if len(drafts) != 45:
        errors.append(f"expected 45 drafts, found {len(drafts)}")

    for path in drafts:
        text = path.read_text(encoding="utf-8")
        if "voice_check: edited" not in text:
            errors.append(f"{path.name}: missing voice_check: edited")
        if "zone: 8a" not in text:
            errors.append(f"{path.name}: missing zone: 8a")
        b = body(text)
        if BANNED.search(b):
            errors.append(f"{path.name}: STYLE_GUIDE ban-list hit in body")
        words = len(re.findall(r"\b\w+\b", b))
        if words < 1100 or words > 1600:
            errors.append(f"{path.name}: word count {words} outside 1100–1600")

    if errors:
        for e in errors:
            print(e, file=sys.stderr)
        return 1
    print(f"OK: {len(drafts)} drafts passed editor validation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
