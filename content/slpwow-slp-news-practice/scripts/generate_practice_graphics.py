#!/usr/bin/env python3
"""Generate SVG explainers, embed snippets, and patch articles for image+SEO."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = Path(__file__).resolve().parent
SPECS_PATH = SCRIPTS / "graphics_specs.json"
ASSETS = ROOT / "assets"
EMBEDS = ROOT / "embeds"
ART = ROOT / "articles"

sys.path.insert(0, str(SCRIPTS))
from svg_builder import build_svg  # noqa: E402

FIGURE_CREDIT = (
    "SLPWOW SLP News — practice pack — original editorial SVG. "
    "Not billing, legal, or clinical advice."
)


def figure_html(slug: str, filename: str, alt: str, caption: str) -> str:
    src = f"../assets/{slug}/{filename}"
    return f"""<figure class="slpwow-figure slpwow-figure--infographic" itemscope itemtype="https://schema.org/ImageObject">
  <img
    src="{src}"
    alt="{alt}"
    width="880"
    height="420"
    loading="lazy"
    decoding="async"
    itemprop="contentUrl"
  />
  <figcaption itemprop="caption">
    <strong>Figure 1.</strong> {caption}
    <span class="figure-credit">{FIGURE_CREDIT}</span>
  </figcaption>
</figure>"""


def embed_md(slug: str, filename: str, alt: str, caption: str) -> str:
    body = figure_html(slug, filename, alt, caption)
    return f"# Embed — {slug}\n\n```html\n{body}\n```\n"


def patch_article(path: Path, figure: str, slug: str, filename: str) -> None:
    text = path.read_text(encoding="utf-8")
    if "<figure" in text:
        return
    m = re.match(r"^(---\s*\n.*?\n---\s*\n)(.*)$", text, re.S)
    if not m:
        text = text.rstrip() + "\n\n" + figure + "\n"
        path.write_text(text, encoding="utf-8")
        return
    fm, body = m.group(1), m.group(2)
    featured = f"featured_image: assets/{slug}/{filename}\n"
    if "featured_image:" not in fm:
        fm = fm.replace("\n---\n", f"\n{featured}---\n", 1)
    body = body.rstrip() + "\n\n" + figure + "\n"
    path.write_text(fm + body, encoding="utf-8")


def write_rights(rows: list[dict]) -> None:
    lines = [
        "# Rights — SLPWOW SLP News practice pack graphics",
        "",
        "All vector assets under `assets/` in this pack unless noted.",
        "",
        "| Asset path | Creator / rightsholder | License | Credit line (publish) | Notes |",
        "| --- | --- | --- | --- | --- |",
    ]
    for r in rows:
        rel = f"assets/{r['slug']}/{r['filename']}"
        lines.append(
            f"| `{rel}` | SLPWOW editorial (this repo) | "
            f"All rights reserved; practice may publish on slpwow.com | "
            f"“SLPWOW — original schematic” | Typographic SVG; no photographs. |"
        )
    lines.extend(
        [
            "",
            "## Excluded by policy",
            "",
            "- No stock patient photography.",
            "- No AI-generated faces or synthetic likenesses (`PHOTO_NOTES.md`).",
            "",
            "## Third-party text",
            "",
            "CMS, ASHA, ED, IDDSI, and society materials are cited in article YAML and prose. "
            "Diagrams are editorial schematics; verify dollar figures and dates on live primary pages.",
            "",
        ]
    )
    (ROOT / "RIGHTS.md").write_text("\n".join(lines), encoding="utf-8")


def write_checklist(rows: list[dict]) -> None:
    lines = [
        "# Graphics checklist — SLPWOW SLP News (practice wave)",
        "",
        "| Slug | Asset | Embed | In article | Status |",
        "|------|-------|-------|------------|--------|",
    ]
    for r in rows:
        lines.append(
            f"| `{r['slug']}` | `{r['filename']}` | "
            f"`embeds/{r['slug']}.md` | `articles/*-{r['slug']}.md` | **Ready** |"
        )
    lines.extend(
        [
            "",
            "- [x] SVG `<title>` + `<desc>` on all practice-wave assets",
            "- [x] `<figure>` / `<figcaption>` with schema.org `ImageObject` in articles",
            "- [x] `RIGHTS.md` inventory",
            "- [x] No AI faces",
            "- [x] `python scripts/regenerate_graphics_index.py`",
            "",
        ]
    )
    (ROOT / "GRAPHICS_CHECKLIST.md").write_text("\n".join(lines), encoding="utf-8")


def find_article(slug: str) -> Path | None:
    hits = list(ART.glob(f"*-{slug}.md"))
    return hits[0] if hits else None


def main() -> int:
    specs = json.loads(SPECS_PATH.read_text(encoding="utf-8"))
    EMBEDS.mkdir(exist_ok=True)
    rows: list[dict] = []
    for spec in specs:
        slug = spec["slug"]
        slug_dir = ASSETS / slug
        slug_dir.mkdir(parents=True, exist_ok=True)
        bands = [(b["strong"], b["detail"]) for b in spec["bands"]]
        svg = build_svg(
            title=spec["title"],
            desc=spec["desc"],
            headline=spec["headline"],
            subhead=spec["subhead"],
            layout=spec["layout"],
            bands=bands,
        )
        out_path = slug_dir / spec["filename"]
        out_path.write_text(svg, encoding="utf-8")
        fig = figure_html(slug, spec["filename"], spec["alt"], spec["caption"])
        (EMBEDS / f"{slug}.md").write_text(
            embed_md(slug, spec["filename"], spec["alt"], spec["caption"]),
            encoding="utf-8",
        )
        art = find_article(slug)
        if art:
            patch_article(art, fig, slug, spec["filename"])
        else:
            print(f"WARN: no article for slug {slug}", file=sys.stderr)
        rows.append({"slug": slug, "filename": spec["filename"]})
    write_rights(rows)
    write_checklist(rows)
    regen = SCRIPTS / "regenerate_graphics_index.py"
    if regen.is_file():
        subprocess.run([sys.executable, str(regen)], check=True, cwd=ROOT)
    print(f"Generated {len(rows)} graphics under {ASSETS}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
