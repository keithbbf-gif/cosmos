#!/usr/bin/env python3
"""Editorial QA for the microbiome-supplements-landscape pack. Not a site runtime."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DRAFTS = ROOT / "drafts"
REQUIRED_ROOT = [
    "INDEX.md",
    "MANIFEST.md",
    "STYLE_GUIDE.md",
    "BIBLIOGRAPHY.md",
    "CLAIMS_GUARDRAILS.md",
    "PHOTO_NOTES.md",
    "WP_IMPORT.md",
    "README.md",
]
FM_KEYS = [
    "voice_check",
    "title",
    "slug",
    "meta_description",
    "summary",
    "tags",
    "era_focus",
    "wave",
    "citations",
    "sources_notes",
    "status",
    "legal_frame",
]
BANNED = re.compile(
    r"delve|leverage|\brobust\b|seamless|tapestry|underscore|"
    r"ever-evolving|rapidly evolving|it's important to note|"
    r"it is important to note|needless to say|whether you're|"
    r"in today's world|multifaceted|unpack the|navigate the complexities|"
    r"game-changer|cutting-edge|\bunlock\b|in conclusion|"
    r"gut health journey|balance your biome|"
    r"landscape",
    re.I,
)
# Folder/ops docs may say the word; drafts may not.
DISEASE_SKU = re.compile(
    r"prevents? (?:c\.?\s*diff|nec|ibd|cancer)|"
    r"cures? (?:depression|obesity|ibd)|"
    r"treats? your (?:gut|ibs|anxiety)|"
    r"\bpsychobiotic\b[^.!?\n]{0,40}\b(?:treats?|for depression|for anxiety)\b|"
    r"\b(?:take|start with)\s+\d+\s*(?:billion|million)?\s*cfu\b",
    re.I,
)
READER_DOSE = re.compile(
    r"\b(?:you should|you need to)\s+(?:take|start|swallow|dose)\b",
    re.I,
)
DISCLAIMER = re.compile(r"not medical advice", re.I)
PHOTO = re.compile(r"\*\*Photo:\*\*")
SOFT_FLOOR = 1000


def strip_fm(text: str) -> tuple[dict[str, str], str]:
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        return {}, text
    fm: dict[str, str] = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip()
    return fm, m.group(2)


def main() -> int:
    errors: list[str] = []
    notes: list[str] = []
    for name in REQUIRED_ROOT:
        if not (ROOT / name).is_file():
            errors.append(f"missing root file: {name}")

    drafts = sorted(DRAFTS.glob("*.md"))
    if len(drafts) < 40:
        errors.append(f"draft count {len(drafts)} < 40")
    slugs: list[tuple[str, str]] = []
    words: list[tuple[int, str]] = []
    for path in drafts:
        text = path.read_text(encoding="utf-8")
        fm, body = strip_fm(text)
        for key in FM_KEYS:
            if key not in fm:
                errors.append(f"{path.name}: missing {key}")
        if fm.get("voice_check") != "edited":
            errors.append(f"{path.name}: voice_check is not edited")
        if fm.get("status") != "draft":
            errors.append(f"{path.name}: status is not draft")
        if fm.get("legal_frame") != "educational-research":
            errors.append(f"{path.name}: legal_frame not educational-research")
        if not PHOTO.search(body):
            errors.append(f"{path.name}: missing photo slot")
        if not DISCLAIMER.search(body):
            errors.append(f"{path.name}: missing disclaimer language")
        slug = fm.get("slug", "").strip("\"'")
        if slug:
            slugs.append((slug, path.name))
        w = len(body.split())
        words.append((w, path.name))
        if w < SOFT_FLOOR:
            errors.append(f"{path.name}: {w} words < {SOFT_FLOOR} stub floor")
        hit = BANNED.search(body)
        if hit:
            errors.append(f"{path.name}: banned phrase {hit.group(0)!r}")
        bad = DISEASE_SKU.search(body)
        if bad:
            errors.append(f"{path.name}: disease-SKU pattern {bad.group(0)!r}")
        dose = READER_DOSE.search(body)
        if dose:
            errors.append(f"{path.name}: reader-dose pattern {dose.group(0)!r}")

    seen: dict[str, str] = {}
    for slug, name in slugs:
        if slug in seen:
            errors.append(f"duplicate slug {slug}: {seen[slug]} and {name}")
        seen[slug] = name

    if words:
        ws = [w for w, _ in words]
        notes.append(f"drafts={len(drafts)}")
        notes.append(f"word_min={min(ws)} ({min(words)[1]})")
        notes.append(f"word_max={max(ws)} ({max(words)[1]})")
        notes.append(f"word_mean={sum(ws) // len(ws)}")
        notes.append(f"slugs={len(seen)}")

    print("PACK QA")
    for n in notes:
        print(f"  {n}")
    if errors:
        print("FAIL")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
