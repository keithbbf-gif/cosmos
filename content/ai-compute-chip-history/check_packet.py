#!/usr/bin/env python3
"""Checks on the staged writing packet. Evidence, not a vibe."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BANNED = re.compile(
    r"cosmos|patent|uspto|claim\s+chart|\bketh\b|\bkeith\b|\bmotif\b",
    re.I,
)
MIN_FILES = 40
MIN_FINAL_WORDS = 1200


def main() -> int:
    files = sorted(p for p in ROOT.glob("*.md") if p.is_file())
    errors: list[str] = []
    hits: list[str] = []
    empty: list[str] = []
    words_by_file: dict[str, int] = {}

    for path in files:
        text = path.read_text(encoding="utf-8")
        if not text.strip():
            empty.append(path.name)
        words_by_file[path.name] = len(re.findall(r"\S+", text))
        for i, line in enumerate(text.splitlines(), 1):
            if BANNED.search(line):
                hits.append(f"{path.name}:{i}:{line.strip()}")

    n = len(files)
    if n < MIN_FILES:
        errors.append(f"file count {n} < {MIN_FILES}")
    if empty:
        errors.append("empty: " + ", ".join(empty))
    if hits:
        errors.append("banned term:\n  " + "\n  ".join(hits))

    final = ROOT / "50-essay-final.md"
    if not final.exists():
        errors.append("missing 50-essay-final.md")
    else:
        fw = words_by_file.get("50-essay-final.md", 0)
        if fw < MIN_FINAL_WORDS:
            errors.append(f"final word count {fw} < {MIN_FINAL_WORDS}")

    print(f"markdown_files={n}")
    print(f"total_words={sum(words_by_file.values())}")
    print(f"final_words={words_by_file.get('50-essay-final.md', 0)}")
    print(f"banned_hits={len(hits)}")
    print(f"empty_files={len(empty)}")
    print("ok" if not errors else "FAIL")
    for e in errors:
        print(e)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
