#!/usr/bin/env python3
"""Create or refresh markdown shells from pack_data.ARTICLES."""

from __future__ import annotations

from pathlib import Path

from pack_data import ARTICLES, DISCLAIMER

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "articles"


def yaml_list(items: list[str]) -> str:
    return "\n".join(f"  - {i}" for i in items)


def render_article(art: dict) -> str:
    fig_paths = [f"../assets/{art['slug']}/{f['file']}" for f in art["figures"]]
    return f"""---
title: "{art['title']}"
slug: {art['slug']}
meta_description: "{art['meta_description']}"
tags:
{yaml_list(art['tags'])}
era_focus: {art['era_focus']}
figures:
{yaml_list(fig_paths) if fig_paths else '  []'}
citations: []
status: draft
voice_check: pending-grok
graphics_agent: v1
---

{DISCLAIMER}

Editorial shell **#{art['num']:02d}** in the herbal-medicine history pack. Grok writer replaces stub paragraphs with sourced prose.

{art['sections'][0]['heading']}

{art['sections'][0]['body']}

{art['sections'][1]['heading']}

{art['sections'][1]['body']}
"""


def main() -> None:
    ART_DIR.mkdir(parents=True, exist_ok=True)
    for art in ARTICLES:
        path = ART_DIR / art["file"]
        path.write_text(render_article(art), encoding="utf-8")
    print(f"Wrote {len(ARTICLES)} articles to {ART_DIR}/")


if __name__ == "__main__":
    main()
