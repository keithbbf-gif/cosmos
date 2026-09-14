#!/usr/bin/env python3
"""Structural QA for content/voice-disorders-heritage/.

Counts articles, required YAML, educational line, banned style phrases,
minimum words, INDEX slug match. Exit 0 only if all gates pass.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ART = ROOT / "articles"
INDEX = ROOT / "INDEX.md"

REQUIRED_YAML = [
    "title",
    "slug",
    "series",
    "type",
    "tags",
    "portrait",
    "portrait_status",
    "voice_check",
    "audience",
    "stage",
]

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
    r"in this article we will explore",
    r"\btapestry\b",
    r"\bplethora\b",
    r"gold-standard treatment",
    r"try this at home",
    r"self-treat",
    r"holistic approach",
]

# "robust" / "landscape" banned in body prose; STYLE_GUIDE may name them.
BANNED_BODY_ONLY = [
    r"\brobust\b",
    r"\blandscape\b",
    r"\bseamless\b",
    r"\bempower(?:s|ed|ing)?\b",
]

DISCLAIMER_NEEDLE = "not a treatment plan"
PLACEHOLDER_NEEDLE = "**Portrait placeholder.**"
TARGET_ARTICLES = 44
MIN_WORDS_ERA = 650
MIN_WORDS_PROFILE = 420

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


def body_words(text: str) -> int:
    m = FRONT_RE.match(text)
    body = text[m.end() :] if m else text
    return len(re.findall(r"[A-Za-z0-9']+", body))


def main() -> int:
    files = sorted(ART.glob("*.md"))
    errors: list[str] = []
    if len(files) != TARGET_ARTICLES:
        errors.append(f"article count {len(files)} != {TARGET_ARTICLES}")

    slugs: list[str] = []
    types = {"era": 0, "profile": 0}
    for path in files:
        text = path.read_text(encoding="utf-8")
        fm = parse_front(text)
        for key in REQUIRED_YAML:
            if key not in fm:
                errors.append(f"{path.name}: missing YAML {key}")
        if fm.get("series") != "slpwow-voice-disorders-heritage":
            errors.append(f"{path.name}: bad series {fm.get('series')!r}")
        if fm.get("voice_check") != "human":
            errors.append(f"{path.name}: voice_check is not human")
        if fm.get("stage") != "draft":
            errors.append(f"{path.name}: stage is not draft")
        if fm.get("audience") != "slpwow":
            errors.append(f"{path.name}: audience is not slpwow")
        typ = fm.get("type")
        if typ not in {"era", "profile"}:
            errors.append(f"{path.name}: bad type {typ!r}")
        else:
            types[typ] += 1
        if typ == "profile" and "figure_dates" not in fm:
            errors.append(f"{path.name}: profile missing figure_dates")
        if DISCLAIMER_NEEDLE not in text.lower():
            errors.append(f"{path.name}: missing educational note")
        if typ == "profile" and fm.get("portrait_status") == "placeholder":
            if PLACEHOLDER_NEEDLE not in text:
                errors.append(f"{path.name}: placeholder status without placeholder block")
        n = body_words(text)
        floor = MIN_WORDS_ERA if typ == "era" else MIN_WORDS_PROFILE
        if n < floor:
            errors.append(f"{path.name}: {n} words < {floor} ({typ})")
        low = text.lower()
        # skip YAML
        body = text[FRONT_RE.match(text).end() :] if FRONT_RE.match(text) else text
        blow = body.lower()
        for pat in BANNED:
            if re.search(pat, blow):
                errors.append(f"{path.name}: banned phrase /{pat}/")
        for pat in BANNED_BODY_ONLY:
            if re.search(pat, blow):
                errors.append(f"{path.name}: banned body phrase /{pat}/")
        slug = fm.get("slug", "")
        if slug:
            slugs.append(slug)
            stem = path.name.split("-", 1)[-1].removesuffix(".md")
            if slug != stem and not path.name.endswith(slug + ".md"):
                # filename is NN-slug.md
                if path.name != f"{path.name[:3]}{slug}.md":
                    expected_tail = slug + ".md"
                    if not path.name.endswith(expected_tail):
                        errors.append(f"{path.name}: filename/slug mismatch {slug}")

    if len(slugs) != len(set(slugs)):
        errors.append("duplicate slugs")

    idx = INDEX.read_text(encoding="utf-8")
    for slug in slugs:
        if slug not in idx:
            errors.append(f"INDEX.md missing slug {slug}")

    if types["era"] != 16:
        errors.append(f"era count {types['era']} != 16")
    if types["profile"] != 28:
        errors.append(f"profile count {types['profile']} != 28")

    ops = [
        "INDEX.md",
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

    print(f"articles: {len(files)} (era {types['era']}, profile {types['profile']})")
    print(f"errors: {len(errors)}")
    for e in errors:
        print(f"FAIL {e}")
    if errors:
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
