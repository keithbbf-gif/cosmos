#!/usr/bin/env python3
"""Embed <figure> blocks and SEO front matter into finishing-chemistry drafts."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "content" / "furniture-finishing-chemistry"

# slug -> (photo basename under photos/, photo alt, photo caption credit line short)
PHOTO_BY_SLUG: dict[str, tuple[str, str, str]] = {
    "what-a-finish-actually-is": (
        "oak-end-grain-quartersawn.jpg",
        "End-grain cutting board showing ray flecks and pores",
        "End grain shows rays and pores — the finish lands on this anatomy. Photo: Wikimedia Commons, CC BY-SA 4.0.",
    ),
    "film-versus-penetrating": (
        "walnut-pore-close.jpg",
        "End-grain wood surface with open pores",
        "Open end grain drinks finish unevenly if you pretend the surface is closed. Photo: Wikimedia Commons, CC BY-SA 2.0.",
    ),
    "binder-solvent-additive": (
        "paint-brushes-studio.jpg",
        "Clean paint brushes representing finish application tools",
        "Brushes and pads move binder and carrier onto wood — tool cleanliness is part of chemistry. Photo: Wikimedia Commons, CC0.",
    ),
    "why-some-woods-drink-and-some-spit": (
        "teak-wood-texture.jpg",
        "Teak wood surface with natural oily appearance",
        "Teak carries its own extractives — the finish must deal with an oily substrate. Photo: Wikimedia Commons, CC BY 2.0.",
    ),
    "linseed-oil-polymerizes": (
        "linseed-oil-bottle.jpg",
        "Linseed oil in a glass bottle",
        "Raw linseed oil polymerizes in thin films — the bottle is not the cure schedule. Photo: Wikimedia Commons, CC BY-SA 3.0.",
    ),
    "shellac-is-a-bug-resin": (
        "shellac-flakes.jpg",
        "Amber shellac flakes before dissolving in alcohol",
        "Shellac flake dissolves in alcohol — pound cut decides how much resin lands on the wood. Photo: Wikimedia Commons, CC BY-SA 2.0.",
    ),
    "waterborne-means-emulsion": (
        "waterborne-latex-paint.jpg",
        "Craftsman applying varnish to bare wood with a brush",
        "Thin wet coats level like waterborne builds — the film is made by repeated passes, not one flood. Photo: Wikimedia Commons, CC BY-SA 4.0.",
    ),
    "milk-paint-is-casein-and-lime": (
        "milk-paint-brush.jpg",
        "Matte pigmented coating on a wood panel",
        "Matte coat on wood — read the hand before you promise chalk. Photo: Wikimedia Commons, CC BY-SA 4.0 (encaustic panel, illustrative).",
    ),
    "sanding-decides-the-film": (
        "orbital-sander-wood.jpg",
        "Random-orbit sander on a wood panel",
        "The sander decides what the finish is allowed to hide. Photo: Wikimedia Commons, CC BY 2.0.",
    ),
    "rags-air-and-the-fire-you-do-not-see-coming": (
        "linseed-oil-bottle.jpg",
        "Linseed oil container — oxidizing oils heat in piled rags",
        "Oxidizing oils in a crumpled pile can self-heat — lay rags flat or soak them. Photo: Wikimedia Commons, CC BY-SA 3.0.",
    ),
    "a-staged-dining-table-schedule": (
        "dining-table-wood.jpg",
        "Wooden table furniture study (museum object photograph)",
        "A table finish schedule is measured in cure days, not showroom sheen. Photo: Wikimedia Commons, CC0 (NGA Open Access).",
    ),
}

DEFAULT_PHOTO = (
    "oak-end-grain-quartersawn.jpg",
    "End-grain cutting board showing ray flecks and pores",
    "End grain shows rays and pores — the finish lands on this anatomy. Photo: Wikimedia Commons, CC BY-SA 4.0.",
)


def load_graphics_meta() -> dict[str, tuple[str, str]]:
    import runpy

    mod = runpy.run_path(
        str(ROOT / "tools" / "generate_furniture_finishing_chemistry_graphics.py"),
        run_name="generate_furniture_finishing_chemistry_graphics",
    )
    out: dict[str, tuple[str, str]] = {}
    for g in mod["GRAPHICS"]:
        out[g.slug] = (g.alt, g.caption)
    return out


def meta_description(body: str, title: str) -> str:
    body_no_fig = re.sub(r"<figure[\s\S]*?</figure>\s*", "", body, count=0)
    lines = body_no_fig.splitlines()
    chunks: list[str] = []
    for line in lines:
        if line.startswith("# ") or line.startswith("## "):
            if line.startswith("## "):
                break
            continue
        s = line.strip()
        if s and not s.startswith("<"):
            chunks.append(s)
    text = re.sub(r"\s+", " ", " ".join(chunks)).strip()
    if len(text) > 155:
        text = text[:152].rsplit(" ", 1)[0] + "…"
    if not text:
        text = title
    return text


def inject(path: Path, graphics: dict[str, tuple[str, str]]) -> None:
    raw = path.read_text(encoding="utf-8")
    if not raw.startswith("---"):
        return
    parts = raw.split("---", 2)
    if len(parts) < 3:
        return
    fm, body = parts[1], parts[2]
    slug_m = re.search(r"^slug:\s*(\S+)\s*$", fm, re.M)
    title_m = re.search(r"^title:\s*(.+)\s*$", fm, re.M)
    if not slug_m:
        return
    slug = slug_m.group(1)
    title = title_m.group(1).strip() if title_m else slug
    if "graphics:" in fm and "<figure" in body:
        return

    g_alt, g_cap = graphics.get(slug, ("Shop finishing diagram", "Shop diagram for this draft."))
    photo = PHOTO_BY_SLUG.get(slug, DEFAULT_PHOTO)
    p_file, p_alt, p_cap = photo

    md = meta_description(body, title)
    extra = f"""
meta_description: "{md.replace('"', "'")}"
graphics:
  - asset_slug: {slug}
    path: assets/{slug}/shop-diagram.svg
    alt: "{g_alt.replace('"', "'")}"
    caption: "{g_cap.replace('"', "'")}"
figures:
  - id: photo-1
    path: photos/{p_file}
    alt: "{p_alt.replace('"', "'")}"
    caption: "{p_cap.replace('"', "'")}"
""".rstrip()

    fm = fm.rstrip() + extra + "\n"

    diagram_block = f"""
<figure class="ffc-figure">
  <img src="assets/{slug}/shop-diagram.svg" alt="{g_alt}" width="640" height="420" loading="lazy" decoding="async" />
  <figcaption><strong>Figure 1.</strong> {g_cap}</figcaption>
</figure>

<figure class="ffc-figure ffc-photo">
  <img src="photos/{p_file}" alt="{p_alt}" width="640" height="480" loading="lazy" decoding="async" />
  <figcaption><strong>Figure 2.</strong> {p_cap}</figcaption>
</figure>
"""

    body_stripped = body.lstrip("\n")
    lines = body_stripped.split("\n")
    insert_at = 0
    for i, line in enumerate(lines):
        if line.startswith("# "):
            insert_at = i + 1
            break
    # After title heading, skip blank lines then first paragraph ending
    while insert_at < len(lines) and not lines[insert_at].strip():
        insert_at += 1
    para_end = insert_at
    while para_end < len(lines):
        if para_end > insert_at and lines[para_end].startswith("## "):
            break
        if para_end > insert_at and not lines[para_end].strip():
            break
        para_end += 1
    new_lines = lines[:para_end] + [diagram_block.rstrip(), ""] + lines[para_end:]
    path.write_text("---" + fm + "---\n\n" + "\n".join(new_lines), encoding="utf-8")


def main() -> None:
    graphics = load_graphics_meta()
    for md in sorted(PACK.glob("[0-9][0-9]-*.md")):
        inject(md, graphics)
    print(f"Updated drafts in {PACK}")


if __name__ == "__main__":
    main()
