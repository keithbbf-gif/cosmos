#!/usr/bin/env python3
"""Embed IMAGE+SEO figure blocks and frontmatter into OGFH spoken drafts."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DRAFTS = ROOT / "drafts"
IMAGE_PASS = "2026-09-14"
FIGURE_CLASS = "ogfh-figure ogfh-figure--diagram"
MARKER = "<!-- ogfh-figure:v1 -->"
RIGHTS_LINE = (
    "Original editorial schematic; Keith Fritz / BBF outdoor-garden-furniture-history pack "
    "(see RIGHTS.md)."
)

FM_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.S)


def meta_description(title: str, claim: str) -> str:
    claim = claim.strip().strip('"').strip("'")
    if len(claim) > 140:
        claim = claim[:137].rsplit(" ", 1)[0] + "…"
    base = title.rstrip(".")
    return f"{base}. {claim} Staged BBF spoken draft."


def figure_block(stem: str, alt: str, caption: str) -> str:
    asset = f"../assets/diagrams/{stem}.svg"
    return f"""{MARKER}
<figure class="{FIGURE_CLASS}">
  <img
    src="{asset}"
    alt="{alt}"
    width="880"
    height="520"
    loading="lazy"
    decoding="async"
  />
  <figcaption><strong>Fig. 1.</strong> {caption} <em>Rights:</em> {RIGHTS_LINE}</figcaption>
</figure>

"""


def upsert_frontmatter(fm: str, fields: dict[str, str]) -> str:
    lines = fm.splitlines()
    keys = {line.split(":", 1)[0].strip() for line in lines if ":" in line}
    for key, val in fields.items():
        if key in keys:
            lines = [
                f"{key}: {val}" if line.split(":", 1)[0].strip() == key else line
                for line in lines
            ]
        else:
            lines.append(f"{key}: {val}")
    return "\n".join(lines) + "\n"


def normalize_empty_sequence(fm: str) -> str:
    return re.sub(r"^sequence_after:\s*$", 'sequence_after: ""', fm, flags=re.M)


def alt_from_title(title: str) -> str:
    return f"Editorial schematic for BBF outdoor furniture history: {title.rstrip('.')}"


def main() -> int:
    updated = 0
    for path in sorted(DRAFTS.glob("*.md")):
        stem = path.stem
        svg = ROOT / "assets" / "diagrams" / f"{stem}.svg"
        if not svg.is_file():
            print(f"skip {path.name}: missing {svg.name}")
            continue
        raw = path.read_text(encoding="utf-8")
        m = FM_RE.match(raw)
        if not m:
            print(f"skip {path.name}: no frontmatter")
            continue
        fm, body = m.group(1), m.group(2)
        fm = normalize_empty_sequence(fm)
        fields = dict(re.findall(r"^([a-z_]+):[ \t]*(.+)$", fm, re.M))
        title = fields.get("title", stem).strip().strip('"').strip("'")
        claim = fields.get("educational_claim", title)
        figure_id = f"diagrams.{stem}"
        desc = meta_description(title, claim)
        fm_new = upsert_frontmatter(
            fm,
            {
                "meta_description": yaml_quote(desc),
                "figure_id": figure_id,
                "image_rights": "documented",
                "image_pass": IMAGE_PASS,
                "featured_image": "../assets/_shared/series-featured.svg",
            },
        )
        alt = alt_from_title(title)
        caption = claim.strip().strip('"').strip("'")
        block = figure_block(stem, alt, caption)
        if MARKER in body:
            body = re.sub(
                rf"{re.escape(MARKER)}.*?</figure>\s*",
                "",
                body,
                count=1,
                flags=re.S,
            )
        body = block + body.lstrip("\n")
        path.write_text(f"---\n{fm_new}---\n{body}", encoding="utf-8")
        updated += 1
    print(f"embedded figures in {updated} drafts")
    return 0 if updated else 1


def yaml_quote(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


if __name__ == "__main__":
    raise SystemExit(main())
