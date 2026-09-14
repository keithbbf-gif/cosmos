#!/usr/bin/env python3
"""Magazine-grade SVG figures for furniture-woods-500y-blog (small curated set)."""
from __future__ import annotations

import html
import json
import math
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
EMBEDS = ROOT / "staged-embeds"
SLUGS_FILE = ROOT / "writer-slugs.json"

# Design tokens — restrained craft / editorial
INK = "#1c1917"
PAPER = "#faf9f6"
MUTED = "#78716c"
RULE = "#e7e5e4"
LANE_A = "#a8a29e"
LANE_B = "#78716c"
LANE_C = "#57534e"
FONT_SERIF = "Georgia, 'Iowan Old Style', 'Times New Roman', serif"
FONT_SANS = "'Helvetica Neue', Helvetica, Arial, sans-serif"

# USDA FPL Wood Handbook / Wood Database — species means (Janka lbf, density kg/m³ OD)
CORE_SPECIES = [
    ("European oak", "Quercus petraea / Q. robur", 1120, 680),
    ("White oak", "Quercus alba", 1360, 755),
    ("Honduran mahogany", "Swietenia macrophylla", 900, 640),
    ("Black walnut", "Juglans nigra", 1010, 610),
    ("Teak", "Tectona grandis", 1155, 655),
    ("Indian rosewood", "Dalbergia latifolia", 2440, 850),
    ("Brazilian rosewood", "Dalbergia nigra", 2790, 865),
    ("Hard maple", "Acer saccharum", 1450, 705),
    ("Black cherry", "Prunus serotina", 950, 560),
    ("Eastern white pine", "Pinus strobus", 380, 350),
]

GLOBAL_MILESTONES = [
    (1550, "Baltic oak\npacking ports"),
    (1607, "Chesapeake\nsoftwood frame"),
    (1720, "Caribbean\nmahogany"),
    (1830, "Rosewood\nveneer boom"),
    (1856, "Burma teak\nimperial yards"),
    (1900, "Factory era\n& plywood"),
    (1973, "CITES\nsigned"),
    (2017, "Dalbergia\nAppendix II"),
]

TRADE_LANES = [
    (
        "Baltic & North Sea oak",
        [("Riga & Danzig markets", 1580), ("Dutch & English shipping", 1660), ("Royal Navy contracts", 1755), ("Local oak revival", 1885)],
    ),
    (
        "Atlantic mahogany",
        [("Jamaica exports", 1725), ("London cabinet peak", 1765), ("Cuba & Hispaniola", 1820), ("Swietenia App. II", 1992)],
    ),
    (
        "Indian Ocean teak",
        [("Bombay dockyards", 1842), ("Irrawaddy rafting", 1872), ("Colonial reservations", 1925), ("Myanmar log ban", 2014)],
    ),
]


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def figure_svg(
    width: int,
    plot_h: int,
    figure_no: str,
    title: str,
    desc: str,
    plot: str,
    caption: str,
    source: str,
) -> str:
    cap_h = 88
    total_h = plot_h + cap_h
    header = f"""
  <text x="48" y="36" font-family="{FONT_SANS}" font-size="10" letter-spacing="0.12em" fill="{MUTED}">FIGURE {esc(figure_no)}</text>
  <text x="48" y="62" font-family="{FONT_SERIF}" font-size="22" fill="{INK}">{esc(title)}</text>
  <line x1="48" y1="74" x2="{width - 48}" y2="74" stroke="{RULE}" stroke-width="1"/>
"""
    cap_y = plot_h + 24
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {total_h}" width="{width}" height="{total_h}" role="img" aria-labelledby="title desc">
  <title id="title">{esc(title)}</title>
  <desc id="desc">{esc(desc)}</desc>
  <rect width="100%" height="100%" fill="{PAPER}"/>
  {header}
  <g transform="translate(0, 0)">
  {plot}
  </g>
  <line x1="48" y1="{plot_h}" x2="{width - 48}" y2="{plot_h}" stroke="{RULE}" stroke-width="1"/>
  <text x="48" y="{cap_y}" font-family="{FONT_SERIF}" font-size="13" fill="{INK}">{esc(caption)}</text>
  <text x="48" y="{cap_y + 20}" font-family="{FONT_SANS}" font-size="10" fill="{MUTED}">{esc(source)}</text>
</svg>
"""


def timeline_global() -> str:
    w, plot_h = 900, 340
    x0, x1 = 80, 820
    y_axis = 200
    t0, t1 = 1540, 2030
    parts: list[str] = []
    eras = [
        (1540, 1700, 0.04),
        (1700, 1830, 0.06),
        (1830, 1914, 0.05),
        (1914, 1973, 0.04),
        (1973, 2030, 0.07),
    ]
    for a, b, op in eras:
        xa = x0 + (a - t0) / (t1 - t0) * (x1 - x0)
        xb = x0 + (b - t0) / (t1 - t0) * (x1 - x0)
        parts.append(f'<rect x="{xa}" y="100" width="{xb - xa}" height="160" fill="{INK}" opacity="{op}"/>')
    parts.append(f'<line x1="{x0}" y1="{y_axis}" x2="{x1}" y2="{y_axis}" stroke="{INK}" stroke-width="1.5"/>')
    for year, label in GLOBAL_MILESTONES:
        x = x0 + (year - t0) / (t1 - t0) * (x1 - x0)
        parts.append(f'<line x1="{x}" y1="{y_axis - 10}" x2="{x}" y2="{y_axis + 10}" stroke="{INK}" stroke-width="1"/>')
        parts.append(f'<circle cx="{x}" cy="{y_axis}" r="3.5" fill="{PAPER}" stroke="{INK}" stroke-width="1.5"/>')
        above = year % 2 == 0
        ty = y_axis - 22 if above else y_axis + 28
        for i, line in enumerate(label.split("\n")):
            parts.append(
                f'<text x="{x}" y="{ty + i * 14}" text-anchor="middle" font-family="{FONT_SANS}" '
                f'font-size="11" fill="{INK}">{esc(line)}</text>'
            )
        parts.append(
            f'<text x="{x}" y="{y_axis + (48 if above else -36)}" text-anchor="middle" '
            f'font-family="{FONT_SANS}" font-size="10" fill="{MUTED}">{year}</text>'
        )
    parts.append(
        f'<text x="{x0}" y="290" font-family="{FONT_SANS}" font-size="10" fill="{MUTED}">1540</text>'
    )
    parts.append(
        f'<text x="{x1}" y="290" text-anchor="end" font-family="{FONT_SANS}" font-size="10" fill="{MUTED}">2030</text>'
    )
    plot = "\n    ".join(parts)
    return figure_svg(
        w,
        plot_h,
        "1",
        "Five centuries of furniture timber",
        "Global milestone timeline for furniture-trade woods.",
        plot,
        "Selected dates marking Baltic oak exports, Atlantic mahogany, tropical rosewood and teak, and modern CITES controls.",
        "Trade years: series historiography; CITES dates from cites.org.",
    )


def timeline_lanes() -> str:
    w, plot_h = 900, 360
    x0, x1 = 220, 860
    lanes_y = [130, 210, 290]
    colors = [LANE_A, LANE_B, LANE_C]
    t0, t1 = 1570, 2020
    parts: list[str] = []
    for idx, (lane_title, points) in enumerate(TRADE_LANES):
        y = lanes_y[idx]
        parts.append(f'<text x="48" y="{y + 4}" font-family="{FONT_SERIF}" font-size="13" fill="{INK}">{esc(lane_title)}</text>')
        parts.append(f'<line x1="{x0}" y1="{y}" x2="{x1}" y2="{y}" stroke="{RULE}" stroke-width="1"/>')
        for label, year in points:
            x = x0 + (year - t0) / (t1 - t0) * (x1 - x0)
            parts.append(f'<circle cx="{x}" cy="{y}" r="4" fill="{colors[idx]}" stroke="{INK}" stroke-width="0.75"/>')
            parts.append(
                f'<text x="{x}" y="{y - 12}" text-anchor="middle" font-family="{FONT_SANS}" '
                f'font-size="9" fill="{INK}">{esc(label)}</text>'
            )
            parts.append(
                f'<text x="{x}" y="{y + 18}" text-anchor="middle" font-family="{FONT_SANS}" '
                f'font-size="9" fill="{MUTED}">{year}</text>'
            )
    parts.append(
        f'<text x="{(x0 + x1) / 2}" y="340" text-anchor="middle" font-family="{FONT_SANS}" '
        f'font-size="10" fill="{MUTED}">Milestone years (not scaled for distance)</text>'
    )
    plot = "\n    ".join(parts)
    return figure_svg(
        w,
        plot_h,
        "2",
        "Three trade lanes",
        "Regional furniture-timber trade milestones on parallel lanes.",
        plot,
        "Baltic oak, Caribbean mahogany, and Indian Ocean teak followed distinct supply chains before twentieth-century conservation law.",
        "Milestone years follow draft bibliographies; 1992 Swietenia listing per cites.org.",
    )


def grain_orientation() -> str:
    w, plot_h = 900, 400
    cx, cy, r = 200, 210, 78
    parts: list[str] = []
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{INK}" stroke-width="1.25"/>')
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r * 0.32}" fill="none" stroke="{INK}" stroke-width="0.75"/>')
    # flatsawn tangential
    parts.append(
        f'<line x1="{cx - r}" y1="{cy}" x2="{cx + r}" y2="{cy}" stroke="{INK}" stroke-width="1.5" stroke-dasharray="7 5"/>'
    )
    parts.append(
        f'<text x="{cx}" y="{cy - r - 14}" text-anchor="middle" font-family="{FONT_SANS}" font-size="11" fill="{INK}">Flatsawn (tangential)</text>'
    )
    # quartersawn radial
    parts.append(f'<line x1="{cx}" y1="{cy - r}" x2="{cx}" y2="{cy + r}" stroke="{INK}" stroke-width="1.5"/>')
    parts.append(
        f'<text x="{cx + r + 12}" y="{cy + 4}" font-family="{FONT_SANS}" font-size="11" fill="{INK}">Quartersawn (radial)</text>'
    )
    ang = math.radians(52)
    dx, dy = math.cos(ang) * r, math.sin(ang) * r
    parts.append(
        f'<line x1="{cx - dx}" y1="{cy - dy}" x2="{cx + dx}" y2="{cy + dy}" '
        f'stroke="{MUTED}" stroke-width="1.25" stroke-dasharray="2 4"/>'
    )
    parts.append(
        f'<text x="48" y="{cy + r + 36}" font-family="{FONT_SANS}" font-size="11" fill="{MUTED}">Rift cut (~30–60° to ray)</text>'
    )
    panels = [
        ("Flatsawn face", "cathedral", 400),
        ("Quartersawn face", "straight", 545),
        ("Rift face", "bias", 690),
    ]
    for label, kind, px in panels:
        parts.append(f'<rect x="{px}" y="120" width="110" height="110" fill="{PAPER}" stroke="{INK}" stroke-width="0.75"/>')
        if kind == "cathedral":
            for i in range(5):
                parts.append(
                    f'<path d="M{px + 12} {150 + i * 16} Q{px + 55} {142 + i * 16} {px + 98} {150 + i * 16}" '
                    f'fill="none" stroke="{INK}" stroke-width="0.9" opacity="0.85"/>'
                )
        elif kind == "straight":
            for i in range(7):
                parts.append(
                    f'<line x1="{px + 10}" y1="{128 + i * 14}" x2="{px + 100}" y2="{128 + i * 14}" '
                    f'stroke="{INK}" stroke-width="0.7" opacity="0.8"/>'
                )
        else:
            for i in range(9):
                parts.append(
                    f'<line x1="{px + 14 + i * 9}" y1="125" x2="{px + 24 + i * 9}" y2="225" '
                    f'stroke="{INK}" stroke-width="0.65" opacity="0.75"/>'
                )
        parts.append(
            f'<text x="{px + 55}" y="248" text-anchor="middle" font-family="{FONT_SANS}" font-size="10" fill="{INK}">{esc(label)}</text>'
        )
    parts.append(
        f'<text x="400" y="100" font-family="{FONT_SANS}" font-size="11" fill="{MUTED}">Face grain resulting from cut</text>'
    )
    plot = "\n    ".join(parts)
    return figure_svg(
        w,
        plot_h,
        "3",
        "How a log is sawn",
        "Log cross-section with cut directions and resulting face-grain patterns.",
        plot,
        "Tangential flatsawn boards show cathedral figure; radial quartersawn shows linear ray fleck; rift sits between the two.",
        "Geometry after R. B. Hoadley, Understanding Wood (Taunton).",
    )


def species_scatter() -> str:
    w, plot_h = 900, 420
    ml, mr, mt, mb = 90, 48, 100, 72
    cw = w - ml - mr
    ch = plot_h - mt - mb
    j_max, d_max = 3200, 1100
    parts: list[str] = []
    parts.append(f'<rect x="{ml}" y="{mt}" width="{cw}" height="{ch}" fill="{PAPER}" stroke="{RULE}" stroke-width="1"/>')
    for tick in (0, 800, 1600, 2400, 3200):
        x = ml + tick / j_max * cw
        parts.append(f'<line x1="{x}" y1="{mt}" x2="{x}" y2="{mt + ch}" stroke="{RULE}" stroke-width="0.5"/>')
        parts.append(
            f'<text x="{x}" y="{mt + ch + 18}" text-anchor="middle" font-family="{FONT_SANS}" font-size="9" fill="{MUTED}">{tick}</text>'
        )
    for tick in (350, 550, 750, 950):
        y = mt + ch - (tick / d_max) * ch
        parts.append(f'<line x1="{ml}" y1="{y}" x2="{ml + cw}" y2="{y}" stroke="{RULE}" stroke-width="0.5"/>')
        parts.append(
            f'<text x="{ml - 10}" y="{y + 3}" text-anchor="end" font-family="{FONT_SANS}" font-size="9" fill="{MUTED}">{tick}</text>'
        )
    parts.append(
        f'<text x="{ml + cw / 2}" y="{plot_h - 28}" text-anchor="middle" font-family="{FONT_SANS}" font-size="11" fill="{INK}">Janka side hardness (lbf)</text>'
    )
    parts.append(
        f'<text x="28" y="{mt + ch / 2}" text-anchor="middle" font-family="{FONT_SANS}" font-size="11" fill="{INK}" transform="rotate(-90 28 {mt + ch / 2})">Oven-dry density (kg/m³)</text>'
    )
    for name, sci, janka, dens in CORE_SPECIES:
        x = ml + janka / j_max * cw
        y = mt + ch - dens / d_max * ch
        parts.append(f'<circle cx="{x}" cy="{y}" r="5" fill="{INK}" opacity="0.9"/>')
        parts.append(
            f'<text x="{x + 8}" y="{y - 6}" font-family="{FONT_SANS}" font-size="10" font-weight="600" fill="{INK}">{esc(name)}</text>'
        )
        parts.append(
            f'<text x="{x + 8}" y="{y + 8}" font-family="{FONT_SERIF}" font-size="9" font-style="italic" fill="{MUTED}">{esc(sci)}</text>'
        )
    plot = "\n    ".join(parts)
    return figure_svg(
        w,
        plot_h,
        "4",
        "Core furniture species — hardness and weight",
        "Scatter plot of Janka hardness versus oven-dry density for ten historical species.",
        plot,
        "Harder, denser species (upper right) demand sharper tooling; softwoods cluster lower left.",
        "Janka & density means: USDA FPL Wood Handbook; Wood Database cross-check.",
    )


def cites_map() -> str:
    w, plot_h = 900, 400
    # Simplified continental outlines (schematic, not navigation grade)
    land = f"""
    <path d="M120 140 L200 110 L240 150 L220 220 L150 240 L110 190 Z" fill="{RULE}" stroke="{INK}" stroke-width="0.75"/>
    <path d="M170 250 L230 230 L260 300 L210 330 L150 310 Z" fill="{RULE}" stroke="{INK}" stroke-width="0.75"/>
    <path d="M400 120 L470 110 L500 150 L480 200 L420 210 L390 160 Z" fill="{RULE}" stroke="{INK}" stroke-width="0.75"/>
    <path d="M420 220 L520 210 L540 290 L460 310 L400 270 Z" fill="{RULE}" stroke="{INK}" stroke-width="0.75"/>
    <path d="M560 130 L700 120 L740 200 L680 260 L580 240 L550 180 Z" fill="{RULE}" stroke="{INK}" stroke-width="0.75"/>
    <path d="M620 280 L700 270 L720 320 L650 340 Z" fill="{RULE}" stroke="{INK}" stroke-width="0.75"/>
    """
    highlights = """
    <path d="M170 250 L230 230 L260 300 L210 330 L150 310 Z" fill="#57534e" opacity="0.18"/>
    <path d="M420 220 L520 210 L540 290 L460 310 L400 270 Z" fill="#57534e" opacity="0.22"/>
    <path d="M560 130 L700 120 L740 200 L680 260 L580 240 L550 180 Z" fill="#57534e" opacity="0.2"/>
    """
    legend = f"""
    <text x="48" y="120" font-family="{FONT_SERIF}" font-size="14" fill="{INK}">CITES touchpoints for traded furniture woods</text>
    <text x="48" y="340" font-family="{FONT_SANS}" font-size="11" fill="{INK}">• Americas — Swietenia macrophylla (App. II, 1992); Dalbergia nigra (App. I)</text>
    <text x="48" y="358" font-family="{FONT_SANS}" font-size="11" fill="{INK}">• Africa — Diospyros crassiflora (App. II); Khaya spp. (App. II)</text>
    <text x="48" y="376" font-family="{FONT_SANS}" font-size="11" fill="{INK}">• South &amp; SE Asia — Dalbergia latifolia (App. II); teak under national export controls</text>
    """
    plot = land + highlights + legend
    return figure_svg(
        w,
        plot_h,
        "5",
        "Where listing meets the trade",
        "Schematic map with CITES appendix notes for commonly traded furniture timbers.",
        plot,
        "Shaded regions show where listed tropical furniture species originate; temperate oaks and pines are generally not CITES-listed.",
        "Appendix status: cites.org (verify before publication). Map is illustrative only.",
    )


FIGURE_PATHS = {
    "timeline": "../assets/timber-trade-500y/timeline.svg",
    "lanes": "../assets/timber-trade-500y/trade-lanes.svg",
    "grain": "../assets/grain-cuts/sawn-orientation.svg",
    "species": "../assets/species-comparison/core-species-properties.svg",
    "cites": "../assets/cites-conservation/furniture-timber-listings.svg",
}

# Writer slug → figure keys (max 2 per draft)
SLUG_FIGURES: dict[str, list[str]] = {
    "intro-500-year-timber": ["timeline", "species"],
    "glossary-grain-and-cut": ["grain"],
    "baltic-oak-renaissance": ["lanes", "species"],
    "english-oak-great-furniture": ["species", "grain"],
    "dutch-golden-age-shipping": ["lanes", "timeline"],
    "navy-oak-reserves": ["lanes", "timeline"],
    "american-colonial-pine": ["species", "timeline"],
    "white-pine-softwood-economy": ["species"],
    "walnut-baroque": ["species", "grain"],
    "walnut-queen-anne": ["species", "grain"],
    "mahogany-chippendale": ["lanes", "species"],
    "mahogany-federal-america": ["lanes", "species"],
    "mahogany-regency-empire": ["lanes", "cites"],
    "rosewood-victorian": ["species", "grain"],
    "rosewood-gothic-revival": ["species", "cites"],
    "teak-colonial-dockyards": ["lanes", "species"],
    "teak-deck-and-garden": ["species", "lanes"],
    "ebony-inlay-keys": ["species", "cites"],
    "maple-birdseye-factory": ["species", "grain"],
    "cherry-shaker": ["species"],
    "yew-medieval-turnery": ["species"],
    "satinwood-adam-style": ["species", "grain"],
    "beech-bentwood-thonet": ["species"],
    "ash-sporting-chairs": ["species"],
    "cedar-lining-chests": ["species"],
    "boxwood-inlay": ["species"],
    "padauk-modernist-accents": ["species", "cites"],
    "cites-1973-convention": ["cites", "timeline"],
    "cites-dalbergia-2017": ["cites", "species"],
    "cites-swietenia-permits": ["cites", "lanes"],
    "cites-ebony-africa": ["cites", "species"],
    "sustainable-teak-plantations": ["lanes", "cites"],
    "reclaimed-oak-beams": ["species", "timeline"],
    "quartersawn-arts-crafts": ["grain", "species"],
    "flatsawn-panel-figure": ["grain"],
    "rift-cut-flooring": ["grain"],
    "moisture-wood-movement": ["grain", "species"],
    "janka-hardness-explained": ["species"],
    "density-weight-shipping": ["species", "timeline"],
    "workability-hand-tools": ["species", "grain"],
    "veneer-versus-solid": ["grain", "species"],
    "brazilian-rosewood-midcentury": ["species", "cites"],
    "indian-rosewood-exports": ["species", "timeline"],
    "plywood-and-core-stock": ["grain", "timeline"],
    "tropical-hardwood-peak-1900": ["timeline", "species"],
    "conservation-today": ["cites", "timeline"],
}

FIGURE_CAPTIONS = {
    "timeline": "Figure 1. Milestone years in the long furniture-timber trade, from Baltic oak through tropical hardwoods to CITES enforcement.",
    "lanes": "Figure 2. Three parallel supply chains — Baltic oak, Atlantic mahogany, and Indian Ocean teak — with documentary milestone years.",
    "grain": "Figure 3. Tangential, radial, and rift cuts through a log and the face-grain patterns they produce in finished boards.",
    "species": "Figure 4. Mean Janka hardness and oven-dry density for ten species that anchor this series (USDA FPL / Wood Database means).",
    "cites": "Figure 5. Illustrative origin regions for CITES-listed furniture timbers; confirm appendix status at publication time (cites.org).",
}


def write_embed(slug: str, keys: list[str]) -> None:
    lines = [
        f"<!-- staged embed for draft: {slug} -->",
        f"<!-- paste into drafts/{slug}.md when the draft is merged -->",
        "",
    ]
    for key in keys:
        path = FIGURE_PATHS[key]
        alt = FIGURE_CAPTIONS[key].split(". ", 1)[-1]
        lines.append(f"![{alt}]({path})")
        lines.append("")
        lines.append(f"*{FIGURE_CAPTIONS[key]}*")
        lines.append("")
    EMBEDS.mkdir(parents=True, exist_ok=True)
    (EMBEDS / f"{slug}.md").write_text("\n".join(lines), encoding="utf-8")


def prune_legacy_assets() -> None:
    keep = {
        ASSETS / "timber-trade-500y",
        ASSETS / "grain-cuts",
        ASSETS / "species-comparison",
        ASSETS / "cites-conservation",
    }
    if ASSETS.exists():
        for child in ASSETS.iterdir():
            if child.is_dir() and child not in keep:
                shutil.rmtree(child)
    for folder in keep:
        if folder.exists():
            for f in folder.glob("*.svg"):
                f.unlink()


def main() -> None:
    prune_legacy_assets()
    write_svg = lambda p, c: (p.parent.mkdir(parents=True, exist_ok=True), p.write_text(c, encoding="utf-8"))
    write_svg(ASSETS / "timber-trade-500y" / "timeline.svg", timeline_global())
    write_svg(ASSETS / "timber-trade-500y" / "trade-lanes.svg", timeline_lanes())
    write_svg(ASSETS / "grain-cuts" / "sawn-orientation.svg", grain_orientation())
    write_svg(ASSETS / "species-comparison" / "core-species-properties.svg", species_scatter())
    write_svg(ASSETS / "cites-conservation" / "furniture-timber-listings.svg", cites_map())

    slugs = json.loads(SLUGS_FILE.read_text(encoding="utf-8"))["draft_slugs"]
    for slug in slugs:
        keys = SLUG_FIGURES.get(slug, ["species"])
        write_embed(slug, keys)
    print("Wrote 5 SVG figures and", len(slugs), "staged embeds")


if __name__ == "__main__":
    main()
