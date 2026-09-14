#!/usr/bin/env python3
"""Post-editor validation for the bunk-beds-youth-furniture-history pack."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

BANNED = re.compile(
    r"\b(delve|tapestry|moreover|furthermore|nestled|showcases|"
    r"it's important to note|in conclusion|fast-paced|vibrant heritage)\b",
    re.I,
)

ESSAY_GLOB = "[0-9]*.md"
FRAME_FILES = {"README.md", "SOURCES.md", "MANIFEST.md", "EDITOR_REPORT.md"}


def main() -> int:
    errors: list[str] = []
    essays = sorted(ROOT.glob(ESSAY_GLOB))
    if len(essays) != 46:
        errors.append(f"expected 46 numbered essays, found {len(essays)}")

    report = ROOT / "EDITOR_REPORT.md"
    if not report.is_file():
        errors.append("missing EDITOR_REPORT.md")

    for path in sorted(ROOT.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---"):
            errors.append(f"{path.name}: missing YAML front matter")
            continue
        fm, body = text.split("---", 2)[1], text.split("---", 2)[2]
        if "voice_check: edited" not in fm:
            errors.append(f"{path.name}: missing voice_check: edited")
        if "not: legal-advice" not in fm:
            errors.append(f"{path.name}: missing not: legal-advice")
        if "audience: educational" not in fm:
            errors.append(f"{path.name}: missing audience: educational")
        if path.name in FRAME_FILES and path.name != "EDITOR_REPORT.md":
            continue
        if path.name == "EDITOR_REPORT.md":
            continue
        for m in BANNED.finditer(body):
            if path.name == "README.md" and m.group().lower() in {"delve", "fast-paced"}:
                continue
            errors.append(f"{path.name}: banned habit word: {m.group()}")

    if errors:
        for e in errors:
            print(e, file=sys.stderr)
        return 1
    print(f"OK: {len(essays)} essays + frame files passed editor validation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
