#!/usr/bin/env python3
"""Structural check for the staged fig-hardiness draft set."""
from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
DRAFTS = HERE / "drafts"
MIN_DRAFTS = 40
MIN_WORDS = 480
SLOP = (
    "it's important to note",
    "whether you're a beginner",
    "in today's world",
    "delve ",
    "unlock the",
    "comprehensive guide",
    "in the world of",
)
REQUIRED_STAGES = {"ground", "choose", "wrap", "hold", "open"}
TOPIC_NEEDLES = {
    "hardiness": ("hardiness", "hardy", "dieback", "10°f", "15°f"),
    "wrapping": ("wrap", "burlap", "cage", "tarp"),
    "in_ground": ("in-ground", "in the ground"),
    "pot": ("pot", "garage"),
    "zone7": ("zone 7", "7a", "7b"),
    "zone9": ("zone 9", "9a"),
    "zone8a": ("8a",),
}


def body_of(text: str) -> str:
    if not text.startswith("---"):
        return text
    end = text.find("\n---", 3)
    return text[end + 4 :] if end != -1 else text


def main() -> int:
    files = sorted(DRAFTS.glob("d*.md"))
    errors: list[str] = []
    words_all: list[int] = []
    stages: Counter[str] = Counter()
    blob = ""

    if len(files) < MIN_DRAFTS:
        errors.append(f"draft count {len(files)} < {MIN_DRAFTS}")

    for path in files:
        text = path.read_text(encoding="utf-8")
        blob += "\n" + text.lower()
        if "status: staged" not in text:
            errors.append(f"{path.name}: missing status: staged")
        if "focus: 8a" not in text:
            errors.append(f"{path.name}: missing focus: 8a")
        stage = None
        for line in text.splitlines():
            if line.startswith("stage:"):
                stage = line.split(":", 1)[1].strip()
                stages[stage] += 1
                break
        if stage not in REQUIRED_STAGES:
            errors.append(f"{path.name}: bad stage {stage!r}")
        n = len(re.findall(r"[A-Za-z0-9']+", body_of(text)))
        words_all.append(n)
        if n < MIN_WORDS:
            errors.append(f"{path.name}: {n} words < {MIN_WORDS}")
        if "<figure>" not in text:
            errors.append(f"{path.name}: missing <figure> block")
        if "figcaption>" not in text:
            errors.append(f"{path.name}: missing SEO figcaption")
        low = text.lower()
        for phrase in SLOP:
            if phrase in low:
                errors.append(f"{path.name}: slop phrase {phrase!r}")

    for label, needles in TOPIC_NEEDLES.items():
        if not any(n in blob for n in needles):
            errors.append(f"missing topic coverage: {label}")

    missing_stages = REQUIRED_STAGES - set(stages)
    if missing_stages:
        errors.append(f"missing stages: {sorted(missing_stages)}")

    print(f"drafts={len(files)}")
    print(f"words_min={min(words_all) if words_all else 0}")
    print(f"words_max={max(words_all) if words_all else 0}")
    print(f"words_total={sum(words_all)}")
    print(f"stages={dict(stages)}")
    if errors:
        print("FAIL")
        for e in errors:
            print(f"  {e}")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
