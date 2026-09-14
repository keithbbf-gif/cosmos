#!/usr/bin/env python3
"""Editorial QA for the SLPWOW SLP News draft pack. Not a site runtime."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ARTICLES = ROOT / "articles"
PACK = "slpwow-slp-news"

REQUIRED_ROOT = [
    "README.md",
    "INDEX.md",
    "BIBLIOGRAPHY.md",
    "CLAIMS_GUARDRAILS.md",
    "WP_IMPORT.md",
    "EDITOR_REPORT.md",
    "_TEMPLATE.md",
]

DISCLAIMER = re.compile(
    r"This article does not offer clinical advice, billing guarantees, or diagnosis guidance\."
)

CLAIMS_FENCE = re.compile(
    r"(What SLPs should verify|What this is not|What the .+ is not|did not add)",
    re.I,
)

BANNED = re.compile(
    r"\bdelve\b|\btapestry\b|\bunlock(?:s|ing)?\b|\bempower(?:s|ing)?\b|"
    r"rapidly evolving|it'?s important to note|as an SLP, you may be wondering|"
    r"stakeholders are excited|in this article we\b|let'?s explore\b|"
    r"wellness journey|multifaceted|a testament to|plays a crucial role",
    re.I,
)

COMPOSITE = re.compile(
    r"\bclinicians say\b|\bexperts agree\b|\bmany SLPs report\b(?!\s+they)",
    re.I,
)

BILLING_GUARANTEE = re.compile(
    r"\b(?:is|are|will be)\s+(?:always\s+)?covered\b|"
    r"\bguaranteed reimbursement\b",
    re.I,
)

FRONT_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.S)


def fail(msg: str) -> None:
    print(f"FAIL  {msg}")
    raise SystemExit(1)


def split_front(text: str) -> tuple[dict[str, str], str]:
    m = FRONT_RE.match(text)
    if not m:
        fail("markdown missing YAML frontmatter")
    fm: dict[str, str] = {}
    for line in m.group(1).splitlines():
        if ":" in line and not line.startswith(" "):
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip().strip('"')
    return fm, m.group(2)


def main() -> int:
    errors: list[str] = []
    for name in REQUIRED_ROOT:
        if not (ROOT / name).is_file():
            errors.append(f"missing root file: {name}")

    drafts = sorted(ARTICLES.glob("*.md"))
    if len(drafts) != 46:
        errors.append(f"article count {len(drafts)} != 46")

    slugs: dict[str, str] = {}
    for path in drafts:
        text = path.read_text(encoding="utf-8")
        fm, body = split_front(text)
        if fm.get("status") != "draft":
            errors.append(f"{path.name}: status is not draft")
        if fm.get("category") != "slp-news":
            errors.append(f"{path.name}: category is not slp-news")
        if fm.get("voice_check") != "edited":
            errors.append(f"{path.name}: voice_check is not edited")
        if not fm.get("slug"):
            errors.append(f"{path.name}: missing slug")
        slug = fm["slug"]
        if slug in slugs:
            errors.append(f"duplicate slug {slug}: {slugs[slug]} and {path.name}")
        slugs[slug] = path.name
        if "sources" not in text.split("---", 2)[1]:
            errors.append(f"{path.name}: missing sources YAML block")
        if not DISCLAIMER.search(body):
            errors.append(f"{path.name}: missing claims disclaimer sentence")
        if "## Sources" not in body:
            errors.append(f"{path.name}: missing ## Sources section")
        at = fm.get("article_type", "feature")
        if at == "feature" and not CLAIMS_FENCE.search(body):
            errors.append(f"{path.name}: feature missing claims-fence section")
        scan = body
        scan = re.sub(r"“[^”]*”", " ", scan)
        scan = re.sub(r'"[^"]*"', " ", scan)
        hit = BANNED.search(scan)
        if hit:
            errors.append(f"{path.name}: brochure voice {hit.group(0)!r}")
        comp = COMPOSITE.search(scan)
        if comp:
            errors.append(f"{path.name}: composite-voice {comp.group(0)!r}")
        for line in scan.splitlines():
            bill_m = BILLING_GUARANTEE.search(line)
            if bill_m and not re.search(
                r"\bnot\b.+\bis covered\b|\bis not\b.+\bcovered\b|"
                r"finding that every .+ is covered",
                line,
                re.I,
            ):
                errors.append(
                    f"{path.name}: billing-guarantee {bill_m.group(0)!r}"
                )
                break

    report = ROOT / "EDITOR_REPORT.md"
    if report.is_file():
        rt = report.read_text(encoding="utf-8")
        if "voice_check: edited" not in rt:
            errors.append("EDITOR_REPORT.md missing voice_check: edited marker")

    if errors:
        print(f"PACK QA  {PACK}")
        for e in errors:
            print(f"  - {e}")
        return 1

    print(f"PASS  {PACK}  articles={len(drafts)}  slugs={len(slugs)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
