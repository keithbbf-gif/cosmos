#!/usr/bin/env python3
"""Tripwire for the herbal-tea foodways claims fence.

Not a truth machine. Catches missing frontmatter, thin drafts, duplicate
openings, disease-payoff phrases, and wellness-bot sludge. A human still
has to catch the sly sentence that never uses the word 'cure'.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MIN_DRAFTS = 40
MIN_WORDS = 700
REQUIRED_FRONT = (
    "id",
    "slug",
    "title",
    "stage",
    "stage_name",
    "voice",
    "claims_posture",
    "audience",
    "status",
    "voice_check",
)
FM_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.S)
FORBIDDEN = [
    (
        r"\b(cures?|cured)\s+(cancer|diabetes|depression|disease|infection|covid|you|your)\b",
        "cure-verb + payoff",
    ),
    (
        r"\b(treats?|treated|treating)\s+(cancer|diabetes|depression|disease|infection|covid|hypertension|anxiety)\b",
        "treat + condition",
    ),
    (
        r"\b(prevents?|prevented|preventing)\s+(cancer|diabetes|heart disease|disease|infection|covid)\b",
        "prevent + condition",
    ),
    (r"\bclinically proven to\b", "clinically proven to"),
    (r"\bmiracle (cure|herb|plant|tea)\b", "miracle claim"),
    (r"\bno side effects\b", "no side effects"),
    (r"\b100%\s*safe\b", "100% safe"),
    (r"\bFDA[- ]approved (tea|tisane|herb|supplement)\b", "false FDA class"),
    (r"\bwonder (drug|herb|plant|tea)\b", "wonder-drug register"),
    (r"\bguaranteed to\b", "guaranteed to"),
    (r"\bboosts? (your )?immune system\b", "immune-boost claim"),
    (r"\bsuperfood\b", "superfood"),
    (r"\bunlock(s|ing)? your (body|potential|stress)\b", "unlock-your-body"),
    (r"\bin today's fast-paced world\b", "bot opening"),
    (r"\blet's dive in\b", "bot opening"),
    (r"\bwithout further ado\b", "bot opening"),
    (r"\banti-inflammatory\b", "clinical-adjacent payoff"),
    (r"\bantiviral\b", "clinical-adjacent payoff"),
    (r"\bantibacterial\b", "clinical-adjacent payoff"),
    (r"\bantimicrobial\b", "clinical-adjacent payoff"),
    (r"\badaptogen\b", "wrong-folder class word"),
]
# Disease names as payoff. Allowed only in draft 01, which is the refuse file.
DISEASE_PAYOFF = re.compile(
    r"\b(cancer|diabetes|hypertension|arthritis|alzheimer'?s|covid-?19|"
    r"influenza|pneumonia|depression|anxiety disorder|tumor|malaria)\b",
    re.I,
)
BOT_SMELL = [
    r"\bdelve\b",
    r"\btapestry\b",
    r"\brich (and vibrant )?history\b",
    r"\bit's important to note\b",
    r"\bin conclusion,?\b",
    r"\blet's explore\b",
    r"\bholistic wellness journey\b",
]
CLAIMS_NEEDLE = re.compile(r"not medical advice", re.I)
HIST_NEEDLE = re.compile(
    r"\b(foodways?|hospitality|household|historical|historically|"
    r"kitchen|stillroom|trade|garden|ceremony|cafe|substitution|"
    r"etymolog|tisane|grocery)\b",
    re.I,
)
CURE_REFUSE = re.compile(
    r"(does not (diagnose|treat|cure|prevent)|not a (disease )?(treatment|cure)|"
    r"not (an? )?(disease )?(treatment|cure)|no disease|"
    r"not (offered|written|sold) as (a )?(treatment|cure))",
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
    if meta.get("claims_posture") != "educational-foodways":
        errs.append(f"{path.name}: claims_posture must be educational-foodways")
    if meta.get("status") != "draft":
        errs.append(f"{path.name}: status must be draft")
    if meta.get("voice") not in {"essay", "human-essay"}:
        errs.append(f"{path.name}: voice must be essay or human-essay")
    if meta.get("audience") != "curious-reader":
        errs.append(f"{path.name}: audience must be curious-reader")
    if meta.get("voice_check") not in {"writer-pass", "edited"}:
        errs.append(f"{path.name}: voice_check must be writer-pass or edited")

    wc = words(body)
    if wc < MIN_WORDS:
        errs.append(f"{path.name}: {wc} words < {MIN_WORDS}")

    if not re.search(r"^## Claims box\s*$", body, re.M):
        errs.append(f"{path.name}: missing '## Claims box' heading")
    box_at = body.lower().find("claims box")
    bullets = re.findall(r"^[-*]\s+\S+", body[box_at:], re.M) if box_at >= 0 else []
    if len(bullets) < 3:
        errs.append(f"{path.name}: Claims box needs at least 3 bullets")

    if not CLAIMS_NEEDLE.search(body):
        errs.append(f"{path.name}: body must say 'not medical advice'")
    if not HIST_NEEDLE.search(body):
        errs.append(f"{path.name}: missing foodways/historical framing word")
    if not CURE_REFUSE.search(body):
        errs.append(f"{path.name}: missing an explicit refuse-to-cure sentence")

    for pat, label in FORBIDDEN:
        if re.search(pat, body, re.I):
            errs.append(f"{path.name}: forbidden phrase ({label})")

    if meta.get("id") != "01" and DISEASE_PAYOFF.search(body):
        errs.append(f"{path.name}: disease-name payoff (no-disease series)")

    smells = [p for p in BOT_SMELL if re.search(p, body, re.I)]
    if len(smells) >= 2:
        errs.append(f"{path.name}: bot-voice cluster ({len(smells)} hits)")

    return errs


def manifest_text(rows: list[dict[str, str]]) -> str:
    lines = [
        "# Generated by tools/lint_claims.py --write-manifest. Do not hand-edit.",
        "",
        'series = "herbal-tea-foodways-history"',
        f"min_drafts = {MIN_DRAFTS}",
        'status = "draft"',
        'claims_posture = "educational-foodways"',
        "",
        f"draft_count = {len(rows)}",
        "",
    ]
    for row in rows:
        lines.append("[[draft]]")
        for key in ("id", "slug", "title", "stage", "path", "words"):
            val = row[key].replace('"', '\\"')
            lines.append(f'{key} = "{val}"')
        lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write-manifest", action="store_true")
    args = ap.parse_args(argv)

    paths = draft_paths()
    errors: list[str] = []
    if len(paths) < MIN_DRAFTS:
        errors.append(f"draft count {len(paths)} < {MIN_DRAFTS}")

    slugs: dict[str, str] = {}
    titles: dict[str, str] = {}
    openings: dict[str, str] = {}
    rows: list[dict[str, str]] = []

    for path in paths:
        errors.extend(lint_one(path))
        text = path.read_text(encoding="utf-8")
        try:
            meta, body = parse_frontmatter(text)
        except ValueError:
            continue
        slug = meta.get("slug", "")
        title = meta.get("title", "")
        if slug in slugs:
            errors.append(f"duplicate slug {slug}: {path.name} vs {slugs[slug]}")
        slugs[slug] = path.name
        if title in titles:
            errors.append(f"duplicate title {title!r}: {path.name} vs {titles[title]}")
        titles[title] = path.name
        prose = re.sub(r"^#+\s+.*$", "", body, flags=re.M)
        prose = re.sub(r"<!-- htf-figure:v1 -->.*?</figure>", " ", prose, flags=re.S)
        prose = re.sub(r"\s+", " ", prose).strip()
        key = prose[:100].lower()
        if key in openings:
            errors.append(f"duplicate opening {path.name} vs {openings[key]}")
        openings[key] = path.name
        rows.append(
            {
                "id": meta.get("id", ""),
                "slug": slug,
                "title": title,
                "stage": meta.get("stage", ""),
                "path": str(path.relative_to(ROOT)).replace("\\", "/"),
                "words": str(words(body)),
            }
        )

    if args.write_manifest:
        (ROOT / "MANIFEST.toml").write_text(manifest_text(rows), encoding="utf-8")

    if errors:
        print("FAIL")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"OK {len(paths)} drafts, fence standing")
    return 0


if __name__ == "__main__":
    sys.exit(main())
