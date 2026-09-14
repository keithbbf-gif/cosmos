#!/usr/bin/env python3
"""Pack QA for content/veneer-history-practice/. Exit 0 only if the syllabus holds."""

from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DRAFTS = ROOT / "drafts"
MIN_WORDS = 1200
MIN_DRAFTS = 40
REQUIRED_META = ROOT / "STYLE_GUIDE.md"
PACK_FILES = [
    "STYLE_GUIDE.md",
    "README.md",
    "INDEX.md",
    "MANIFEST.md",
    "BIBLIOGRAPHY.md",
    "PHOTO_CAPTIONS.md",
    "WP_IMPORT.md",
]
BANNED = [
    r"\bdelve\b",
    r"\bleverage\b",
    r"\bunlock\b",
    r"\brobust\b",
    r"\bcutting-edge\b",
    r"\bgame-changer\b",
    r"in today's",
    r"it's important to note",
    r"\bmoreover\b",
    r"\bfurthermore\b",
    r"whether you're a beginner",
    r"in conclusion",
    r"at the end of the day",
    r"the key takeaway",
    r"let's dive in",
    r"this article will explore",
]
FM_KEYS = (
    "title",
    "slug",
    "status",
    "voice_check",
    "word_count",
    "dek",
    "series",
    "stage",
    "stage_name",
    "order",
    "topic",
)


def fm_get(fm: str, key: str) -> str:
    m = re.search(rf"^{key}:\s*(.*)$", fm, re.M)
    return m.group(1).strip().strip('"') if m else ""


def body_words(body: str) -> int:
    return len(re.findall(r"[A-Za-z0-9']+", body))


def first_sentence(body: str) -> str:
    plain = re.sub(r"^# .+\n+", "", body.strip())
    return re.split(r"(?<=[.!?])\s+", plain, maxsplit=1)[0].replace("\n", " ").strip()


def main() -> int:
    errors: list[str] = []
    for name in PACK_FILES:
        if not (ROOT / name).is_file():
            errors.append(f"missing pack file: {name}")
    if not REQUIRED_META.is_file():
        errors.append("STYLE_GUIDE missing")

    files = sorted(DRAFTS.glob("*.md"))
    if len(files) < MIN_DRAFTS:
        errors.append(f"draft count {len(files)} < {MIN_DRAFTS}")

    rows = []
    openings = []
    slugs = []
    orders = []
    for path in files:
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---"):
            errors.append(f"{path.name}: no front matter")
            continue
        parts = text.split("---", 2)
        if len(parts) < 3:
            errors.append(f"{path.name}: broken front matter")
            continue
        fm, body = parts[1], parts[2]
        for key in FM_KEYS:
            if not fm_get(fm, key):
                errors.append(f"{path.name}: missing {key}")
        if fm_get(fm, "status") != "draft":
            # figure blocks also have status: needed; require a draft line
            if not re.search(r"^status:\s*draft\s*$", fm, re.M):
                errors.append(f"{path.name}: status is not draft")
        if fm_get(fm, "voice_check") != "human":
            errors.append(f"{path.name}: voice_check is not human")
        if fm_get(fm, "series") != "veneer-history-practice":
            errors.append(f"{path.name}: series mismatch")
        wc = body_words(body)
        claimed = fm_get(fm, "word_count")
        if claimed.isdigit() and abs(int(claimed) - wc) > 5:
            errors.append(f"{path.name}: word_count {claimed} != body {wc}")
        if wc < MIN_WORDS:
            errors.append(f"{path.name}: {wc} words < {MIN_WORDS}")
        low = body.lower()
        for pat in BANNED:
            if re.search(pat, low):
                errors.append(f"{path.name}: banned pattern {pat}")
        openings.append(first_sentence(body))
        slugs.append(fm_get(fm, "slug"))
        try:
            orders.append(int(fm_get(fm, "order")))
        except ValueError:
            errors.append(f"{path.name}: order not an int")
        rows.append((path.name, wc))

    dups = [s for s, n in Counter(openings).items() if n > 1 and s]
    if dups:
        errors.append(f"duplicate openings: {dups[:3]}")
    slug_dups = [s for s, n in Counter(slugs).items() if n > 1 and s]
    if slug_dups:
        errors.append(f"duplicate slugs: {slug_dups}")
    if orders and sorted(orders) != list(range(1, len(orders) + 1)):
        errors.append(f"order sequence broken: {sorted(orders)[:8]}...")

    total = sum(wc for _, wc in rows)
    print(f"drafts={len(rows)} words={total} min={min(wc for _, wc in rows)} max={max(wc for _, wc in rows)}")
    for name, wc in rows:
        print(f"  {name}\t{wc}")
    if errors:
        print("FAIL")
        for e in errors:
            print(f"  {e}")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
