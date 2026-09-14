#!/usr/bin/env python3
"""Structural check for the staged buyfigs nursery/wholesale draft set."""
from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
DRAFTS = HERE / "drafts"
MIN_DRAFTS = 40
MIN_WORDS = 520
REQUIRED_STAGES = {"take", "mark", "pack", "hold", "ship", "land"}
KEEP_IDS = {"d12", "d19", "d35", "d45"}
SLOP = (
    "it's important to note",
    "whether you're a beginner",
    "in today's world",
    "in today’s world",
    "delve ",
    "unlock the",
    "comprehensive guide",
    "in the world of",
    "in conclusion",
    "game-changer",
    "supercharge",
    "tips and tricks",
    "essential for success",
)
MEDICAL = (
    "treat diabetes",
    "lowers blood sugar",
    "anti-inflammatory supplement",
    "medicinal use",
    "figs treat",
    "cure ",
    "dietary supplement",
    "for your health",
)
TOPIC_NEEDLES = {
    "packing": ("pack", "damp", "bundle", "box"),
    "labeling": ("label", "lot code", "packing slip"),
    "dormant": ("dormant", "lignified", "cooler"),
    "shipping": ("ship", "usps", "heat pack"),
    "not_medical": ("not medicine", "not a pharmacy", "not medical"),
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
    openings: dict[str, str] = {}
    ids: set[str] = set()
    blob = ""

    if len(files) < MIN_DRAFTS:
        errors.append(f"draft count {len(files)} < {MIN_DRAFTS}")

    for path in files:
        text = path.read_text(encoding="utf-8")
        blob += "\n" + text.lower()
        if "status: staged" not in text:
            errors.append(f"{path.name}: missing status: staged")
        if "lane: buyfigs" not in text:
            errors.append(f"{path.name}: missing lane: buyfigs")
        if "voice: human" not in text:
            errors.append(f"{path.name}: missing voice: human")
        stage = None
        did = None
        for line in text.splitlines():
            if line.startswith("stage:"):
                stage = line.split(":", 1)[1].strip()
                stages[stage] += 1
            if line.startswith("id:"):
                did = line.split(":", 1)[1].strip()
                ids.add(did)
        if stage not in REQUIRED_STAGES:
            errors.append(f"{path.name}: bad stage {stage!r}")
        body = body_of(text)
        n = len(re.findall(r"[A-Za-z0-9']+", body))
        words_all.append(n)
        if n < MIN_WORDS:
            errors.append(f"{path.name}: {n} words < {MIN_WORDS}")
        low = text.lower()
        for phrase in SLOP:
            if phrase in low:
                errors.append(f"{path.name}: slop phrase {phrase!r}")
        for phrase in MEDICAL:
            if phrase in low:
                errors.append(f"{path.name}: medical phrase {phrase!r}")
        first = re.sub(r"\s+", " ", body.strip())[:96]
        if first in openings:
            errors.append(f"{path.name}: opening collides with {openings[first]}")
        else:
            openings[first] = path.name

    missing_keep = KEEP_IDS - ids
    if missing_keep:
        errors.append(f"missing keep drafts: {sorted(missing_keep)}")

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
    print(f"unique_openings={len(openings)}/{len(files)}")
    if errors:
        print("FAIL")
        for e in errors:
            print(f"  {e}")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
