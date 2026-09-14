#!/usr/bin/env python3
"""Embed PR #236 schematic figures into PR #253 magazine essays (one-way merge helper)."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "content" / "furniture-history-ancient-blog"
GRAPHICS_REF = "origin/cursor/furniture-ancient-graphics-2a96"
DRAFTS_GLOB = "content/furniture-history-ancient-blog/drafts"


def graphics_figure_block(asset_slug: str) -> str:
    rel = f"{DRAFTS_GLOB}/{_draft_file_for_slug(asset_slug)}"
    text = subprocess.check_output(["git", "show", f"{GRAPHICS_REF}:{rel}"], text=True)
    m = re.search(r"^# .+?\n\n", text, re.M)
    if not m:
        raise ValueError(f"no body in graphics draft for {asset_slug}")
    start = m.end()
    m2 = re.search(r"\n## Evidence and argument", text)
    if not m2:
        raise ValueError(f"no figure section end in {asset_slug}")
    block = text[start : m2.start()].strip()
    block = block.replace("../assets/", "assets/")
    return block + "\n"


def _draft_file_for_slug(asset_slug: str) -> str:
    out = subprocess.check_output(
        ["git", "ls-tree", "-r", "--name-only", GRAPHICS_REF, DRAFTS_GLOB],
        text=True,
    )
    for path in out.strip().splitlines():
        if path.endswith(f"-{asset_slug}.md"):
            return Path(path).name
    raise KeyError(asset_slug)


def split_front_matter(text: str) -> tuple[str, str]:
    m = re.match(r"^(---\n.*?\n---\n)(.*)$", text, re.S)
    if not m:
        raise ValueError("missing front matter")
    return m.group(1), m.group(2)


def graphics_yaml_block(asset_slugs: list[str]) -> str:
    lines = ["graphics:"]
    for slug in asset_slugs:
        lines.append(f"  - asset_slug: {slug}")
        lines.append(f"    path: assets/{slug}/")
        lines.append(f'    status: embedded')
    return "\n".join(lines) + "\n"


def update_front_matter(fm_block: str, asset_slugs: list[str]) -> str:
    inner = fm_block[4:-4]
    inner = re.sub(
        r"^graphics:\n(?:  - [^\n]+\n(?:    [^\n]+\n)*)*",
        "",
        inner,
        flags=re.M,
    )
    block = graphics_yaml_block(asset_slugs)
    return f"---\n{inner.rstrip()}\n{block}---\n"


def strip_embedded_figures(body: str) -> str:
    """Remove markdown schematic blocks (graphics pack embed convention)."""
    return re.sub(
        r"\n!\[[^\]]*\]\(assets/[^)]+\)\n\n\*Fig\. \d+\.\*[^\n]*\n",
        "\n",
        body,
    )


def inject_figures(body: str, blocks: list[str], force: bool = False) -> str:
    if not blocks:
        return body
    body = body.lstrip("\n")
    joined = "\n\n".join(blocks).strip() + "\n"
    marker = "assets/"
    if not force and marker in body.split("\n## ", 1)[0]:
        return body
    if force:
        body = strip_embedded_figures(body)
        body = re.sub(r"\n\*Fig\. \d+\.\*[^\n]*\n", "\n", body)
    m = re.match(r"^(# .+?\n\n)", body)
    if m:
        idx = m.end()
        return body[:idx] + joined + "\n" + body[idx:]
    m = re.search(r"\n(## .+?\n)", body)
    if not m:
        return body.rstrip() + "\n\n" + joined
    idx = m.start(1)
    intro = body[:idx].rstrip()
    rest = body[idx:].lstrip("\n")
    return intro + "\n\n" + joined + "\n" + rest


def main() -> None:
    import sys

    force = "--force" in sys.argv
    mapping: dict[str, list[str]] = yaml.safe_load((PACK / "GRAPHIC_MAP.yaml").read_text())
    for stem, slugs in mapping.items():
        path = PACK / f"{stem}.md"
        if not path.exists():
            raise SystemExit(f"missing prose file: {path}")
        blocks = [graphics_figure_block(s) for s in slugs]
        text = path.read_text(encoding="utf-8")
        fm, body = split_front_matter(text)
        body = inject_figures(body, blocks, force=force)
        fm = update_front_matter(fm, slugs)
        path.write_text(fm.rstrip() + "\n\n" + body.lstrip("\n"), encoding="utf-8")
        print(f"updated {path.name} ({len(slugs)} slug(s))")


if __name__ == "__main__":
    main()
