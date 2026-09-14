#!/usr/bin/env python3
"""Lint staged vitamin-history drafts against CLAIMS_GUARDRAILS."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MIN_DRAFTS = 40
MIN_WORDS = 420
SERIES = "vitamins-history-claims-guarded"

REQUIRED_FRONT = {
    "series": SERIES,
    "status": "staged",
    "stage": "claims-guarded",
    "voice": "human",
    "voice_check": "edited",
    "claims_class": "history-education",
    "dshea": "no-disease-claim",
    "product_claim": "none",
    "structure_function": "none",
    "audience": "general-adult",
    "lint": "claims-lint",
}

DISCLAIMER = (
    "Staged historical education, not labeling. This draft is not a "
    "dietary-supplement label, not a product, and not medical advice. "
    "Dietary supplements are not intended to diagnose, treat, cure, or "
    "prevent any disease. Structure/function claims, deficiency-disease "
    "claims, and well-being claims are out of scope here."
)

BROCHURE = (
    r"\bdelve\b",
    r"\btapestry\b",
    r"\bunlock(?:s|ing)?\b",
    r"\bempower(?:s|ing)?\b",
    r"\bin this article\b",
    r"\blet's explore\b",
    r"\bin today's (?:world|fast-paced|wellness)\b",
    r"\bwellness journey\b",
    r"\bmultifaceted\b",
    r"\ba testament to\b",
    r"\bplays a crucial role\b",
    r"\bsupercharge\b",
    r"\bboost your\b",
    r"\bit'?s important to note\b",
    r"\bin the landscape of\b",
)

# Narrator-voice product/disease patterns. Statute quotes live in Claims desk.
DISEASE_CLAIM = (
    r"\b(?:vitamin|vitamine|ascorbic|thiamin|thiamine|niacin|riboflavin|"
    r"cobalamin|folate|folic|pyridoxine|biotin|pantothenic|retinol|"
    r"calciferol|tocopherol|phylloquinone|menaquinone|nutrient|supplement|"
    r"multivitamin|tablet|gumm(?:y|ies)|pill|capsule|dose|our formula)"
    r"\b[^.!?\n]{0,80}\b(?:treats?|cur(?:e|es|ed|ing)|prevents?|preventing|"
    r"diagnos(?:e|es|ed|ing)|heal(?:s|ed|ing)|mitigat(?:e|es|ed|ing))\b",
    r"\b(?:treats?|cur(?:e|es|ing)|prevents?|diagnos(?:e|es|ing)|heals?|"
    r"mitigat(?:e|es|ing))\b[^.!?\n]{0,60}\b(?:scurvy|beriberi|beri-beri|"
    r"rickets|pellagra|anemia|anaemia|cancer|diabetes|influenza|flu|"
    r"covid|heart disease|hypertension|arthritis|depression|obesity|"
    r"infection|infections)\b",
    r"\btake (?:this|your|a|the)\b[^.!?\n]{0,40}\b(?:supplement|vitamin|"
    r"tablet|gummy|capsule|pill)\b",
    r"\bsupports? (?:a )?(?:healthy )?(?:immune|immunity|heart|bone|joint|"
    r"brain|energy|metabolism)\b",
    r"\bbuilds? strong bones\b",
    r"\bmaintains? (?:cell integrity|bowel regularity)\b",
    r"\bclinically (?:proven|shown|demonstrated)\b",
    r"\bnatural alternative to\b",
    r"\bfights? (?:free radicals|cancer|disease|the flu|infection)\b",
    r"\bboosts? (?:your )?(?:immune|immunity|energy|metabolism)\b",
    r"\bfor everyday vitality\b",
    r"\bask (?:your doctor|a physician) about this supplement\b",
    r"\bfloor you should ignore\b",
    r"\byou should ignore\b[^.!?\n]{0,40}\b(?:RDA|DV|milligram|mg)\b",
)

FRONT_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.S)
KEY_RE = re.compile(r"^([a-z_]+):\s*(.*)$")


def parse_front(text: str) -> tuple[dict[str, object], str]:
    m = FRONT_RE.match(text)
    if not m:
        raise ValueError("missing YAML frontmatter")
    raw, body = m.group(1), m.group(2)
    data: dict[str, object] = {}
    key = None
    bucket: list[str] = []
    for line in raw.splitlines():
        km = KEY_RE.match(line)
        if km:
            if key == "sources":
                data[key] = bucket
                bucket = []
            key = km.group(1)
            val = km.group(2).strip().strip('"')
            if key == "sources":
                if val:
                    bucket.append(val)
                data[key] = bucket
            else:
                data[key] = val
        elif key == "sources" and line.strip().startswith("-"):
            bucket.append(line.split("-", 1)[1].strip())
            data[key] = bucket
    return data, body


def split_desk(body: str) -> tuple[str, str]:
    parts = re.split(r"^## Claims desk\s*$", body, maxsplit=1, flags=re.M)
    if len(parts) != 2:
        raise ValueError("missing ## Claims desk")
    return parts[0], parts[1]


def word_count(text: str) -> int:
    return len(re.findall(r"[A-Za-z0-9']+", text))


def lint_file(path: Path) -> list[str]:
    errs: list[str] = []
    text = path.read_text(encoding="utf-8")
    try:
        front, body = parse_front(text)
    except ValueError as e:
        return [f"{path.name}: {e}"]

    for k, v in REQUIRED_FRONT.items():
        if front.get(k) != v:
            errs.append(f"{path.name}: frontmatter {k}={front.get(k)!r} want {v!r}")

    for k in ("id", "slug", "title"):
        if not front.get(k):
            errs.append(f"{path.name}: missing {k}")

    sources = front.get("sources")
    if not isinstance(sources, list) or len(sources) < 2:
        errs.append(f"{path.name}: need at least two sources")

    try:
        essay, desk = split_desk(body)
    except ValueError as e:
        return errs + [f"{path.name}: {e}"]

    if word_count(essay) < MIN_WORDS:
        errs.append(
            f"{path.name}: essay has {word_count(essay)} words, floor is {MIN_WORDS}"
        )

    def smash(s: str) -> str:
        s = re.sub(r"[*_`]+", "", s)
        return " ".join(s.split())

    if smash(DISCLAIMER) not in smash(desk):
        errs.append(f"{path.name}: series disclaimer missing or paraphrased")

    for pat in BROCHURE:
        if re.search(pat, essay, re.I):
            errs.append(f"{path.name}: brochure voice / {pat}")

    # Strip quoted period language and statute mentions from the claim scan.
    scan = essay
    scan = re.sub(r"“[^”]*”", " ", scan)
    scan = re.sub(r'"[^"]*"', " ", scan)
    scan = re.sub(r"\*[^*]{0,80}\*", " ", scan)
    for pat in DISEASE_CLAIM:
        hit = re.search(pat, scan, re.I)
        if hit:
            errs.append(f"{path.name}: claims pattern {pat!r} near {hit.group(0)!r}")

    return errs


def main() -> int:
    drafts = sorted(ROOT.glob("VH-*.md"))
    errs: list[str] = []
    if len(drafts) < MIN_DRAFTS:
        errs.append(f"draft count {len(drafts)} < {MIN_DRAFTS}")

    slugs: dict[str, str] = {}
    ids: dict[str, str] = {}
    for path in drafts:
        front, _ = parse_front(path.read_text(encoding="utf-8"))
        slug = str(front.get("slug"))
        did = str(front.get("id"))
        if slug in slugs:
            errs.append(f"duplicate slug {slug}: {slugs[slug]} and {path.name}")
        slugs[slug] = path.name
        if did in ids:
            errs.append(f"duplicate id {did}: {ids[did]} and {path.name}")
        ids[did] = path.name
        errs.extend(lint_file(path))

    if errs:
        print("CLAIMS_LINT FAIL")
        for e in errs:
            print(f"  - {e}")
        print(f"{len(drafts)} drafts, {len(errs)} problems")
        return 1

    print(f"CLAIMS_LINT PASS  drafts={len(drafts)} slugs={len(slugs)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
