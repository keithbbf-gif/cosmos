#!/usr/bin/env python3
"""Graphics and SEO tripwire for act-mindfulness-therapy-history pack."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FM_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.S)
FIGURE_RE = re.compile(r'<figure class="wow-act-figure', re.I)
AI_FACE = re.compile(
    r"(ai[- ]generated|synthetic (?:face|likeness|portrait)|midjourney|stable diffusion)",
    re.I,
)
FORBIDDEN_META = re.compile(
    r"(clinically proven|gold-standard treatment|treats your|book (?:now|today)|guaranteed)",
    re.I,
)

REQUIRED_SEO = ("meta_description", "featured_image", "graphic_kind", "last_verified")
MIN_META = 100
MAX_META = 165


def parse_front(text: str) -> tuple[dict[str, str], str]:
    m = FM_RE.match(text)
    if not m:
        return {}, text
    meta: dict[str, str] = {}
    for line in m.group(1).splitlines():
        if ":" not in line or line.strip().startswith("#"):
            continue
        k, v = line.split(":", 1)
        meta[k.strip()] = v.strip().strip('"').strip("'")
    return meta, m.group(2)


def draft_paths() -> list[Path]:
    return sorted(ROOT.glob("stage-*/[0-9][0-9]-*.md"))


def main() -> int:
    errors: list[str] = []
    for path in draft_paths():
        text = path.read_text(encoding="utf-8")
        meta, body = parse_front(text)
        for key in REQUIRED_SEO:
            if key not in meta or not meta[key]:
                errors.append(f"{path.name}: missing YAML {key}")
        md = meta.get("meta_description", "")
        if md and (len(md) < MIN_META or len(md) > MAX_META):
            errors.append(f"{path.name}: meta_description length {len(md)} not in [{MIN_META},{MAX_META}]")
        if md and FORBIDDEN_META.search(md):
            errors.append(f"{path.name}: meta_description has forbidden marketing phrase")
        feat = meta.get("featured_image", "")
        if feat:
            if feat.startswith("../"):
                rel = (path.parent / feat).resolve()
            else:
                rel = (ROOT / feat).resolve()
            if not rel.is_file():
                errors.append(f"{path.name}: featured_image missing at {rel}")
        kind = meta.get("graphic_kind", "")
        if kind not in {"essay", "timeline", "map", "type", "portrait-pending"}:
            errors.append(f"{path.name}: bad graphic_kind {kind!r}")
        if kind in {"timeline", "map", "type", "portrait-pending"} and not FIGURE_RE.search(body):
            errors.append(f"{path.name}: graphic_kind {kind} but no wow-act-figure embed")
        if AI_FACE.search(body):
            errors.append(f"{path.name}: AI-face language in body")
        if FIGURE_RE.search(body):
            if "<figcaption>" not in body.lower():
                errors.append(f"{path.name}: figure without figcaption")
            if 'class="figure-credit"' not in body and "portrait-pending" not in body:
                if kind in {"timeline", "map", "type"}:
                    errors.append(f"{path.name}: figure missing figure-credit span")

    for name in ("RIGHTS.md", "GRAPHICS_INDEX.md", "embeds/figure-blocks.md"):
        if not (ROOT / name).is_file():
            errors.append(f"missing ops file {name}")

    for svg in (
        "graphics/fig-01-document-milestones.svg",
        "graphics/fig-02-clinic-places-map.svg",
        "graphics/fig-03-act-naming-dates.svg",
        "assets/_shared/series-featured.svg",
    ):
        if not (ROOT / svg).is_file():
            errors.append(f"missing asset {svg}")

    print(f"drafts checked: {len(draft_paths())}")
    print(f"errors: {len(errors)}")
    for e in errors:
        print(f"FAIL {e}")
    if errors:
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
