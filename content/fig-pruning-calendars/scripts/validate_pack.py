#!/usr/bin/env python3
"""Validate editor + image SEO pass for fig pruning calendar drafts."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

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
    drafts = sorted(
        p for p in ROOT.glob("*.md") if p.name != "README.md" and re.match(r"^\d{2}-", p.name)
    )
    if len(drafts) != 46:
        errors.append(f"expected 46 drafts, found {len(drafts)}")

    for path in drafts:
        text = path.read_text(encoding="utf-8")
        if "voice_check: edited" not in text:
            errors.append(f"{path.name}: missing voice_check: edited")
        if "zone_center: 8a" not in text:
            errors.append(f"{path.name}: missing zone_center: 8a")
        if "figures:" not in text:
            errors.append(f"{path.name}: missing figures: front matter")
        if "<figure>" not in text:
            errors.append(f"{path.name}: missing <figure> block")
        b = body(text)
        if BANNED.search(b):
            errors.append(f"{path.name}: ban-list hit in body")
        if 'loading="lazy"' not in b or "decoding=" not in b:
            errors.append(f"{path.name}: img missing lazy/async attrs")
        words = len(re.findall(r"\b\w+\b", b))
        if words < 280:
            errors.append(f"{path.name}: word count {words} below 280 floor")

    if errors:
        for e in errors:
            print(e, file=sys.stderr)
        return 1
    print(f"OK: {len(drafts)} drafts passed pack validation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
