#!/usr/bin/env python3
"""Validate staged desk / hallway / entryway furniture drafts.

Quality gates (fail closed):
  - at least 40 markdown drafts in content/desks-hallway-entryway-furniture/drafts/
  - required frontmatter keys on every draft
  - status is staged
  - unique ids, slugs, titles, and opening paragraphs
  - minimum body length (words after frontmatter)
  - required brief topics appear in at least one draft's topics list
  - refuse common brochure / LLM-slop phrases
  - voice_check: edited, lane, meta_description, figure_image in frontmatter
  - one Commons/museum <figure class="desk-entry-figure"> per draft (SEO alt + figcaption)
  - RIGHTS.md present; raster files on disk match embeds
"""

from __future__ import annotations

import json
import os
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK_DIR = ROOT / "content" / "desks-hallway-entryway-furniture"
RIGHTS = PACK_DIR / "RIGHTS.md"
IMAGE_DIR = PACK_DIR / "assets" / "images"
DRAFT_DIR = Path(
    os.environ.get(
        "COSMOS_DESK_ENTRY_DRAFT_DIR",
        ROOT / "content" / "desks-hallway-entryway-furniture" / "drafts",
    )
)
MIN_DRAFTS = 40
MIN_WORDS = 280
MIN_ALT_LEN = 48
REQUIRED_FRONT = (
    "id",
    "slug",
    "title",
    "meta_description",
    "stage",
    "status",
    "lane",
    "voice_check",
    "topics",
    "figure_image",
)
REQUIRED_TOPICS = {
    "history": "history",
    "desk": "desk",
    "hallway": "hallway",
    "entryway": "entryway",
    "design": "design",
    "proportions": "proportions",
    "bbf": "bbf",
    "collections": "collections",
    "staging": "staging",
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
    "fast-paced world",
)

FM_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.S)
FIGURE_CLASS_RE = re.compile(
    r'<figure class="desk-entry-figure">\s*'
    r'<img src="(?P<src>\.\./assets/images/[^"]+)" alt="(?P<alt>[^"]+)"[^>]*/>\s*'
    r"<figcaption>Figure 1\.[^<]+RIGHTS\.md\.</figcaption>\s*"
    r"</figure>",
    re.S,
)


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

    if not RIGHTS.is_file():
        errors.append(f"missing {RIGHTS.relative_to(ROOT)}")
    manifest = IMAGE_DIR / "manifest.json"
    if not manifest.is_file():
        errors.append(f"missing {manifest.relative_to(ROOT)}")
    else:
        manifest_slugs = {r["slug"] for r in json.loads(manifest.read_text(encoding="utf-8"))}

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
        if fm.get("voice_check") != "edited":
            errors.append(f"{path.name}: voice_check {fm.get('voice_check')!r} != edited")
        if fm.get("lane") != "bbf-desks-hall":
            errors.append(f"{path.name}: lane {fm.get('lane')!r} != bbf-desks-hall")
        slug = fm.get("slug", "")
        if manifest.is_file() and slug and slug not in manifest_slugs:
            errors.append(f"{path.name}: slug {slug!r} missing from image manifest")
        figs = FIGURE_CLASS_RE.findall(body)
        if len(figs) != 1:
            errors.append(f"{path.name}: want exactly one desk-entry-figure embed")
        else:
            src, alt = figs[0]
            if fm.get("figure_image") != src:
                errors.append(f"{path.name}: figure_image {fm.get('figure_image')!r} != embed {src!r}")
            if len(alt) < MIN_ALT_LEN:
                errors.append(f"{path.name}: img alt too short ({len(alt)} < {MIN_ALT_LEN})")
            rel_file = src.replace("../assets/images/", "")
            disk = IMAGE_DIR / rel_file
            if not disk.is_file():
                errors.append(f"{path.name}: missing raster {rel_file}")
        if "<!-- figure:commons -->" not in body:
            errors.append(f"{path.name}: missing figure:commons marker")
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
        if fm.get("id"):
            try:
                expected = f"{int(fm['id']):02d}-"
            except ValueError:
                expected = None
            if expected and not path.name.startswith(expected):
                warnings.append(
                    f"{path.name}: filename does not match id {fm.get('id')}"
                )
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
