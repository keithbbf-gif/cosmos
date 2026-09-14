#!/usr/bin/env python3
"""Apply IMAGE+SEO pass to butcher-block countertop guide drafts."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "content" / "butcher-block-countertops-guide"
DRAFT_DIR = PACK / "drafts"
EMBED_DIR = PACK / "embeds"

FM_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.S)

FIGURE_SPECS: dict[str, dict[str, str]] = {
    "why-this-guide": {
        "asset": "../assets/workflow/island-wood-top-schematic.svg",
        "class": "bradley-figure bradley-figure--diagram",
        "alt": "Top-down schematic of a kitchen island with an edge-grain wood countertop labeled separately from the Bradley cabinet box.",
        "width": "880",
        "height": "520",
        "caption": "A wood island top is a second contract: the box is furniture; the lid is species, grain, finish, and fasteners.",
        "credit": "Bradley butcher-block countertops guide — editorial schematic.",
    },
    "the-block-was-a-tool": {
        "asset": "../assets/historical-butcher-block/ochs-reading-terminal-market-1910s.jpg",
        "class": "bradley-figure bradley-figure--photo",
        "alt": "Historic black-and-white photograph of a butcher shop with large maple blocks at Reading Terminal Market, Philadelphia.",
        "width": "880",
        "height": "587",
        "caption": "Before the kitchen borrowed the name, the block was a shop tool — scraped, salted, and turned down when the face went hollow.",
        "credit": "Carol M. Highsmith, Library of Congress. Harry G. Ochs butcher shop, Reading Terminal Market. Public domain via Wikimedia Commons.",
    },
    "edge-grain-is-the-residential-default": {
        "asset": "../assets/grain-orientations/edge-end-face-grain.svg",
        "class": "bradley-figure bradley-figure--diagram",
        "alt": "Cross-section illustrations labeling edge grain, end grain, and face grain orientations for butcher-block island countertops.",
        "width": "880",
        "height": "360",
        "caption": "Edge grain is the residential default; end grain earns its keep as a tool; face grain is a plank top with different care.",
        "credit": "Bradley butcher-block countertops guide — editorial schematic.",
    },
    "thickness-is-structure": {
        "asset": "../assets/thickness-profile/thickness-profile.svg",
        "class": "bradley-figure bradley-figure--diagram",
        "alt": "Side elevations comparing 1.25, 1.5, and 2.5 inch butcher-block top thickness with built-up edge callout.",
        "width": "880",
        "height": "400",
        "caption": "Thickness is structure — not a mood-board slider. Fly, grain, and species pick the number.",
        "credit": "Bradley butcher-block countertops guide — editorial schematic.",
    },
    "how-the-top-gets-fastened": {
        "asset": "../assets/top-fasteners/top-fasteners.svg",
        "class": "bradley-figure bradley-figure--diagram",
        "alt": "Underside diagram of Z-clips, figure-eight washers, and slotted wood buttons fastening a wood island top to rails.",
        "width": "880",
        "height": "420",
        "caption": "Hold the lid on the box; let the field breathe. A grid of screws through the rails is the usual mistake.",
        "credit": "Bradley butcher-block countertops guide — editorial schematic.",
    },
    "oil-is-a-habit": {
        "asset": "../assets/oil-schedule/oil-maintenance-schedule.svg",
        "class": "bradley-figure bradley-figure--diagram",
        "alt": "Timeline for mineral oil maintenance on butcher-block counters: saturate week one, month one, then quarterly and winter touch-ups.",
        "width": "880",
        "height": "360",
        "caption": "Oil is a habit — heavy early, then wipe when the maple goes pale, especially under forced-air winter heat.",
        "credit": "Bradley butcher-block countertops guide — editorial schematic.",
    },
    "never-soak-never-dishwasher": {
        "asset": "../assets/care-habits/care-never-soak.svg",
        "class": "bradley-figure bradley-figure--diagram",
        "alt": "Care diagram prohibiting standing water, dishwasher cleaning, and overnight soaking on oiled wood countertops.",
        "width": "880",
        "height": "360",
        "caption": "Standing water and a dishwasher are how a pretty top becomes a cupped lid — wipe spills and dry the rim.",
        "credit": "Bradley butcher-block countertops guide — editorial schematic.",
    },
    "knives-heat-and-the-trivet": {
        "asset": "../assets/care-habits/heat-knife-trivet.svg",
        "class": "bradley-figure bradley-figure--diagram",
        "alt": "Wood island top section showing trivet for hot pans, cutting board for knives, and scorch risk on bare wood.",
        "width": "880",
        "height": "360",
        "caption": "Heat and knives are habits. The top is wood, not stone — trivet, board, and a client who will wipe.",
        "credit": "Bradley butcher-block countertops guide — editorial schematic.",
    },
    "overhang-on-wood": {
        "asset": "../assets/overhang-wood/wood-overhang-support.svg",
        "class": "bradley-figure bradley-figure--diagram",
        "alt": "Section drawing of wood countertop seating overhang with corbel bracket and typical twelve-inch fly dimension.",
        "width": "880",
        "height": "400",
        "caption": "A modest fly on edge grain can live with brackets; pride is not a substitute for steel under a long breakfast side.",
        "credit": "Bradley butcher-block countertops guide — editorial schematic.",
    },
    "spec-sheet-for-a-wood-top": {
        "asset": "../assets/spec-sheet/six-line-spec-sheet.svg",
        "class": "bradley-figure bradley-figure--diagram",
        "alt": "Six-line specification checklist for wood island tops: species, grain, thickness, finish, fasteners, and wet-work policy.",
        "width": "880",
        "height": "480",
        "caption": "Six honest lines — species through wet work — plus date, mill, dealer, and cut allowed yes or no.",
        "credit": "Bradley butcher-block countertops guide — editorial schematic.",
    },
    "sequence-job-to-care-card": {
        "asset": "../assets/workflow/job-to-care-sequence.svg",
        "class": "bradley-figure bradley-figure--diagram",
        "alt": "Flow from room measure to grain and species choice, spec sheet, build and oil, and care card delivery.",
        "width": "880",
        "height": "360",
        "caption": "Short path: measure, spec the lid, build and oil, tape the care card where the next owner will find it.",
        "credit": "Bradley butcher-block countertops guide — editorial schematic.",
    },
    "aftercare-card": {
        "asset": "../assets/aftercare-card/aftercare-card-layout.svg",
        "class": "bradley-figure bradley-figure--diagram",
        "alt": "Mock aftercare card for oiled butcher-block island tops with oil schedule and never-soak reminders.",
        "width": "880",
        "height": "420",
        "caption": "Tape the care card in the trash pull. Houses change hands; the next owner should not guess whether they may cut.",
        "credit": "Bradley butcher-block countertops guide — editorial schematic.",
    },
}

DEFAULT_FEATURED = "../assets/_shared/series-featured.svg"
DROP_KEYS = {"meta_description", "featured_image", "figures"}


def meta_description(title: str, slug: str) -> str:
    base = title.rstrip(".")
    if slug in FIGURE_SPECS:
        return (
            f"{base} — butcher-block island countertop guide for Bradley wood tops: "
            "species, oil, fasteners, and shop habits. Staged draft."
        )
    return (
        f"{base} — wood island tops and butcher-block care from a Warren shop voice. "
        "History, construction, and living with oiled maple. Staged draft."
    )


def figure_html(spec: dict[str, str]) -> str:
    return f"""<figure class="{spec['class']}">
  <img
    src="{spec['asset']}"
    alt="{spec['alt']}"
    width="{spec['width']}"
    height="{spec['height']}"
    loading="lazy"
  />
  <figcaption>
    {spec['caption']}
    <span class="figure-credit">{spec['credit']}</span>
  </figcaption>
</figure>"""


def strip_seo_keys(fm_lines: list[str]) -> list[str]:
    out: list[str] = []
    i = 0
    while i < len(fm_lines):
        line = fm_lines[i]
        key = line.split(":", 1)[0].strip() if ":" in line else line.strip()
        if key in DROP_KEYS:
            if key == "figures":
                i += 1
                while i < len(fm_lines) and fm_lines[i].startswith("  -"):
                    i += 1
                continue
            i += 1
            continue
        out.append(line)
        i += 1
    return out


def parse_frontmatter(text: str) -> tuple[list[str], str]:
    m = FM_RE.match(text)
    if not m:
        return [], text
    return m.group(1).splitlines(), m.group(2)


def insert_figure(body: str, html: str) -> str:
    if "bradley-figure" in body:
        return body
    paras = re.split(r"\n\s*\n", body.strip(), maxsplit=1)
    if len(paras) == 1:
        return body.strip() + "\n\n" + html + "\n"
    first, rest = paras[0], paras[1]
    return f"{first}\n\n{html}\n\n{rest}"


def main() -> int:
    EMBED_DIR.mkdir(parents=True, exist_ok=True)
    updated = 0
    for path in sorted(DRAFT_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        fm_lines, body = parse_frontmatter(text)
        if not fm_lines:
            print(f"skip {path.name}: no frontmatter")
            continue
        fm_map: dict[str, str] = {}
        for ln in fm_lines:
            if ":" in ln and not ln.startswith("  -"):
                k, v = ln.split(":", 1)
                fm_map[k.strip()] = v.strip().strip('"')
        slug = fm_map.get("slug", "")
        title = fm_map.get("title", slug)
        base_lines = strip_seo_keys(fm_lines)
        base_lines.append(f'meta_description: "{meta_description(title, slug)}"')
        spec = FIGURE_SPECS.get(slug)
        if spec:
            base_lines.append(f"featured_image: {spec['asset']}")
            base_lines.append("figures:")
            base_lines.append(f"  - {spec['asset']}")
            html = figure_html(spec)
            body = insert_figure(body, html)
            (EMBED_DIR / f"{slug}.md").write_text(html + "\n", encoding="utf-8")
        else:
            base_lines.append(f"featured_image: {DEFAULT_FEATURED}")
        out = "---\n" + "\n".join(base_lines) + "\n---\n" + body.lstrip("\n")
        if out != text:
            path.write_text(out, encoding="utf-8")
            updated += 1
    print(f"updated {updated} drafts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
