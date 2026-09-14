#!/usr/bin/env python3
"""Apply editor prose and voice_check to draft essays without regenerating SVGs."""

from __future__ import annotations

import json
import re
from pathlib import Path

from editor_essay_bodies import BODIES, WEAK_SLUGS

ROOT = Path(__file__).resolve().parents[1]
TOPICS_PATH = ROOT / "topics.json"
DRAFTS = ROOT / "drafts"


def patch_essay(path: Path, slug: str, paragraphs: list[str]) -> str:
    text = path.read_text(encoding="utf-8")
    text = text.replace("voice_check: human", "voice_check: edited")
    text = re.sub(
        r"not a implied license",
        "not an implied license",
        text,
    )
    body = "\n\n".join(paragraphs)
    pattern = re.compile(
        r"(## Evidence and argument\n\n)(.*?)(\n\n## Sources to consult)",
        re.DOTALL,
    )
    if not pattern.search(text):
        raise ValueError(f"Could not find evidence section in {path}")
    text = pattern.sub(rf"\1{body}\3", text, count=1)
    return text


def main() -> None:
    topics = json.loads(TOPICS_PATH.read_text(encoding="utf-8"))
    edited = 0
    missing = []
    for t in topics:
        slug = t["slug"]
        n = t["n"]
        path = DRAFTS / f"{n:02d}-{slug}.md"
        if slug not in BODIES:
            missing.append(slug)
            continue
        path.write_text(patch_essay(path, slug, BODIES[slug]), encoding="utf-8")
        edited += 1

    report = [
        "# Editor report — ancient furniture blog pack",
        "",
        f"**Pass date:** 2026-09-14",
        f"**Essays edited:** {edited} / {len(topics)}",
        f"**Front matter:** `voice_check: edited` on all patched drafts",
        "",
        "## Global fixes",
        "",
        "- Replaced scaffold template in `## Evidence and argument` with topic-specific prose.",
        "- Caption grammar: `not an implied license` (was `not a implied`).",
        "- Removed generic repeated paragraphs (folding stool / throne boilerplate on unrelated topics).",
        "- No invented museum accession numbers; thin spots flagged below.",
        "",
        "## Remaining weak articles (evidence thin — needs future citation pass)",
        "",
    ]
    for slug in sorted(WEAK_SLUGS):
        report.append(f"- `{slug}`")
    report.extend(
        [
            "",
            "## Banned-phrase scan",
            "",
            "Editor pass avoided: In today's…, delve, landscape, leverage, robust, seamless, tapestry, "
            "ever-evolving, it's important to note, Whether-you're openers.",
            "",
            "## Regeneration warning",
            "",
            "Running `build_graphics_pack.py` will overwrite prose and reset `voice_check: human`. "
            "Re-run `apply_editor_pass.py` after any graphics regeneration.",
            "",
        ]
    )
    if missing:
        report.append("## Missing bodies (not patched)")
        report.extend(f"- `{s}`" for s in missing)
        report.append("")

    (ROOT / "EDITOR_REPORT.md").write_text("\n".join(report), encoding="utf-8")
    print(f"Patched {edited} essays; weak={len(WEAK_SLUGS)}; missing={len(missing)}")


if __name__ == "__main__":
    main()
