#!/usr/bin/env python3
"""Structural QA for content/family-systems-therapy-history/.

Counts articles, required YAML, educational note, banned style phrases,
minimum words, INDEX slug match, graphics gates (<figure>, plates, era assets).
Exit 0 only if all gates pass.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ART = ROOT / "articles"
PLATES = ROOT / "plates"
ERA_ASSETS = ROOT / "assets" / "era"
INDEX = ROOT / "INDEX.md"
FIGURE_RE = re.compile(r'<figure class="wow-figure', re.I)
AI_FACE = re.compile(
    r"(ai[- ]generated|synthetic (?:face|likeness|portrait)|midjourney|stable diffusion)",
    re.I,
)
ALLOW_AI_MENTION = re.compile(
    r"(no ai[- ]generated|never generate|do not.*face|banned.*face|not a face|no likeness)",
    re.I,
)

REQUIRED_YAML = [
    "title",
    "slug",
    "meta_description",
    "tags",
    "type",
    "order",
    "portrait",
    "citations",
    "status",
    "voice_check",
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
    r"the family causes schizophrenia",
]

DISCLAIMER_NEEDLE = "not a treatment plan"
MIN_WORDS = 700
MIN_WORDS_ERA = 1200
MIN_WORDS_FIGURE = 1000
TARGET_ARTICLES = 44

FRONT_RE = re.compile(r"^---\n(.*?)\n---\n", re.S)

PERIOD_OBJECT_SLUGS = frozenset(
    {"child-guidance-invites-the-parents", "manuals-evidence-profession"}
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


def era_lead_ok(slug: str, lead: str) -> bool:
    if not lead.startswith("assets/era/"):
        return False
    if slug in PERIOD_OBJECT_SLUGS:
        return lead.endswith("lead-period-object.svg")
    return lead.endswith("lead-timeline.svg")


def main() -> int:
    files = sorted(ART.glob("*.md"))
    errors: list[str] = []
    if len(files) < 40:
        errors.append(f"article count {len(files)} < 40")
    if len(files) != TARGET_ARTICLES:
        errors.append(f"article count {len(files)} != {TARGET_ARTICLES} (manifest target)")

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
        if fm.get("status") not in {"publishable", "draft"}:
            errors.append(f"{path.name}: bad status {fm.get('status')!r}")
        if DISCLAIMER_NEEDLE not in text.lower():
            errors.append(f"{path.name}: missing educational note")
        if AI_FACE.search(text) and not ALLOW_AI_MENTION.search(text):
            errors.append(f"{path.name}: possible AI-face language")
        if not FIGURE_RE.search(text):
            errors.append(f"{path.name}: missing <figure> lead block")
        if fm.get("type") == "era":
            if fm.get("portrait_status") != "essay-only":
                errors.append(f"{path.name}: era portrait_status must be essay-only")
            slug = fm.get("slug", "")
            lead = fm.get("lead_asset", "")
            if not era_lead_ok(slug, lead):
                errors.append(f"{path.name}: era missing or wrong lead_asset")
        if fm.get("type") == "figure":
            if "figure_dates" not in fm:
                errors.append(f"{path.name}: figure missing figure_dates")
            ps = fm.get("portrait_status")
            if ps not in {"typographic", "cleared", "placeholder"}:
                errors.append(
                    f"{path.name}: figure portrait_status must be typographic|cleared|placeholder"
                )
            port = fm.get("portrait", "")
            if not str(port).startswith("plates/"):
                errors.append(f"{path.name}: figure portrait must point at plates/…")
        n = body_words(text)
        floor = (
            MIN_WORDS_ERA
            if fm.get("type") == "era"
            else MIN_WORDS_FIGURE
            if fm.get("type") == "figure"
            else MIN_WORDS
        )
        if n < floor:
            errors.append(f"{path.name}: {n} words < {floor} ({fm.get('type') or 'unknown'} target)")
        low = text.lower()
        for pat in BANNED:
            if re.search(pat, low):
                errors.append(f"{path.name}: banned phrase /{pat}/")
        slug = fm.get("slug", "")
        if slug:
            slugs.append(slug)

    if len(slugs) != len(set(slugs)):
        errors.append("duplicate slugs")

    idx = INDEX.read_text(encoding="utf-8")
    for slug in slugs:
        if slug not in idx:
            errors.append(f"INDEX.md missing slug {slug}")

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

    if not ERA_ASSETS.is_dir():
        errors.append("missing assets/era/ directory")
    else:
        for slug_dir in sorted(p for p in ERA_ASSETS.iterdir() if p.is_dir()):
            slug = slug_dir.name
            if slug in PERIOD_OBJECT_SLUGS:
                lead = slug_dir / "lead-period-object.svg"
                if not lead.is_file():
                    errors.append(f"missing {lead.relative_to(ROOT)}")
                rights = slug_dir / "RIGHTS.md"
                if not rights.is_file():
                    errors.append(f"missing {rights.relative_to(ROOT)}")
            else:
                lead = slug_dir / "lead-timeline.svg"
                if not lead.is_file():
                    errors.append(f"missing {lead.relative_to(ROOT)}")

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
        "RIGHTS.md",
        "GRAPHICS_INDEX.md",
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
