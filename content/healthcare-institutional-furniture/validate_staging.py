#!/usr/bin/env python3
"""Validate staged healthcare / institutional furniture magazine drafts."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DRAFTS = ROOT / "drafts"
MIN_ESSAYS = 40
MIN_WORDS = 1800
MAX_WORDS = 2600
BANNED = re.compile(
    r"\b(delve|leverage|robust|unlock|cutting-edge|game-changer|"
    r"ever-evolving|underscore|seamless)\b|"
    r"elevate your space|it's important to note|its important to note|"
    r"in today's rapidly|whether you're|in conclusion|"
    r"shop the look|related products|add to cart|call for quote",
    re.I,
)
REQUIRED_FM = (
    "title",
    "slug",
    "chapter",
    "series",
    "status",
    "voice_check",
    "lane",
    "period",
    "regions",
    "word_target",
    "figures",
    "meta_description",
    "tags",
    "citations",
)
DISCLAIMER = re.compile(
    r"Educational history of healthcare and nursing-home furniture",
    re.I,
)


def body_words(text: str) -> int:
    parts = re.split(r"^---\s*$", text, flags=re.M)
    body = parts[2] if len(parts) > 2 else text
    body = re.split(r"^## (Notes|Figure plan)\s*$", body, flags=re.M)[0]
    return len(re.findall(r"\b[\w’'-]+\b", body))


def front_matter(text: str) -> str:
    parts = re.split(r"^---\s*$", text, flags=re.M)
    return parts[1] if len(parts) > 2 else ""


def main() -> int:
    files = sorted(DRAFTS.glob("*.md"))
    errors: list[str] = []
    rows: list[tuple[str, int]] = []
    if len(files) < MIN_ESSAYS:
        errors.append(f"essay count {len(files)} < {MIN_ESSAYS}")
    for path in files:
        text = path.read_text(encoding="utf-8")
        fm = front_matter(text)
        n = body_words(text)
        rows.append((path.name, n))
        for key in REQUIRED_FM:
            if not re.search(rf"^{key}\s*:", fm, re.M):
                errors.append(f"{path.name}: missing YAML {key}")
        if "status: staged" not in fm:
            errors.append(f"{path.name}: status is not staged")
        if not re.search(r"^voice_check:\s*(human|edited)\s*$", fm, re.M):
            errors.append(f"{path.name}: voice_check must be human or edited")
        if "lane: bbf-furniture" not in fm:
            errors.append(f"{path.name}: lane is not bbf-furniture")
        if n < MIN_WORDS or n > MAX_WORDS:
            errors.append(f"{path.name}: body words {n} not in {MIN_WORDS}-{MAX_WORDS}")
        if "## Notes" not in text:
            errors.append(f"{path.name}: missing ## Notes")
        if "## Figure plan" not in text:
            errors.append(f"{path.name}: missing ## Figure plan")
        figs = re.findall(r"\*\*Fig\.", text)
        if not (4 <= len(figs) <= 7):
            errors.append(f"{path.name}: figure count {len(figs)} not in 4-7")
        if not DISCLAIMER.search(text):
            errors.append(f"{path.name}: missing educational disclaimer")
        hit = BANNED.search(text)
        if hit:
            errors.append(f"{path.name}: banned phrase {hit.group(0)!r}")
        if re.search(r"\b(shop our|buy now|add to cart|call for quote)\b", text, re.I):
            errors.append(f"{path.name}: product language")
        if re.search(r"\bCOSMOS\b|\bWebsite-GC\b|\bvoice_check\b", text.split("---", 2)[-1]):
            # process talk in body after front matter
            body_only = re.split(r"^---\s*$", text, flags=re.M)
            if len(body_only) > 2 and re.search(
                r"\b(COSMOS|Website-GC)\b", body_only[2].split("## Notes")[0]
            ):
                errors.append(f"{path.name}: process talk in body")
    print(f"essays: {len(files)}")
    for name, n in rows:
        flag = "OK" if MIN_WORDS <= n <= MAX_WORDS else "WORD"
        print(f"  {flag} {n:5d}  {name}")
    if errors:
        print("FAIL")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
