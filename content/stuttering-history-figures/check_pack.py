#!/usr/bin/env python3
"""Structural QA for content/stuttering-history-figures/.

Counts articles, required YAML, educational note, banned style phrases,
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
    "order",
    "meta_description",
    "portrait",
    "portrait_status",
    "voice_check",
    "audience",
    "stage",
    "last_verified",
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
    r"whether you’re a",
    r"in this article we will explore",
    r"\btapestry\b",
    r"\bplethora\b",
    r"gold-standard treatment",
    r"try this at home",
    r"self-treat",
    r"book with us",
]

BANNED_VOICE = [
    r"healthcare landscape",
    r"holistic approach",
]

DISCLAIMER_NEEDLE = "not a treatment plan"
MIN_WORDS_ERA = 600
MIN_WORDS_PROFILE = 450
TARGET_ARTICLES = 45
SERIES = "slpwow-stuttering-history-figures"

FRONT_RE = re.compile(r"^---\n(.*?)\n---\n", re.S)
AI_FACE = re.compile(
    r"(ai[- ]generated|synthetic (?:face|likeness|portrait)|midjourney|stable diffusion)",
    re.I,
)


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
    if len(files) != TARGET_ARTICLES:
        errors.append(f"article count {len(files)} != {TARGET_ARTICLES}")

    idx = INDEX.read_text(encoding="utf-8") if INDEX.is_file() else ""
    slugs: list[str] = []
    orders: list[str] = []

    for path in files:
        text = path.read_text(encoding="utf-8")
        fm = parse_front(text)
        for key in REQUIRED_YAML:
            if key not in fm:
                errors.append(f"{path.name}: missing YAML {key}")
        if fm.get("voice_check") != "human":
            errors.append(f"{path.name}: voice_check is not human")
        if fm.get("stage") != "draft":
            errors.append(f"{path.name}: stage must be draft (got {fm.get('stage')!r})")
        if fm.get("series") != SERIES:
            errors.append(f"{path.name}: bad series {fm.get('series')!r}")
        if fm.get("audience") != "slpwow":
            errors.append(f"{path.name}: audience must be slpwow")
        if fm.get("portrait") not in {"null", ""}:
            errors.append(f"{path.name}: this pack is notes-only; portrait must be null")
        if fm.get("type") == "profile" and fm.get("portrait_status") not in {"note"}:
            errors.append(f"{path.name}: profile portrait_status must be note")
        if fm.get("type") == "era" and fm.get("portrait_status") not in {"essay-only"}:
            errors.append(f"{path.name}: era portrait_status must be essay-only")
        if fm.get("type") == "profile" and "figure_dates" not in fm:
            errors.append(f"{path.name}: profile missing figure_dates")
        if DISCLAIMER_NEEDLE not in text.lower():
            errors.append(f"{path.name}: missing educational note")
        if AI_FACE.search(text) and "do not" not in text.lower():
            errors.append(f"{path.name}: possible AI-face language")
        n = body_words(text)
        floor = MIN_WORDS_ERA if fm.get("type") == "era" else MIN_WORDS_PROFILE
        if n < floor:
            errors.append(f"{path.name}: {n} words < {floor} ({fm.get('type') or 'unknown'})")
        low = text.lower()
        for pat in BANNED + BANNED_VOICE:
            if re.search(pat, low):
                errors.append(f"{path.name}: banned phrase /{pat}/")
        slug = fm.get("slug", "")
        if slug:
            slugs.append(slug)
            if slug not in idx:
                errors.append(f"INDEX.md missing slug {slug}")
            file_slug = re.sub(r"^\d+-", "", path.stem)
            if slug != file_slug:
                errors.append(f"{path.name}: slug {slug!r} != filename {file_slug!r}")
        if fm.get("order"):
            orders.append(fm["order"])

    if len(slugs) != len(set(slugs)):
        errors.append("duplicate slugs")
    if len(orders) != len(set(orders)):
        errors.append("duplicate order fields")

    for img in ROOT.rglob("*"):
        if img.suffix.lower() in {".jpg", ".jpeg", ".png", ".gif", ".webp"}:
            errors.append(f"image file not allowed in this notes-only pack: {img.relative_to(ROOT)}")

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
