#!/usr/bin/env python3
"""Embed figures and SEO frontmatter into finishing-chemistry drafts."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = Path(__file__).resolve().parent
SPECS = json.loads((SCRIPT_DIR / "ffc_graphics_specs.json").read_text(encoding="utf-8"))
PHOTOS = json.loads((SCRIPT_DIR / "ffc_photo_slots.json").read_text(encoding="utf-8"))

FIGURE_RE = re.compile(r"<figure\b", re.I)


def meta_description(title: str, caption: str) -> str:
    desc = caption if len(caption) <= 155 else caption[:152].rsplit(" ", 1)[0] + "…"
    return desc


def figure_block(slug: str, spec: dict, photo: dict | None) -> str:
    alt = spec["alt"]
    cap = spec["caption"]
    svg = f"assets/{slug}/shop-diagram.svg"
    lines = [
        "",
        '<figure class="ffc-figure">',
        f'  <img src="{svg}" alt="{alt}" width="640" height="420" loading="lazy" decoding="async" />',
        f"  <figcaption><strong>Figure 1.</strong> {cap}</figcaption>",
        "</figure>",
    ]
    if photo:
        lines.extend(
            [
                "",
                '<figure class="ffc-figure ffc-photo">',
                f'  <img src="{photo["path"]}" alt="{photo["alt"]}" width="{photo.get("width", 640)}" height="{photo.get("height", 480)}" loading="lazy" decoding="async" />',
                f'  <figcaption><strong>Photo 2.</strong> {photo["caption"]} (<a href="{photo["credit_url"]}">{photo["credit_label"]}</a>)</figcaption>',
                "</figure>",
            ]
        )
    return "\n".join(lines) + "\n"


def patch_frontmatter(fm: str, slug: str, spec: dict, photo: dict | None) -> str:
    lines = [ln for ln in fm.strip().splitlines()]
    keys = {ln.split(":", 1)[0].strip() for ln in lines if ":" in ln and not ln.startswith(" ")}
    title_line = next((ln for ln in lines if ln.startswith("title:")), "title: Draft")
    title = title_line.split(":", 1)[1].strip().strip('"')
    if "meta_description" not in keys:
        lines.append(f'meta_description: "{meta_description(title, spec["caption"])}"')
    if "graphic" not in keys:
        lines.append("graphic:")
        lines.append(f'  primary: "assets/{slug}/shop-diagram.svg"')
        lines.append(f'  alt: "{spec["alt"]}"')
    if photo and "photo" not in keys:
        lines.append("photo:")
        lines.append(f'  path: "{photo["path"]}"')
        lines.append(f'  license: "{photo["license"]}"')
        lines.append(f'  credit: "{photo["credit_label"]}"')
    return "\n".join(lines) + "\n"


def insert_figure(body: str, block: str) -> str:
    if FIGURE_RE.search(body):
        return body
    m = re.search(r"^(## .+?\n\n)(.+?\n\n)", body, re.M | re.S)
    if m:
        return body[: m.end()] + block + body[m.end() :]
    return body + block


def split_fm(text: str) -> tuple[str, str] | None:
    if not text.startswith("---"):
        return None
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    return parts[1], parts[2]


def process_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    split = split_fm(text)
    if not split:
        return False
    fm, body = split
    slug_m = re.search(r"^slug:\s*(.+)$", fm, re.M)
    if not slug_m:
        return False
    slug = slug_m.group(1).strip()
    if slug in ("manifest", "furniture-finishing-chemistry"):
        return False
    spec = SPECS.get(slug)
    if not spec:
        print(f"skip no spec: {slug}")
        return False
    photo = PHOTOS.get(slug)
    new_fm = patch_frontmatter(fm, slug, spec, photo)
    new_body = insert_figure(body, figure_block(slug, spec, photo))
    out = "---\n" + new_fm + "---" + new_body
    if out != text:
        path.write_text(out, encoding="utf-8")
        return True
    return False


def main() -> None:
    changed = sum(1 for p in sorted(ROOT.glob("[0-9][0-9]-*.md")) if process_file(p))
    print(f"Updated {changed} drafts")


if __name__ == "__main__":
    main()
