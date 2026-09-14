#!/usr/bin/env python3
"""Inventory and novelty-fence check for the staged multimodal history pack."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
HOUSE = {
    "README.md",
    "NOVELTY.md",
    "MANIFEST.md",
    "INDEX.md",
    "SOURCES.md",
}
FORBIDDEN = (
    "COSMOS",
    "CCr",
    "KDash",
    "kdash",
    "MOTIF",
    "watchdog2",
    "BUCm",
    "live tree",
    "live-tree",
    "Keith",
)
REQUIRED_FM = (
    "id:",
    "title:",
    "slug:",
    "series: multimodal-ai-public-history",
    "stage: draft",
    "status: staged",
    "publish: false",
    "novelty: public-record",
)
MIN_WORDS = 280
FLOOR = 40


def split_frontmatter(text: str) -> tuple[str, str]:
    if not text.startswith("---\n"):
        raise ValueError("missing opening frontmatter")
    end = text.find("\n---\n", 4)
    if end < 0:
        raise ValueError("missing closing frontmatter")
    return text[4:end], text[end + 5 :]


def word_count(body: str) -> int:
    return len(re.findall(r"[A-Za-z0-9']+", body))


def main() -> int:
    errors: list[str] = []
    essays = sorted(ROOT.glob("stage-*/[0-9][0-9]-*.md"))
    print(f"root={ROOT}")
    print(f"essay_files={len(essays)}")
    if len(essays) < FLOOR:
        errors.append(f"essay count {len(essays)} < floor {FLOOR}")
    slugs: set[str] = set()
    ids: set[str] = set()
    total_words = 0
    for path in essays:
        text = path.read_text(encoding="utf-8")
        try:
            fm, body = split_frontmatter(text)
        except ValueError as exc:
            errors.append(f"{path.name}: {exc}")
            continue
        for needle in REQUIRED_FM:
            if needle not in fm:
                errors.append(f"{path.name}: missing `{needle}`")
        slug_m = re.search(r"^slug:\s*(\S+)", fm, re.M)
        id_m = re.search(r"^id:\s*(\S+)", fm, re.M)
        if slug_m:
            slug = slug_m.group(1)
            if slug in slugs:
                errors.append(f"duplicate slug {slug}")
            slugs.add(slug)
        if id_m:
            ident = id_m.group(1)
            if ident in ids:
                errors.append(f"duplicate id {ident}")
            ids.add(ident)
        words = word_count(body)
        total_words += words
        if words < MIN_WORDS:
            errors.append(f"{path.name}: {words} words < {MIN_WORDS}")
        print(f"{path.relative_to(ROOT)} words={words}")
    folder_text = []
    for md in sorted(ROOT.rglob("*.md")):
        folder_text.append(md.read_text(encoding="utf-8"))
    blob = "\n".join(folder_text)
    for word in FORBIDDEN:
        if word in blob:
            errors.append(f"forbidden token present: {word!r}")
    expected_house = HOUSE
    present_house = {p.name for p in ROOT.glob("*.md")}
    missing_house = expected_house - present_house
    if missing_house:
        errors.append(f"missing house files: {sorted(missing_house)}")
    print(f"total_essay_words={total_words}")
    print(f"mean_essay_words={total_words // max(len(essays), 1)}")
    if errors:
        print("FAIL")
        for err in errors:
            print(f"  {err}")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
