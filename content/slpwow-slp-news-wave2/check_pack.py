#!/usr/bin/env python3
"""Structural QA for content/slpwow-slp-news-wave2/.

Counts articles, required YAML, educational note, citations, banned style
phrases, minimum words, INDEX slug match. Exit 0 only if all gates pass.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ART = ROOT / "articles"
ASSETS = ROOT / "assets"
EMBEDS = ROOT / "embeds"
INDEX = ROOT / "INDEX.md"

FIGURE_NEEDLES = (
    "<figure",
    "<figcaption",
    'itemtype="https://schema.org/ImageObject"',
    'itemprop="contentUrl"',
)
FIG_OPS_FILES = (
    "RIGHTS.md",
    "AGENTS_GRAPHICS.md",
    "GRAPHICS_CHECKLIST.md",
    "GRAPHICS_INDEX.md",
)

REQUIRED_YAML = [
    "title",
    "slug",
    "meta_description",
    "series",
    "type",
    "desk",
    "order",
    "audience",
    "brand",
    "status",
    "stage",
    "voice_check",
    "last_verified",
]

ALLOWED_DESKS = {"asha", "cms", "compact", "research", "literacy"}
SERIES = "slpwow-slp-news-wave2"
MIN_ARTICLES = 40
TARGET_ARTICLES = 46
MIN_WORDS = 520
MAX_QUOTE_RUN = 80  # words inside a single quoted run — dump guard

BANNED = [
    r"\bdelve(?:s|d|ing)?\b",
    r"in today's rapidly",
    r"it's important to note",
    r"it is important to note",
    r"\bleverage\b",
    r"\bunlock(?:s|ed|ing)?\b",
    r"cutting-edge",
    r"game-chang",
    r"\bin conclusion\b",
    r"whether you're a",
    r"whether you’re a",
    r"in this article we will explore",
    r"\btapestry\b",
    r"\bplethora\b",
    r"gold-standard treatment",
    r"try this at home",
    r"self-treat",
    r"book with us",
    r"healthcare landscape",
    r"holistic approach",
]

BANNED_BODY_ONLY = [
    r"\brobust\b",
    r"\blandscape\b",
    r"\bseamless\b",
    r"\bempower(?:s|ed|ing)?\b",
]

DISCLAIMER_NEEDLE = "not legal advice, not billing advice"
SOURCES_NEEDLE = "## Sources"
FRONT_RE = re.compile(r"^---\n(.*?)\n---\n", re.S)
LIST_URL_RE = re.compile(r"^\s*-\s+\"?(https?://[^\"]+)\"?\s*$", re.M)


def parse_front(text: str) -> dict[str, str]:
    m = FRONT_RE.match(text)
    if not m:
        return {}
    data: dict[str, str] = {}
    in_list = None
    for line in m.group(1).splitlines():
        if in_list and (line.startswith("  - ") or line.startswith("    - ")):
            continue
        if line.strip().endswith(":") and not line.startswith(" ") and line[:-1].strip() in {
            "tags",
            "citations",
        }:
            in_list = line[:-1].strip()
            data[in_list] = "list"
            continue
        if ":" in line and not line.startswith(" ") and not line.startswith("-"):
            in_list = None
            k, v = line.split(":", 1)
            data[k.strip()] = v.strip().strip('"')
    return data


def body(text: str) -> str:
    m = FRONT_RE.match(text)
    return text[m.end() :] if m else text


def body_words(text: str) -> int:
    return len(re.findall(r"[A-Za-z0-9']+", body(text)))


def citation_count(text: str) -> int:
    m = FRONT_RE.match(text)
    if not m:
        return 0
    return len(LIST_URL_RE.findall(m.group(1)))


def longest_quote_words(text: str) -> int:
    runs = re.findall(r"[“\"](.+?)[”\"]", body(text), re.S)
    best = 0
    for run in runs:
        n = len(re.findall(r"[A-Za-z0-9']+", run))
        if n > best:
            best = n
    return best


def main() -> int:
    files = sorted(ART.glob("*.md"))
    errors: list[str] = []
    if len(files) < MIN_ARTICLES:
        errors.append(f"article count {len(files)} < {MIN_ARTICLES}")
    if len(files) != TARGET_ARTICLES:
        errors.append(f"article count {len(files)} != {TARGET_ARTICLES} (manifest target)")

    idx = INDEX.read_text(encoding="utf-8") if INDEX.is_file() else ""
    if not idx:
        errors.append("INDEX.md missing")

    orders: list[int] = []
    slugs: list[str] = []
    desks: dict[str, int] = {d: 0 for d in ALLOWED_DESKS}

    for path in files:
        text = path.read_text(encoding="utf-8")
        fm = parse_front(text)
        for key in REQUIRED_YAML:
            if key not in fm:
                errors.append(f"{path.name}: missing YAML {key}")
        if fm.get("voice_check") != "human":
            errors.append(f"{path.name}: voice_check is not human")
        if fm.get("stage") != "draft":
            errors.append(f"{path.name}: stage is not draft")
        if fm.get("status") != "draft":
            errors.append(f"{path.name}: status is not draft")
        if fm.get("series") != SERIES:
            errors.append(f"{path.name}: wrong series")
        if fm.get("type") != "news-brief":
            errors.append(f"{path.name}: type is not news-brief")
        desk = fm.get("desk", "")
        if desk not in ALLOWED_DESKS:
            errors.append(f"{path.name}: desk {desk!r} not allowed")
        else:
            desks[desk] += 1
        slug = fm.get("slug", "")
        slugs.append(slug)
        if slug and f"`{slug}`" not in idx and f"{slug}" not in idx:
            errors.append(f"{path.name}: slug {slug!r} missing from INDEX.md")
        try:
            order = int(fm.get("order", "0"))
            orders.append(order)
            num = int(path.name.split("-", 1)[0])
            if order != num:
                errors.append(f"{path.name}: order {order} != filename {num}")
        except ValueError:
            errors.append(f"{path.name}: order/filename not integer")
        nwords = body_words(text)
        if nwords < MIN_WORDS:
            errors.append(f"{path.name}: {nwords} words < {MIN_WORDS}")
        b = body(text)
        if DISCLAIMER_NEEDLE not in b.lower():
            errors.append(f"{path.name}: missing educational disclaimer")
        if SOURCES_NEEDLE not in b:
            errors.append(f"{path.name}: missing Sources heading")
        if citation_count(text) < 2:
            errors.append(f"{path.name}: fewer than 2 citation URLs")
        if longest_quote_words(text) > MAX_QUOTE_RUN:
            errors.append(f"{path.name}: quoted run looks like a copyright dump")
        hay = b.lower()
        for pat in BANNED + BANNED_BODY_ONLY:
            if re.search(pat, hay, re.I):
                errors.append(f"{path.name}: banned phrase /{pat}/")
        for needle in FIGURE_NEEDLES:
            if needle not in text:
                errors.append(f"{path.name}: missing SEO figure hook {needle!r}")
        if slug:
            asset_dir = ASSETS / slug
            if not asset_dir.is_dir() or not any(asset_dir.glob("*.svg")):
                errors.append(f"{path.name}: no SVG under assets/{slug}/")
            embed = EMBEDS / f"{slug}.md"
            if not embed.is_file():
                errors.append(f"{path.name}: missing embeds/{slug}.md")

    for svg in ASSETS.rglob("*.svg") if ASSETS.is_dir() else []:
        svg_text = svg.read_text(encoding="utf-8")
        if "<title" not in svg_text or "<desc" not in svg_text:
            errors.append(f"{svg.relative_to(ROOT)}: missing <title> or <desc>")

    for name in FIG_OPS_FILES:
        if not (ROOT / name).is_file():
            errors.append(f"missing ops file {name}")

    if orders and sorted(orders) != list(range(1, len(files) + 1)):
        errors.append(f"orders not 1..{len(files)}: {sorted(orders)}")

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    desk_bits = ", ".join(f"{k}={v}" for k, v in sorted(desks.items()))
    svg_n = len(list(ASSETS.rglob("*.svg"))) if ASSETS.is_dir() else 0
    print(f"OK: {len(files)} articles ({desk_bits}), {svg_n} SVG figures embedded")
    return 0


if __name__ == "__main__":
    sys.exit(main())
