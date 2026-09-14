#!/usr/bin/env python3
"""Inject SEO YAML, disclaimer, and hero <figure> into draft markdown files."""
from __future__ import annotations

import re
from pathlib import Path

from build_figures import SPECS

ROOT = Path(__file__).resolve().parent
FRONT_RE = re.compile(r"^---\n(.*?)\n---\n", re.S)
FIGURE_RE = re.compile(r'<figure class="sn-rd-figure', re.I)
DISCLAIMER = (
    "This is draft sports-nutrition copy for coaches, athletes, and sports RDs. "
    "It is not medical advice, not a meal plan, and not cleared for public use."
)


def rel_figure_path(article: Path, slug: str, ext: str) -> str:
    depth = len(article.relative_to(ROOT).parts) - 1
    prefix = "/".join([".."] * depth)
    return f"{prefix}/figures/{slug}/figure.{ext}"


def figure_block(article: Path, slug: str, spec: dict[str, str]) -> str:
    ext = "jpg" if spec["status"] == "cleared-pd" else "svg"
    src = rel_figure_path(article, slug, ext)
    mod = "photo" if ext == "jpg" else "chart"
    alt = spec["alt"]
    caption = spec["caption"]
    credit = spec["credit"]
    strong = "Photograph." if ext == "jpg" else "Schematic only."
    return f"""
<figure class="sn-rd-figure sn-rd-figure--{mod}">
  <img
    src="{src}"
    alt="{alt}"
    width="640"
    height="400"
    loading="lazy"
  />
  <figcaption>
    <strong>{strong}</strong> {caption}
    <span class="figure-credit">{credit} See figures/{slug}/RIGHTS.md.</span>
  </figcaption>
</figure>
"""


def meta_description(spec: dict[str, str], title: str) -> str:
    base = spec["caption"]
    text = base[:157] + "…" if len(base) > 158 else base
    if len(text) < 80:
        text = f"{title}. {text}"
    return text[:160]


def patch_file(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    m = FRONT_RE.match(text)
    if not m:
        raise SystemExit(f"no front matter: {path}")
    fm_lines = m.group(1).splitlines()
    fm: dict[str, str] = {}
    for line in fm_lines:
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip().strip('"')
    slug = fm.get("slug", "")
    if slug not in SPECS:
        raise SystemExit(f"unknown slug {slug} in {path}")
    spec = SPECS[slug]
    title = fm.get("title", "").strip('"')
    ext = "jpg" if spec["status"] == "cleared-pd" else "svg"
    hero = f"figures/{slug}/figure.{ext}"

    new_keys = {
        "meta_description": meta_description(spec, title),
        "hero_figure": hero,
        "figure_status": spec["status"],
    }
    out_lines: list[str] = []
    for line in fm_lines:
        key = line.split(":", 1)[0].strip()
        if key in new_keys:
            continue
        out_lines.append(line)
    out_lines.append(f'meta_description: "{new_keys["meta_description"]}"')
    out_lines.append(f'hero_figure: "{new_keys["hero_figure"]}"')
    out_lines.append(f'figure_status: {new_keys["figure_status"]}')

    body = text[m.end() :]
    if FIGURE_RE.search(body):
        print(f"skip (already has figure): {path.name}")
        return
    block = figure_block(path, slug, spec)
    insert = f"\n{DISCLAIMER}\n{block}\n\n"
    # After front matter, before first heading
    body = insert + body.lstrip("\n")
    path.write_text(f"---\n" + "\n".join(out_lines) + f"\n---\n" + body, encoding="utf-8")
    print(f"patched {path.relative_to(ROOT)}")


def main() -> None:
    for stage in sorted(ROOT.glob("stage-*")):
        for md in sorted(stage.glob("*.md")):
            patch_file(md)


if __name__ == "__main__":
    main()
