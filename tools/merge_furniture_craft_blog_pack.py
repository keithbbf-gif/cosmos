#!/usr/bin/env python3
"""Embed graphics-branch SVG figures into magazine prose drafts (one-way merge helper)."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "content" / "furniture-craft-blog"
GRAPHICS_REF = "origin/cursor/furniture-craft-graphics-99ed"
DRAFTS = PACK / "drafts"


def graphics_draft_meta() -> dict[str, dict]:
    out = subprocess.check_output(
        ["git", "ls-tree", "-r", "--name-only", GRAPHICS_REF, "content/furniture-craft-blog/drafts"],
        text=True,
    )
    meta: dict[str, dict] = {}
    for rel in out.strip().splitlines():
        if not rel.endswith(".md"):
            continue
        text = subprocess.check_output(["git", "show", f"{GRAPHICS_REF}:{rel}"], text=True)
        m = re.search(r"^---\n(.*?)\n---", text, re.S)
        if not m:
            continue
        fm = yaml.safe_load(m.group(1)) or {}
        slug = fm.get("slug")
        if not slug:
            continue
        graphic = fm.get("graphic") or {}
        cap = ""
        fc = re.search(r"<figcaption><strong>Figure \d+\.</strong>\s*(.*?)</figcaption>", text)
        if fc:
            cap = fc.group(1).strip()
        meta[slug] = {
            "primary": graphic.get("primary", ""),
            "alt": graphic.get("alt", ""),
            "caption": cap,
        }
    return meta


def figure_html(asset_slug: str, fig_num: int, info: dict) -> str:
    primary = info["primary"]
    if not primary.startswith("assets/"):
        primary = f"assets/{asset_slug}/{Path(primary).name}"
    rel = f"../{primary}"
    alt = info.get("alt") or asset_slug.replace("-", " ")
    caption = info.get("caption") or alt
    return (
        f'<figure class="craft-figure">\n'
        f'  <img src="{rel}" alt="{alt}" width="640" height="420" loading="lazy" />\n'
        f"  <figcaption><strong>Figure {fig_num}.</strong> {caption}</figcaption>\n"
        f"</figure>\n"
    )


def split_front_matter(text: str) -> tuple[str, str, str]:
    m = re.match(r"^(---\n.*?\n---\n)(.*)$", text, re.S)
    if not m:
        raise ValueError("missing front matter")
    return m.group(1), m.group(2), text


def inject_figures(body: str, blocks: list[str], force: bool = False) -> str:
    if not blocks:
        return body
    joined = "\n\n".join(blocks).strip() + "\n"
    if not force and "<figure class=\"craft-figure\">" in body:
        return body
    if force and "<figure class=\"craft-figure\">" in body:
        body = re.sub(
            r"\n<figure class=\"craft-figure\">.*?</figure>\n",
            "\n",
            body,
            flags=re.S,
        )
    m = re.search(r"\n(## .+?\n)", body)
    if not m:
        return body.rstrip() + "\n\n" + joined
    idx = m.start(1)
    intro = body[:idx].rstrip()
    rest = body[idx:].lstrip("\n")
    return intro + "\n\n" + joined + "\n" + rest


def graphics_yaml_block(asset_slugs: list[str], meta: dict[str, dict]) -> str:
    lines = ["graphics:"]
    for slug in asset_slugs:
        g = meta.get(slug, {})
        path = g.get("primary", f"assets/{slug}/")
        alt = g.get("alt", "") or slug.replace("-", " ")
        caption = g.get("caption", "") or alt
        lines.append(f"  - asset_slug: {slug}")
        lines.append(f"    path: {path}")
        lines.append(f'    alt: "{alt.replace(chr(34), chr(39))}"')
        cap_esc = caption.replace('"', "'")
        lines.append(f'    caption: "{cap_esc}"')
    return "\n".join(lines) + "\n"


def update_front_matter(fm_block: str, asset_slugs: list[str], meta: dict[str, dict]) -> str:
    inner = fm_block[4:-4]  # strip ---\n and trailing ---\n
    if re.search(r"^graphics:\s*$", inner, re.M):
        inner = re.sub(r"^graphics:.*?(?=\n\S|\Z)", "", inner, flags=re.S)
    block = graphics_yaml_block(asset_slugs, meta)
    return f"---\n{inner.rstrip()}\n{block}---\n"


def main() -> None:
    import sys

    force = "--force" in sys.argv
    mapping = yaml.safe_load((PACK / "GRAPHIC_MAP.yaml").read_text())
    meta = graphics_draft_meta()
    for path in sorted(DRAFTS.glob("*.md")):
        prose_slug = None
        text = path.read_text(encoding="utf-8")
        fm0 = re.search(r"^---\n(.*?)\n---", text, re.S)
        if fm0:
            prose_slug = (yaml.safe_load(fm0.group(1)) or {}).get("slug")
        if not prose_slug or prose_slug not in mapping:
            raise SystemExit(f"no graphic map for {path.name} ({prose_slug})")
        asset_slugs = mapping[prose_slug]
        blocks = []
        for i, aslug in enumerate(asset_slugs, start=1):
            if aslug not in meta:
                raise SystemExit(f"unknown graphics slug {aslug} for {prose_slug}")
            blocks.append(figure_html(aslug, i, meta[aslug]))
        fm_block, body, _ = split_front_matter(text)
        new_fm = update_front_matter(fm_block, asset_slugs, meta)
        new_body = inject_figures(body, blocks, force=force)
        path.write_text(new_fm + new_body, encoding="utf-8")
        print(f"merged {path.name} ← {', '.join(asset_slugs)}")


if __name__ == "__main__":
    main()
