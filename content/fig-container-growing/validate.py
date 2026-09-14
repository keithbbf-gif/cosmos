#!/usr/bin/env python3
"""Structural check for the staged fig container-growing draft set."""
from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
MIN_DRAFTS = 40
MIN_WORDS = 400
SLOP = (
    "it's important to note",
    "whether you're a beginner",
    "in today's world",
    "delve ",
    "unlock the",
    "comprehensive guide",
    "in the world of",
    "game-changer",
    "tips and tricks",
    "in conclusion",
)


def body_of(text: str) -> str:
    if not text.startswith("---"):
        return text
    end = text.find("\n---", 3)
    return text[end + 4 :] if end != -1 else text


def main() -> int:
    files = sorted(HERE.glob("[0-9][0-9]-*.md"))
    errors: list[str] = []
    words_all: list[int] = []

    if len(files) < MIN_DRAFTS:
        errors.append(f"draft count {len(files)} < {MIN_DRAFTS}")

    for path in files:
        text = path.read_text(encoding="utf-8")
        if "status: staged" not in text:
            errors.append(f"{path.name}: missing status: staged")
        if "meta_description:" not in text:
            errors.append(f"{path.name}: missing meta_description")
        if "slug:" not in text:
            errors.append(f"{path.name}: missing slug")
        if "<figure>" not in text:
            errors.append(f"{path.name}: missing <figure> SEO block")
        if "images:" not in text:
            errors.append(f"{path.name}: missing images: shot list")
        if "orchard_slot:" not in text:
            errors.append(f"{path.name}: missing orchard_slot comment")
        body = body_of(text).lower()
        for phrase in SLOP:
            if phrase in body:
                errors.append(f"{path.name}: slop phrase {phrase!r}")
        n = len(re.findall(r"[A-Za-z0-9']+", body_of(text)))
        words_all.append(n)
        if n < MIN_WORDS:
            errors.append(f"{path.name}: short draft {n} words < {MIN_WORDS}")

    img_root = HERE / "assets" / "images"
    if not (img_root / "_download_meta.json").is_file():
        errors.append("missing assets/images/_download_meta.json (run fig_pack_rasters.py container)")

    if errors:
        for e in errors:
            print("ERROR", e)
        return 1

    print(
        f"OK {len(files)} drafts, words min/mean/max:",
        min(words_all),
        sum(words_all) // len(words_all),
        max(words_all),
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
