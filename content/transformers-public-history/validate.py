#!/usr/bin/env python3
"""Mechanical checks for staged transformer-history drafts.

Not a novelty opinion. Not a factual oracle. Checks structure, length,
source lines, and a deny-list of private-system tokens in draft bodies.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MIN_DRAFTS = 40
MIN_WORDS = 300
REQUIRED_FM = (
    "id",
    "slug",
    "title",
    "status",
    "series",
    "era",
    "first_public",
    "date_kind",
    "novelty_lane",
    "private_systems",
)
REQUIRED_HEADINGS = (
    "## The claim",
    "## What this draft does not claim",
    "## Sources",
    "## Draft debt",
)
# Draft bodies must not name these. README may mention the fence once.
DENY = re.compile(
    r"""
    \bCOSMOS\b
    | \bCCr\b
    | \bMOTIF\b
    | \bKDash\b
    | \bcDeck\b
    | \bBUCm\b
    | \bBUcr\b
    | \bGitur\b
    | \bGrokBot\b
    | \bOpenWork\b
    | \bDHx\b
    | \bwatchdog2\b
    | \bcosmos_paths\b
    | \bKMesh\b
    | \bCCR\.lease\b
    | fencing\ tokens?
    | live\ tree
    | work_orders
    """,
    re.IGNORECASE | re.VERBOSE,
)
STATUS_OK = {"staged-draft"}
SERIES_OK = {"transformers-public-history"}
NOVELTY_OK = {"public-prior-art-only"}
PRIVATE_OK = {"excluded"}


def parse_fm(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---"):
        raise ValueError("missing opening frontmatter")
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise ValueError("missing closing frontmatter")
    fm: dict[str, str] = {}
    for raw in parts[1].strip().splitlines():
        if not raw.strip() or ":" not in raw:
            continue
        k, v = raw.split(":", 1)
        fm[k.strip()] = v.strip().strip('"').strip("'")
    return fm, parts[2]


def words(text: str) -> int:
    return len(re.findall(r"\S+", text))


def main() -> int:
    drafts = sorted(
        p
        for p in ROOT.glob("*.md")
        if p.name not in {"README.md"} and re.match(r"^\d{2}-", p.name)
    )
    errors: list[str] = []
    ids: set[str] = []
    ids = set()
    slugs: set[str] = set()
    rows: list[tuple[str, str, int, str]] = []

    if len(drafts) < MIN_DRAFTS:
        errors.append(f"draft count {len(drafts)} < {MIN_DRAFTS}")

    for path in drafts:
        text = path.read_text(encoding="utf-8")
        try:
            fm, body = parse_fm(text)
        except ValueError as e:
            errors.append(f"{path.name}: {e}")
            continue
        for key in REQUIRED_FM:
            if not fm.get(key):
                errors.append(f"{path.name}: missing {key}")
        if fm.get("status") not in STATUS_OK:
            errors.append(f"{path.name}: status {fm.get('status')!r} not staged-draft")
        if fm.get("series") not in SERIES_OK:
            errors.append(f"{path.name}: bad series")
        if fm.get("novelty_lane") not in NOVELTY_OK:
            errors.append(f"{path.name}: novelty_lane must be public-prior-art-only")
        if fm.get("private_systems") not in PRIVATE_OK:
            errors.append(f"{path.name}: private_systems must be excluded")
        did = fm.get("id", "")
        if did in ids:
            errors.append(f"{path.name}: duplicate id {did}")
        ids.add(did)
        slug = fm.get("slug", "")
        if slug in slugs:
            errors.append(f"{path.name}: duplicate slug {slug}")
        slugs.add(slug)
        wc = words(body)
        if wc < MIN_WORDS:
            errors.append(f"{path.name}: {wc} words < {MIN_WORDS}")
        for h in REQUIRED_HEADINGS:
            if h not in body:
                errors.append(f"{path.name}: missing {h}")
        if body.lower().count("arxiv") + body.lower().count("http") + body.count("`official") < 1:
            if "## Sources" in body and len(body.split("## Sources")[-1].strip()) < 40:
                errors.append(f"{path.name}: thin Sources section")
        deny_hits = DENY.findall(body)
        if deny_hits:
            errors.append(f"{path.name}: novelty deny-list hit {deny_hits!r}")
        rows.append((fm.get("id", "?"), fm.get("first_public", "?"), wc, path.name))

    readme = ROOT / "README.md"
    if not readme.exists():
        errors.append("README.md missing")

    print(f"drafts={len(drafts)} min={MIN_DRAFTS}")
    print(f"ids={len(ids)}")
    total_words = sum(r[2] for r in rows)
    print(f"total_body_words={total_words}")
    print("id              first_public  words  file")
    for row in rows:
        print(f"{row[0]:<14}  {row[1]:<12}  {row[2]:>5}  {row[3]}")
    if errors:
        print("FAIL")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
