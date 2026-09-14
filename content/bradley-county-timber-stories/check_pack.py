#!/usr/bin/env python3
"""Structural QA for content/bradley-county-timber-stories/.

Counts drafts, required YAML, banned style phrases, word band, commerce flag,
INDEX slug match. Exit 0 only if all gates pass.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DRAFTS = ROOT / "drafts"
INDEX = ROOT / "INDEX.md"
SLUGS_JSON = ROOT / "writer-slugs.json"

REQUIRED_YAML = [
    "title",
    "slug",
    "series",
    "status",
    "voice_check",
    "reading_order",
    "word_target",
    "lane",
    "commerce",
    "tone",
    "era",
    "place",
]

BANNED = [
    r"\bdelve(?:s|d|ing)?\b",
    r"in today's rapidly",
    r"it's important to note",
    r"\brobust\b",
    r"\bleverage\b",
    r"\bunlock(?:s|ed|ing)?\b",
    r"cutting-edge",
    r"game-chang",
    r"\bin conclusion\b",
    r"whether you're a",
    r"\btapestry\b",
    r"shop now",
    r"add to cart",
    r"hidden gem",
    r"best-kept secret",
    r"\bour craftsmen\b",
]

MIN_WORDS = 1400
MAX_WORDS = 2200
TARGET_DRAFTS = 44

FRONT_RE = re.compile(r"^---\n(.*?)\n---\n", re.S)


def parse_front(text: str) -> dict[str, str]:
    m = FRONT_RE.match(text)
    if not m:
        return {}
    data: dict[str, str] = {}
    for line in m.group(1).splitlines():
        if ":" in line and not line.startswith(" ") and not line.startswith("-"):
            k, v = line.split(":", 1)
            data[k.strip()] = v.strip().strip('"')
    return data


def body_main(text: str) -> str:
    m = FRONT_RE.match(text)
    body = text[m.end() :] if m else text
    parts = re.split(r"\n## Sources\n", body, maxsplit=1)
    return parts[0]


def body_words(text: str) -> int:
    return len(re.findall(r"[A-Za-z0-9']+", body_main(text)))


def index_slugs() -> set[str]:
    text = INDEX.read_text(encoding="utf-8")
    return set(re.findall(r"`([a-z0-9-]+)`\s*$", text, re.M))


def canonical_slugs() -> set[str]:
    import json

    data = json.loads(SLUGS_JSON.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return {str(s) for s in data}
    if isinstance(data, dict) and "slugs" in data:
        return {str(s) for s in data["slugs"]}
    return set()


def main() -> int:
    files = sorted(DRAFTS.glob("*.md"))
    errors: list[str] = []

    if len(files) != TARGET_DRAFTS:
        errors.append(f"draft count {len(files)} != {TARGET_DRAFTS}")

    idx = index_slugs()
    canon = canonical_slugs()
    seen_slugs: list[str] = []

    for path in files:
        text = path.read_text(encoding="utf-8")
        fm = parse_front(text)
        for key in REQUIRED_YAML:
            if key not in fm:
                errors.append(f"{path.name}: missing YAML {key}")

        slug = fm.get("slug", "")
        if slug:
            seen_slugs.append(slug)
            if slug not in idx:
                errors.append(f"{path.name}: slug {slug} not in INDEX")
            if canon and slug not in canon:
                errors.append(f"{path.name}: slug {slug} not in writer-slugs.json")

        vc = fm.get("voice_check", "")
        if vc not in ("human", "edited"):
            errors.append(f"{path.name}: voice_check must be human or edited, got {vc!r}")

        if fm.get("commerce", "").lower() != "false":
            errors.append(f"{path.name}: commerce must be false")

        if fm.get("tone", "") != "ken-burns":
            errors.append(f"{path.name}: tone must be ken-burns")

        main = body_main(text)
        for pat in BANNED:
            if re.search(pat, main, re.I):
                errors.append(f"{path.name}: banned phrase /{pat}/")

        wc = body_words(text)
        if wc < MIN_WORDS or wc > MAX_WORDS:
            errors.append(f"{path.name}: body words {wc} outside {MIN_WORDS}-{MAX_WORDS}")

    if len(seen_slugs) != len(set(seen_slugs)):
        errors.append("duplicate slugs in drafts")

    if canon and set(seen_slugs) != canon:
        missing = canon - set(seen_slugs)
        extra = set(seen_slugs) - canon
        if missing:
            errors.append(f"writer-slugs missing drafts: {sorted(missing)[:5]}")
        if extra:
            errors.append(f"extra draft slugs: {sorted(extra)[:5]}")

    if errors:
        print("FAIL")
        for e in errors:
            print(" -", e)
        return 1

    print(f"PASS ({len(files)} drafts, band {MIN_WORDS}-{MAX_WORDS}, voice_check human|edited)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
