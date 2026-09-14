#!/usr/bin/env python3
"""Tripwire for the counseling ethics-code history claims fence.

Not a truth machine. Catches missing frontmatter, thin drafts, duplicate
openings, protocol language, bot-voice sludge, and long code-paste risk.
A human still has to catch the sly sentence that never uses the word
'try' and still hands the reader a complaint form.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MIN_DRAFTS = 40
MIN_WORDS = 800
REQUIRED_FRONT = (
    "id",
    "slug",
    "title",
    "stage",
    "stage_name",
    "voice",
    "voice_check",
    "claims_posture",
    "audience",
    "status",
    "meta_description",
    "type",
    "order",
    "portrait",
    "last_verified",
)
FM_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.S)
FORBIDDEN = [
    (r"\btry this at home\b", "try this at home"),
    (r"\bself-treat\b", "self-treat"),
    (r"\bgold-standard treatment\b", "gold-standard treatment"),
    (r"\bclinically proven to\b", "clinically proven to"),
    (r"\bguaranteed to\b", "guaranteed to"),
    (r"\bask yourself these\b", "worksheet voice"),
    (r"\bfollow these steps\b", "protocol voice"),
    (r"\bfile (?:your |a )complaint (?:by|online|here)\b", "complaint how-to"),
    (r"\bin today's (?:rapidly |fast-paced )", "bot opening"),
    (r"\blet's dive in\b", "bot opening"),
    (r"\bwithout further ado\b", "bot opening"),
    (r"\bin this article we will explore\b", "bot opening"),
    (r"\bwhether you're a\b", "bot duality"),
    (r"\bholistic wellness journey\b", "wellness-bot"),
    (r"\bmiracle (cure|therapy|treatment)\b", "miracle claim"),
    (r"\bbest therapist in\b", "brand superlative"),
]
BOT_SMELL = [
    r"\bdelve\b",
    r"\btapestry\b",
    r"\bplethora\b",
    r"\brobust\b",
    r"\bleverage\b",
    r"\bunlock(?:s|ed|ing)?\b",
    r"\bit's important to note\b",
    r"\bin conclusion,?\b",
    r"\blet's explore\b",
    r"\bcutting-edge\b",
    r"\bgame-chang",
]
CLAIMS_NEEDLE = re.compile(r"not a treatment plan", re.I)
ADVICE_NEEDLE = re.compile(r"not medical advice", re.I)
LEGAL_NEEDLE = re.compile(r"not legal advice", re.I)
HIST_NEEDLE = re.compile(
    r"\b(histor(?:y|ical|ically)|code|committee|document|assembly|"
    r"revision|amendment|standard|principle|court|report)\b",
    re.I,
)
CURE_REFUSE = re.compile(
    r"(does not (diagnose|treat|cure|prevent|adjudicate)|"
    r"not a (diagnosis|treatment plan)|"
    r"not (a )?substitute for|this series does not publish)",
    re.I,
)
LONG_QUOTE = re.compile(r"^> .{280,}", re.M)


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    m = FM_RE.match(text)
    if not m:
        raise ValueError("missing YAML frontmatter")
    meta: dict[str, str] = {}
    for line in m.group(1).splitlines():
        if not line.strip() or line.strip().startswith("#") or ":" not in line:
            continue
        if line.startswith(" ") or line.startswith("-"):
            continue
        key, val = line.split(":", 1)
        meta[key.strip()] = _unquote_yaml_scalar(val.strip())
    return meta, m.group(2)


def _unquote_yaml_scalar(val: str) -> str:
    """Strip one matching quote pair. Do not eat apostrophes inside the title."""
    if len(val) >= 2 and val[0] == val[-1] and val[0] in {'"', "'"}:
        return val[1:-1]
    return val


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
    if meta.get("claims_posture") != "educational-ethics-history":
        errs.append(f"{path.name}: claims_posture must be educational-ethics-history")
    if meta.get("status") != "draft":
        errs.append(f"{path.name}: status must be draft")
    if meta.get("voice") != "essay":
        errs.append(f"{path.name}: voice must be essay")
    if meta.get("voice_check") not in ("human", "edited"):
        errs.append(f"{path.name}: voice_check must be human or edited")
    if meta.get("audience") != "curious-reader":
        errs.append(f"{path.name}: audience must be curious-reader")
    if meta.get("last_verified") != "2026-09-14":
        errs.append(f"{path.name}: last_verified should be 2026-09-14 for this pack")

    n = words(body)
    if n < MIN_WORDS:
        errs.append(f"{path.name}: {n} words < {MIN_WORDS}")

    low = body.lower()
    if CLAIMS_NEEDLE.search(low) is None:
        errs.append(f"{path.name}: missing 'not a treatment plan'")
    if ADVICE_NEEDLE.search(low) is None:
        errs.append(f"{path.name}: missing 'not medical advice'")
    if LEGAL_NEEDLE.search(low) is None:
        errs.append(f"{path.name}: missing 'not legal advice'")
    if "## claims box" not in low:
        errs.append(f"{path.name}: missing Claims box heading")
    if HIST_NEEDLE.search(body) is None:
        errs.append(f"{path.name}: no historical/document marker")
    if CURE_REFUSE.search(body) is None:
        errs.append(f"{path.name}: missing refuse-treatment sentence")
    if LONG_QUOTE.search(body):
        errs.append(f"{path.name}: long blockquote — possible code paste")

    for pat, label in FORBIDDEN:
        if re.search(pat, low):
            errs.append(f"{path.name}: forbidden /{label}/")
    for pat in BOT_SMELL:
        if re.search(pat, low):
            errs.append(f"{path.name}: bot-smell /{pat}/")

    if not body.strip().startswith("**Educational note.**"):
        errs.append(f"{path.name}: must open with educational note")

    return errs


def first_sentence(body: str) -> str:
    parts = body.split("\n\n", 1)
    rest = parts[1] if len(parts) > 1 else body
    rest = re.sub(r"^#+\s+.*\n", "", rest).strip()
    # Keep initials (Edward C.) and hostnames (apa.org) from looking like a stop.
    dot = "\x00"
    protected = re.sub(r"\b([A-Za-z])\.", lambda m: m.group(1) + dot, rest)
    protected = re.sub(
        r"\.(org|com|edu|gov|net|io)\b",
        lambda m: dot + m.group(1),
        protected,
        flags=re.I,
    )
    m = re.search(r"(.+?[.?!])", protected)
    raw = m.group(1) if m else protected[:160]
    return raw.replace(dot, ".").strip()


def write_manifest(rows: list[dict[str, str]]) -> None:
    lines = [
        "# Generated by tools/lint_claims.py --write-manifest. Do not hand-edit.",
        "",
        'series = "counseling-ethics-history"',
        f"min_drafts = {MIN_DRAFTS}",
        'status = "draft"',
        'claims_posture = "educational-ethics-history"',
        'site = "wowtherapies"',
        "",
        f"draft_count = {len(rows)}",
        "",
    ]
    for r in rows:
        lines.append("[[draft]]")
        for key in ("id", "slug", "title", "stage", "path", "words"):
            val = r[key].replace('"', '\\"')
            lines.append(f'{key} = "{val}"')
        lines.append("")
    (ROOT / "MANIFEST.toml").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-manifest", action="store_true")
    args = parser.parse_args()

    paths = draft_paths()
    errors: list[str] = []
    if len(paths) < MIN_DRAFTS:
        errors.append(f"draft count {len(paths)} < {MIN_DRAFTS}")

    slugs: list[str] = []
    openings: dict[str, str] = {}
    orders: dict[str, str] = {}
    rows: list[dict[str, str]] = []

    for path in paths:
        text = path.read_text(encoding="utf-8")
        try:
            meta, body = parse_frontmatter(text)
        except ValueError as e:
            errors.append(f"{path.name}: {e}")
            continue
        errors.extend(lint_one(path))
        slug = meta.get("slug", "")
        if slug:
            if slug in slugs:
                errors.append(f"duplicate slug {slug}")
            slugs.append(slug)
        opening = first_sentence(body)
        if opening in openings:
            errors.append(f"{path.name}: opening collides with {openings[opening]}")
        else:
            openings[opening] = path.name
        order = meta.get("order", "")
        if order in orders:
            errors.append(f"{path.name}: order {order} collides with {orders[order]}")
        else:
            orders[order] = path.name
        rel = path.relative_to(ROOT).as_posix()
        rows.append(
            {
                "id": meta.get("id", ""),
                "slug": slug,
                "title": meta.get("title", ""),
                "stage": meta.get("stage", ""),
                "path": rel,
                "words": str(words(body)),
            }
        )

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for slug in slugs:
        if slug not in readme:
            errors.append(f"README.md missing slug {slug}")

    ops = [
        "README.md",
        "GUARDRAILS.md",
        "STYLE_GUIDE.md",
        "CITATIONS.md",
        "PHOTO_NOTES.md",
        "PORTRAIT_SOURCES.md",
        "WP_IMPORT.md",
    ]
    for name in ops:
        if not (ROOT / name).is_file():
            errors.append(f"missing ops file {name}")

    if args.write_manifest and rows:
        write_manifest(rows)

    print(f"drafts: {len(paths)}")
    print(f"errors: {len(errors)}")
    for e in errors:
        print(f"FAIL {e}")
    if errors:
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
