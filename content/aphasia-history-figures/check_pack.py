#!/usr/bin/env python3
"""Structural QA for content/aphasia-history-figures/.

Counts articles, required YAML, educational note, banned style phrases,
minimum words, INDEX slug match. Exit 0 only if all gates pass.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ART = ROOT / "articles"
PLATES = ROOT / "plates"
INDEX = ROOT / "INDEX.md"
FIGURE_RE = re.compile(r'<figure class="slpwow-figure', re.I)

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

# "robust" and "seamless" banned as voice, but allow bibliographic titles if any
BANNED_VOICE = [
    r"healthcare landscape",
    r"holistic approach",
]

DISCLAIMER_NEEDLE = "not a treatment plan"
MIN_WORDS_ERA = 600
MIN_WORDS_PROFILE = 450
TARGET_ARTICLES = 45
SERIES = "slpwow-aphasia-history-figures"

FRONT_RE = re.compile(r"^---\n(.*?)\n---\n", re.S)
AI_FACE = re.compile(r"(ai[- ]generated|synthetic (?:face|likeness|portrait)|midjourney|stable diffusion)", re.I)


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
        if fm.get("type") == "profile":
            ps = fm.get("portrait_status", "")
            if ps not in {"cleared", "placeholder"}:
                errors.append(f"{path.name}: profile portrait_status must be cleared or placeholder")
            portrait = fm.get("portrait", "").strip('"')
            if not portrait.startswith("plates/"):
                errors.append(f"{path.name}: profile portrait must point at plates/…")
            elif not (ROOT / portrait).is_file():
                errors.append(f"{path.name}: portrait path missing on disk: {portrait}")
            if not FIGURE_RE.search(text):
                errors.append(f"{path.name}: profile missing <figure> portrait block")
        elif fm.get("type") == "era":
            if fm.get("portrait") not in {"null", ""}:
                errors.append(f"{path.name}: era portrait YAML must be null")
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
            expected = path.name.split("-", 1)[-1].removesuffix(".md")
            # files are NN-slug.md
            file_slug = re.sub(r"^\d+-", "", path.stem)
            if slug != file_slug:
                errors.append(f"{path.name}: slug {slug!r} != filename {file_slug!r}")
        if fm.get("order"):
            orders.append(fm["order"])

    if len(slugs) != len(set(slugs)):
        errors.append("duplicate slugs")
    if len(orders) != len(set(orders)):
        errors.append("duplicate order fields")

    # plates/: one RIGHTS.md per plate folder; rasters only under plates/
    if not PLATES.is_dir():
        errors.append("missing plates/ directory")
    else:
        for plate_dir in sorted(p for p in PLATES.iterdir() if p.is_dir()):
            rights = plate_dir / "RIGHTS.md"
            if not rights.is_file():
                errors.append(f"missing {rights.relative_to(ROOT)}")
            elif "ai_generated | no" not in rights.read_text(encoding="utf-8"):
                errors.append(f"{rights.relative_to(ROOT)} must declare ai_generated | no")
            plate_files = list(plate_dir.glob("plate.*"))
            if len(plate_files) != 1:
                errors.append(f"{plate_dir.name}: expected exactly one plate.* file, got {len(plate_files)}")
        for img in ROOT.rglob("*"):
            if img.suffix.lower() not in {".jpg", ".jpeg", ".png", ".gif", ".webp"}:
                continue
            rel = img.relative_to(ROOT)
            if rel.parts[0] != "plates":
                errors.append(f"raster outside plates/: {rel}")

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
