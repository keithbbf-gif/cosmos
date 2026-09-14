#!/usr/bin/env python3
"""Idempotently embed wave-1/2 figures into blog drafts and sync front-matter figures:."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DRAFTS = ROOT / "drafts"
CATALOG = ROOT / "staged" / "asset_catalog_wave2.json"
PLAN = ROOT / "staged" / "wave2_draft_figure_plan.json"

BEGIN = "<!-- ai-blog-figures:begin -->"
END = "<!-- ai-blog-figures:end -->"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def figure_html(slug: str, meta: dict, n: int) -> str:
    src = f"../assets/{slug}/{meta['file']}"
    alt = meta["alt"]
    cap = meta["caption"]
    return f"""<figure class="blog-figure">
  <img src="{src}" alt="{alt}" width="1200" loading="lazy" />
  <figcaption><strong>Figure {n}.</strong> {cap}</figcaption>
</figure>"""


def embed_block(slugs: list[str], catalog: dict) -> str:
    parts = [BEGIN]
    for i, slug in enumerate(slugs, 1):
        if slug not in catalog:
            raise KeyError(f"Unknown asset slug: {slug}")
        parts.append(figure_html(slug, catalog[slug], i))
        parts.append("")
    parts.append(END)
    return "\n".join(parts)


def insert_figures(body: str, block: str) -> str:
    if BEGIN in body and END in body:
        pre, rest = body.split(BEGIN, 1)
        _, post = rest.split(END, 1)
        return pre.rstrip() + "\n\n" + block + "\n" + post.lstrip("\n")
    idx = body.find("\n## ")
    if idx == -1:
        return body.rstrip() + "\n\n" + block + "\n"
    return body[:idx].rstrip() + "\n\n" + block + "\n" + body[idx:]


def set_figures_front_matter(fm: str, slugs: list[str]) -> str:
    lines = fm.splitlines()
    out: list[str] = []
    i = 0
    while i < len(lines):
        if lines[i].strip() == "figures:":
            i += 1
            while i < len(lines) and lines[i].startswith("  - "):
                i += 1
            continue
        out.append(lines[i])
        i += 1
    out.append("figures:")
    for slug in slugs:
        out.append(f"  - {slug}")
    return "\n".join(out)


def process_draft(text: str, slugs: list[str], catalog: dict) -> str:
    if not text.startswith("---"):
        return insert_figures(text, embed_block(slugs, catalog))
    end = text.find("\n---", 3)
    fm = text[3:end].strip()
    body = text[end + 4 :].lstrip("\n")
    fm = set_figures_front_matter(fm, slugs)
    body = insert_figures(body, embed_block(slugs, catalog))
    return f"---\n{fm}\n---\n\n{body}"


def main() -> None:
    catalog = load_json(CATALOG)
    plan = load_json(PLAN)
    for draft_name, slugs in sorted(plan.items()):
        path = DRAFTS / draft_name
        if not path.exists():
            print(f"skip missing {draft_name}")
            continue
        text = path.read_text(encoding="utf-8")
        path.write_text(process_draft(text, slugs, catalog), encoding="utf-8")
        print(f"embedded {len(slugs)} figures -> {draft_name}")


if __name__ == "__main__":
    main()
