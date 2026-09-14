#!/usr/bin/env python3
"""Validate staged butcher-block countertop guide drafts.

Quality gates (fail closed):
  - at least 40 markdown drafts in content/butcher-block-countertops-guide/drafts/
  - required frontmatter keys on every draft
  - status is staged
  - unique ids, slugs, titles, and opening paragraphs
  - minimum body length (words after frontmatter)
  - required brief topics appear in at least one draft's topics list
  - refuse common brochure / LLM-slop phrases
"""

from __future__ import annotations

import os
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DRAFT_DIR = Path(
    os.environ.get(
        "COSMOS_BUTCHER_BLOCK_DRAFT_DIR",
        ROOT / "content" / "butcher-block-countertops-guide" / "drafts",
    )
)
MIN_DRAFTS = 40
MIN_WORDS = 340
REQUIRED_FRONT = ("id", "slug", "title", "stage", "status", "topics")
REQUIRED_TOPICS = {
    "history": "history",
    "care": "care",
    "island-tops": "island-tops",
    "bradley": "bradley",
    "butcher-block": "butcher-block",
}
SLOP = (
    "in today's",
    "in today’s",
    "let's dive",
    "let’s dive",
    "delve",
    "elevate your",
    "whether you're a homeowner",
    "whether you’re a homeowner",
    "in conclusion",
    "tapestry",
    "unlock the secrets",
    "game changer",
    "game-changer",
    "in this comprehensive guide",
    "look no further",
)

FM_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.S)


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    m = FM_RE.match(text)
    if not m:
        return {}, text
    raw, body = m.group(1), m.group(2)
    data: dict[str, str] = {}
    for line in raw.splitlines():
        if ":" not in line:
            continue
        key, val = line.split(":", 1)
        data[key.strip()] = val.strip().strip('"')
    return data, body


def words(body: str) -> int:
    return len(re.findall(r"[A-Za-z0-9']+", body))


def opening(body: str) -> str:
    paras = [p.strip() for p in re.split(r"\n\s*\n", body.strip()) if p.strip()]
    return paras[0] if paras else ""


def main() -> int:
    files = sorted(DRAFT_DIR.glob("*.md"))
    errors: list[str] = []
    warnings: list[str] = []
    rows: list[dict] = []

    if len(files) < MIN_DRAFTS:
        errors.append(f"draft count {len(files)} < {MIN_DRAFTS}")

    ids: list[str] = []
    slugs: list[str] = []
    titles: list[str] = []
    openings: list[str] = []
    topic_hits: Counter[str] = Counter()

    for path in files:
        text = path.read_text(encoding="utf-8")
        fm, body = parse_frontmatter(text)
        missing = [k for k in REQUIRED_FRONT if k not in fm]
        if missing:
            errors.append(f"{path.name}: missing frontmatter {missing}")
        if fm.get("status") != "staged":
            errors.append(f"{path.name}: status {fm.get('status')!r} is not staged")
        wc = words(body)
        if wc < MIN_WORDS:
            errors.append(f"{path.name}: {wc} words < {MIN_WORDS}")
        low = body.lower()
        for phrase in SLOP:
            if phrase in low:
                errors.append(f"{path.name}: slop phrase {phrase!r}")
        op = opening(body)
        ids.append(fm.get("id", path.name))
        slugs.append(fm.get("slug", path.name))
        titles.append(fm.get("title", path.name))
        openings.append(op)
        topics = fm.get("topics", "")
        for key in REQUIRED_TOPICS:
            if key in topics:
                topic_hits[key] += 1
        if fm.get("id") and not path.name.startswith(f"{int(fm['id']):02d}-"):
            warnings.append(f"{path.name}: filename does not match id {fm.get('id')}")
        rows.append(
            {
                "file": path.name,
                "id": fm.get("id", ""),
                "stage": fm.get("stage", ""),
                "words": wc,
                "topics": topics,
            }
        )

    for label, values in (
        ("id", ids),
        ("slug", slugs),
        ("title", titles),
        ("opening", openings),
    ):
        c = Counter(values)
        dups = [k for k, n in c.items() if n > 1 and k]
        if dups:
            errors.append(f"duplicate {label}: {dups[:5]}")

    for key, name in REQUIRED_TOPICS.items():
        if topic_hits[key] < 1:
            errors.append(f"required topic {name!r} missing from all frontmatter")

    total_words = sum(r["words"] for r in rows)
    print(f"drafts: {len(files)}")
    print(f"words:  {total_words}")
    print(f"min:    {min((r['words'] for r in rows), default=0)}")
    print(f"max:    {max((r['words'] for r in rows), default=0)}")
    print("topic hits:")
    for key in REQUIRED_TOPICS:
        print(f"  {key:16} {topic_hits[key]}")
    print("stages:")
    stage_c = Counter(r["stage"] for r in rows)
    for st, n in sorted(stage_c.items()):
        print(f"  {st:16} {n}")
    if warnings:
        print("warnings:")
        for w in warnings:
            print(f"  WARN  {w}")
    if errors:
        print("errors:")
        for e in errors:
            print(f"  FAIL  {e}")
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
