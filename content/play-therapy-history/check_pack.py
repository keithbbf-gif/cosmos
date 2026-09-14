#!/usr/bin/env python3
"""Structural QA for content/play-therapy-history/.

Counts drafts, required YAML, educational note, claims box, banned style
and protocol phrases, minimum words, INDEX slug match. Exit 0 only if
all gates pass.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ART = ROOT / "drafts"
INDEX = ROOT / "INDEX.md"

REQUIRED_YAML = [
    "title",
    "slug",
    "meta_description",
    "tags",
    "type",
    "stage",
    "order",
    "portrait",
    "citations",
    "status",
    "voice_check",
    "claims_posture",
    "last_verified",
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
    r"in this article we will explore",
    r"\btapestry\b",
    r"\bplethora\b",
    r"gold-standard treatment",
    r"try this at home",
    r"self-treat",
    r"set up a playroom",
    r"here are the toys you need",
    r"special play time at home",
    r"\bholistic approach\b",
    r"journey of healing",
]

DISCLAIMER_NEEDLE = "not a treatment plan"
CLAIMS_NEEDLE = "## claims box"
MIN_WORDS = 800
MIN_WORDS_ERA = 1200
MIN_WORDS_FIGURE = 1000
MIN_WORDS_READER = 800
MIN_ARTICLES = 40

FRONT_RE = re.compile(r"^---\n(.*?)\n---\n", re.S)


def parse_front(text: str) -> dict[str, str]:
    m = FRONT_RE.match(text)
    if not m:
        return {}
    block = m.group(1)
    data: dict[str, str] = {}
    for line in block.splitlines():
        if ":" in line and not line.startswith(" ") and not line.startswith("-"):
            k, v = line.split(":", 1)
            data[k.strip()] = v.strip().strip('"')
    return data


def body_words(text: str) -> int:
    m = FRONT_RE.match(text)
    body = text[m.end() :] if m else text
    return len(re.findall(r"[A-Za-z0-9']+", body))


def main() -> int:
    files = sorted(ART.glob("*.md"))
    errors: list[str] = []
    if len(files) < MIN_ARTICLES:
        errors.append(f"article count {len(files)} < {MIN_ARTICLES}")

    slugs: list[str] = []
    for path in files:
        text = path.read_text(encoding="utf-8")
        fm = parse_front(text)
        for key in REQUIRED_YAML:
            if key not in fm:
                errors.append(f"{path.name}: missing YAML {key}")
        vc = fm.get("voice_check")
        if vc not in {"human", "edited"}:
            errors.append(f"{path.name}: voice_check must be human or edited (got {vc!r})")
        if fm.get("status") not in {"draft", "publishable"}:
            errors.append(f"{path.name}: bad status {fm.get('status')!r}")
        if fm.get("claims_posture") != "educational-therapy-history":
            errors.append(f"{path.name}: claims_posture must be educational-therapy-history")
        if DISCLAIMER_NEEDLE not in text.lower():
            errors.append(f"{path.name}: missing educational note")
        if CLAIMS_NEEDLE not in text.lower():
            errors.append(f"{path.name}: missing claims box")
        n = body_words(text)
        kind = fm.get("type") or "unknown"
        if kind == "era":
            floor = MIN_WORDS_ERA
        elif kind == "figure":
            floor = MIN_WORDS_FIGURE
        elif kind == "reader":
            floor = MIN_WORDS_READER
        else:
            floor = MIN_WORDS
        if n < floor:
            errors.append(f"{path.name}: {n} words < {floor} ({kind} target)")
        low = text.lower()
        for pat in BANNED:
            if re.search(pat, low):
                errors.append(f"{path.name}: banned phrase /{pat}/")
        slug = fm.get("slug", "")
        if slug:
            slugs.append(slug)

    if len(slugs) != len(set(slugs)):
        errors.append("duplicate slugs")

    idx = INDEX.read_text(encoding="utf-8") if INDEX.is_file() else ""
    for slug in slugs:
        if slug not in idx:
            errors.append(f"INDEX.md missing slug {slug}")

    ops = [
        "INDEX.md",
        "MANIFEST.md",
        "STYLE_GUIDE.md",
        "CLAIMS_GUARDRAILS.md",
        "BIBLIOGRAPHY.md",
        "PORTRAIT_SOURCES.md",
        "PHOTO_NOTES.md",
        "WP_IMPORT.md",
        "README.md",
    ]
    for name in ops:
        if not (ROOT / name).is_file():
            errors.append(f"missing ops file {name}")

    print(f"articles: {len(files)}")
    print(f"errors: {len(errors)}")
    for e in errors:
        print(f"FAIL {e}")
    if errors:
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
