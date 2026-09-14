#!/usr/bin/env python3
"""Post-editor validation for the fig-history article pack."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAGING = ROOT / "articles" / "_staging"

BANNED = re.compile(
    r"\b(delve|tapestry|moreover|furthermore|nestled|showcases)\b",
    re.I,
)

def main() -> int:
    errors: list[str] = []
    articles = sorted(STAGING.glob("*/index.md"))
    if len(articles) != 62:
        errors.append(f"expected 62 articles, found {len(articles)}")

    for path in articles:
        text = path.read_text(encoding="utf-8")
        if "voice_check: edited" not in text:
            errors.append(f"{path.parent.name}: missing voice_check: edited")
        body = text.split("---", 2)[2] if text.startswith("---") else text
        if BANNED.search(body):
            errors.append(f"{path.parent.name}: banned habit word in body")
        if path.parent.name != "glossary-fig-history-terms":
            if "## Sources for this piece" not in body:
                errors.append(f"{path.parent.name}: missing Sources section")
        elif "BIBLIOGRAPHY.md" not in body:
            errors.append("glossary-fig-history-terms: missing bibliography pointer")
        for m in re.finditer(r"<!-- figure-id: ([^>]+) -->", text):
            if not m.group(1).strip():
                errors.append(f"{path.parent.name}: empty figure-id")
        for m in re.finditer(r"\]\((\.\./\.\./\.\./assets/[^)]+)\)", text):
            rel = m.group(1)
            if not (path.parent / rel).is_file():
                errors.append(f"{path.parent.name}: missing asset {rel}")

    if errors:
        for e in errors:
            print(e, file=sys.stderr)
        return 1
    print(f"OK: {len(articles)} articles passed editor validation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
