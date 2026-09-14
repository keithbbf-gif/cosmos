#!/usr/bin/env python3
"""Inventory + voice/claims gates for protein-supplements-label-literacy. Not a publisher."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LESSONS = sorted(ROOT.glob("stage-*/PSL-*.md"))

LOCK_PRODUCT = (
    "This draft does not claim that any protein powder diagnoses, "
    "treats, cures, or prevents any disease."
)
LOCK_LABEL = (
    "Under DSHEA, a dietary supplement label may not claim to "
    "diagnose, treat, cure, or prevent any disease."
)

REQUIRED_FM = (
    "status: draft",
    "voice_check: edited",
    "jurisdiction: US-FDA-DSHEA",
    "disease_claims: forbidden",
    "medical_advice: none",
)

BANS = (
    r"\bdelve\b",
    r"\brobust\b",
    r"\bleverage\b",
    r"\bunlock\b",
    r"cutting-edge",
    r"game-chang",
    r"In conclusion",
    r"\bFurthermore\b",
    r"\bMoreover\b",
    r"Whether you're",
    r"rapidly evolving",
    r"It's important to note",
    r"\bnavigate\b",
    r"tapestry",
    r"plethora",
    r"\butilize\b",
    r"\bharness\b",
    r"elevate your",
    r"the future of",
    r"at the forefront",
    r"holistic approach",
    r"\bempower\b",
    r"in this article we will",
    r"\blandscape\b",
)

REFUSAL_MARK = "## What this draft will not say"


def split_front(text: str) -> tuple[str, str]:
    if not text.startswith("---\n"):
        return "", text
    end = text.find("\n---\n", 4)
    if end < 0:
        return "", text
    return text[: end + 5], text[end + 5 :]


def scan_body(path: Path, text: str) -> list[str]:
    issues: list[str] = []
    _, body = split_front(text)
    refusal = body.find(REFUSAL_MARK)
    scan = body if refusal < 0 else body[:refusal]
    for pat in BANS:
        if re.search(pat, scan, re.I):
            issues.append(f"{path.name}: style ban {pat}")
    return issues


def main() -> int:
    issues: list[str] = []
    words_total = 0
    print(f"lessons={len(LESSONS)} (need >= 40)")
    if len(LESSONS) < 40:
        issues.append(f"count {len(LESSONS)} < 40")
    for path in LESSONS:
        text = path.read_text(encoding="utf-8")
        _, body = split_front(text)
        words = len(re.findall(r"\b[\w''-]+\b", body))
        words_total += words
        print(f"  {words:5d}  {path.name}")
        if words < 450:
            issues.append(f"{path.name}: {words} words < 450")
        for key in REQUIRED_FM:
            if key not in text:
                issues.append(f"{path.name}: missing {key}")
        if LOCK_PRODUCT not in text or LOCK_LABEL not in text:
            issues.append(f"{path.name}: missing lock sentences")
        issues.extend(scan_body(path, text))
    print(f"words_total={words_total}")
    print(f"issues={len(issues)}")
    for item in issues:
        print(f"FAIL {item}")
    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
