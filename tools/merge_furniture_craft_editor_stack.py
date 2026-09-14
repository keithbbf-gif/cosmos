#!/usr/bin/env python3
"""Combine editor prose (PR #272) with graphics-merged SVG embeds (PR #263)."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from merge_furniture_craft_blog_pack import (  # noqa: E402
    DRAFTS,
    PACK,
    figure_html,
    graphics_draft_meta,
    inject_figures,
    split_front_matter,
    update_front_matter,
)

EDITOR_REF = "origin/cursor/furniture-craft-editor-dde6"


def editor_draft_relpaths() -> list[str]:
    out = subprocess.check_output(
        [
            "git",
            "ls-tree",
            "-r",
            "--name-only",
            EDITOR_REF,
            "content/furniture-craft-blog/drafts",
        ],
        text=True,
    )
    return sorted(line for line in out.strip().splitlines() if line.endswith(".md"))


def read_editor(rel: str) -> str:
    return subprocess.check_output(["git", "show", f"{EDITOR_REF}:{rel}"], text=True)


def strip_embedded_figures(body: str) -> str:
    return re.sub(
        r"\n<figure class=\"craft-figure\">.*?</figure>\n",
        "\n",
        body,
        flags=re.S,
    )


def main() -> None:
    mapping = yaml.safe_load((PACK / "GRAPHIC_MAP.yaml").read_text())
    meta = graphics_draft_meta()
    for rel in editor_draft_relpaths():
        name = Path(rel).name
        text = read_editor(rel)
        fm_block, body, _ = split_front_matter(text)
        fm = yaml.safe_load(fm_block[4:-4]) or {}
        prose_slug = fm.get("slug")
        if not prose_slug or prose_slug not in mapping:
            raise SystemExit(f"no graphic map for {name} ({prose_slug})")
        asset_slugs = mapping[prose_slug]
        blocks = []
        for i, aslug in enumerate(asset_slugs, start=1):
            if aslug not in meta:
                raise SystemExit(f"unknown graphics slug {aslug} for {prose_slug}")
            blocks.append(figure_html(aslug, i, meta[aslug]))
        body = strip_embedded_figures(body)
        new_body = inject_figures(body, blocks, force=True)
        new_fm = update_front_matter(fm_block, asset_slugs, meta)
        if fm.get("voice_check") != "edited":
            raise SystemExit(f"{name}: expected voice_check: edited from editor branch")
        out = DRAFTS / name
        out.write_text(new_fm + new_body, encoding="utf-8")
        print(f"unified {name} ← editor prose + {len(blocks)} SVG(s)")


if __name__ == "__main__":
    main()
