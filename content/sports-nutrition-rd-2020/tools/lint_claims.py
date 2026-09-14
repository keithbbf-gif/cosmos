#!/usr/bin/env python3
"""Tripwire for sports-nutrition-rd-2020 claims fence and editor flags.

Not a truth machine. Catches missing frontmatter, thin drafts, duplicate H1s,
label-bot sludge, and disease-claim phrases. A human still has to catch the
sly sentence that never uses the word 'cure'.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MIN_DRAFTS = 45
MIN_WORDS = 400
REQUIRED_FRONT = (
    "title",
    "slug",
    "status",
    "stage",
    "series",
    "audience",
    "window",
    "voice",
    "claims",
    "voice_check",
    "last_reviewed",
)
FM_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.S)
FORBIDDEN = [
    (
        r"\b(cures?|cured|curing)\s+(cancer|diabetes|depression|covid|infection|sarcopenia|osteoporosis)\b",
        "disease-cure verb + condition",
    ),
    (
        r"\b(treats?|treated|treating)\s+(cancer|diabetes|reds|red-s|injury|tendon|kidney disease)\b",
        "treat + condition",
    ),
    (
        r"\b(prevents?|prevented|preventing)\s+(cancer|diabetes|heart disease|infection|covid|reds|sarcopenia)\b",
        "prevent + condition",
    ),
    (r"\bclinically proven to\b", "clinically proven to"),
    (r"\bboosts? (your )?immune system\b", "immune-boost claim"),
    (r"\bheals? (your )?(tendon|ligament|injury)\b", "healing claim"),
    (r"\bunlock(s|ing)? your (body|potential)\b", "unlock-your-body"),
    (r"\bin today's fast-paced world\b", "bot opening"),
    (r"\blet's dive in\b", "bot opening"),
    (r"\bgame[- ]changer\b", "game-changer"),
    (r"\bbiohack\b", "biohack"),
]
BOT_SMELL = [
    r"\bdelve\b",
    r"\btapestry\b",
    r"\bit's important to note\b",
    r"\bin conclusion,?\b",
    r"\blet's explore\b",
]
FENCE_NEEDLE = re.compile(
    r"(I will not|I do not diagnose|What (this|it) (is|does) not|disease claim|"
    r"not a (treatment|therapy|kidney protocol|disease|promise|law|religion|license|"
    r"prescription|lifestyle|hotel protocol|purity test|protein stand|gel flavor|"
    r"famine|cliff|brand|serum|nickname|tweet|close fight|not permission)|"
    r"claims policy|Those sentences leave|No (treatment|medical|disease|heat-illness)|"
    r"not medical advice|not cleared for)",
    re.I,
)
REFUSAL_BEFORE = re.compile(
    r"(will not|do not|does not|not claim|not say|draft does not|I will not)\s+",
    re.I,
)


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    m = FM_RE.match(text)
    if not m:
        raise ValueError("missing YAML frontmatter")
    meta: dict[str, str] = {}
    for line in m.group(1).splitlines():
        if not line.strip() or line.strip().startswith("#") or ":" not in line:
            continue
        key, val = line.split(":", 1)
        meta[key.strip()] = val.strip().strip('"').strip("'")
    return meta, m.group(2)


def words(body: str) -> int:
    return len(re.findall(r"[A-Za-z0-9']+", body))


def draft_paths() -> list[Path]:
    return sorted(ROOT.glob("stage-*/[0-9][0-9]-*.md"))


def lint_one(path: Path) -> list[str]:
    errs: list[str] = []
    text = path.read_text(encoding="utf-8")
    try:
        meta, body = parse_frontmatter(text)
    except ValueError as e:
        return [f"{path.name}: {e}"]

    for key in REQUIRED_FRONT:
        if key not in meta or not meta[key]:
            errs.append(f"{path.name}: missing frontmatter '{key}'")
    if meta.get("status") != "draft":
        errs.append(f"{path.name}: status must be draft")
    if meta.get("claims") != "no-disease":
        errs.append(f"{path.name}: claims must be no-disease")
    if meta.get("voice") != "human":
        errs.append(f"{path.name}: voice must be human")
    if meta.get("series") != "sports-nutrition-rd-2020":
        errs.append(f"{path.name}: series must be sports-nutrition-rd-2020")
    if meta.get("voice_check") != "edited":
        errs.append(f"{path.name}: voice_check must be edited after editor pass")

    title = meta.get("title", "")
    h1 = re.search(r"^#\s+(.+)", body, re.M)
    if h1 and title and h1.group(1).strip() != title.strip():
        errs.append(f"{path.name}: H1 does not match title frontmatter")

    wc = words(body)
    if wc < MIN_WORDS:
        errs.append(f"{path.name}: {wc} words < {MIN_WORDS}")

    if not re.search(r"^## Sources\s*$", body, re.M):
        errs.append(f"{path.name}: missing '## Sources' heading")
    if not re.search(r"doi:|PMID:", body, re.I):
        errs.append(f"{path.name}: sources need doi: or PMID:")

    if not FENCE_NEEDLE.search(body):
        errs.append(f"{path.name}: missing an explicit claims fence (refusal or 'not a treatment')")

    for pat, label in FORBIDDEN:
        for m in re.finditer(pat, body, re.I):
            before = body[max(0, m.start() - 48) : m.start()]
            if REFUSAL_BEFORE.search(before):
                continue
            if '"' in before[-20:] or '"' in body[m.end() : m.end() + 3]:
                continue
            errs.append(f"{path.name}: forbidden phrase ({label})")
            break

    for pat in BOT_SMELL:
        if re.search(pat, body, re.I):
            errs.append(f"{path.name}: bot-smell phrase ({pat})")

    return errs


def main() -> int:
    parser = argparse.ArgumentParser(description="Lint sports-nutrition-rd-2020 drafts")
    parser.parse_args()
    paths = draft_paths()
    if len(paths) < MIN_DRAFTS:
        print(f"expected at least {MIN_DRAFTS} drafts, found {len(paths)}", file=sys.stderr)
        return 1

    all_errs: list[str] = []
    for path in paths:
        all_errs.extend(lint_one(path))

    if all_errs:
        for e in all_errs:
            print(e, file=sys.stderr)
        print(f"FAIL ({len(all_errs)} issues)", file=sys.stderr)
        return 1

    print(f"OK — {len(paths)} drafts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
