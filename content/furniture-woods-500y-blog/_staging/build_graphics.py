#!/usr/bin/env python3
"""Generate staged SVG figures for furniture-woods-500y-blog. Run from repo root."""
from __future__ import annotations

import html
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"

# Janka (lbf) and oven-dry density (kg/m³) — USDA Forest Products Lab / Wood Database summaries.
SPECIES = [
    ("European oak", "Quercus petraea/robur", 1120, 680, "#8B6914"),
    ("White oak", "Quercus alba", 1360, 755, "#A67C00"),
    ("Honduran mahogany", "Swietenia macrophylla", 900, 640, "#8B4513"),
    ("Black walnut", "Juglans nigra", 1010, 610, "#5C4033"),
    ("Teak", "Tectona grandis", 1155, 655, "#C4A35A"),
    ("Indian rosewood", "Dalbergia latifolia", 2440, 850, "#4A2C2A"),
    ("Brazilian rosewood", "Dalbergia nigra", 2790, 865, "#3D2317"),
    ("Gabon ebony", "Diospyros crassiflora", 3220, 1080, "#1a1a1a"),
    ("Hard maple", "Acer saccharum", 1450, 705, "#E8D4A8"),
    ("Black cherry", "Prunus serotina", 950, 560, "#A0522D"),
    ("Eastern white pine", "Pinus strobus", 380, 350, "#DEB887"),
    ("Yew", "Taxus baccata", 1500, 670, "#6B4423"),
    ("Ceylon satinwood", "Chloroxylon swietenia", 2270, 820, "#E6C87A"),
    ("European beech", "Fagus sylvatica", 1450, 720, "#D2B48C"),
    ("White ash", "Fraxinus americana", 1320, 680, "#C9A66B"),
    ("Atlas cedar", "Cedrus atlantica", 900, 560, "#B8860B"),
    ("Boxwood", "Buxus sempervirens", 3840, 915, "#D4AF37"),
    ("African padauk", "Pterocarpus soyauxii", 1970, 745, "#8B0000"),
]

TIMELINE_EVENTS = [
    (1526, "Baltic oak\nexport hubs"),
    (1607, "Jamestown:\ncolonial timber"),
    (1720, "Caribbean\nmahogany trade"),
    (1830, "Victorian\nrosewood boom"),
    (1856, "Burma teak\nrail & ships"),
    (1900, "Tropical\nhardwood peak"),
    (1973, "CITES\nConvention"),
    (1992, "Swietenia spp.\nAppendix II"),
    (2017, "Dalbergia spp.\nAppendix II"),
    (2026, "Trade under\npermits & COC"),
]

CITES_REGIONS = [
    ("Americas", "Swietenia macrophylla (App. II, 1992+); Dalbergia nigra (App. I)"),
    ("West & Central Africa", "Diospyros crassiflora (App. II); Khaya spp. (App. II)"),
    ("South & SE Asia", "Tectona grandis (national controls); D. latifolia (App. II)"),
    ("Europe", "Most temperate furniture species: not CITES-listed"),
]


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def svg_wrap(
    width: int,
    height: int,
    body: str,
    title: str,
    desc: str,
    note: str,
) -> str:
    cap_h = 72
    total_h = height + cap_h
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {total_h}" width="{width}" height="{total_h}" role="img" aria-labelledby="title desc">
  <title id="title">{esc(title)}</title>
  <desc id="desc">{esc(desc)}</desc>
  <rect width="100%" height="{height}" fill="#faf8f5"/>
  {body}
  <rect y="{height}" width="100%" height="{cap_h}" fill="#f0ebe3"/>
  <text x="16" y="{height + 22}" font-family="system-ui,Segoe UI,sans-serif" font-size="13" font-weight="600" fill="#2c2416">{esc(title)}</text>
  <text x="16" y="{height + 42}" font-family="system-ui,Segoe UI,sans-serif" font-size="11" fill="#5a5045">{esc(note)}</text>
</svg>
"""


def write_svg(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def bar_chart_janka() -> str:
    w, h = 720, 420
    margin_l, margin_t, margin_b = 140, 40, 50
    chart_w = w - margin_l - 40
    chart_h = h - margin_t - margin_b
    max_j = max(s[2] for s in SPECIES)
    bars = []
    row_h = chart_h / len(SPECIES)
    for i, (name, sci, janka, _dens, color) in enumerate(SPECIES):
        y = margin_t + i * row_h + row_h * 0.15
        bh = row_h * 0.7
        bw = (janka / max_j) * chart_w
        bars.append(
            f'<text x="{margin_l - 8}" y="{y + bh/2 + 4}" text-anchor="end" '
            f'font-size="11" fill="#333">{esc(name)}</text>'
        )
        bars.append(
            f'<rect x="{margin_l}" y="{y}" width="{bw:.1f}" height="{bh:.1f}" fill="{color}" rx="2"/>'
        )
        bars.append(
            f'<text x="{margin_l + bw + 6}" y="{y + bh/2 + 4}" font-size="10" fill="#444">{janka} lbf</text>'
        )
    axis = (
        f'<line x1="{margin_l}" y1="{margin_t + chart_h}" x2="{margin_l + chart_w}" '
        f'y2="{margin_t + chart_h}" stroke="#999"/>'
        f'<text x="{margin_l + chart_w/2}" y="{h - 8}" text-anchor="middle" font-size="11" fill="#555">'
        f"Janka side hardness (lbf)</text>"
    )
    body = "\n  ".join(bars + [axis])
    note = (
        "Source: USDA Forest Products Lab Wood Handbook & The Wood Database summaries (approx. oven-dry)."
    )
    return svg_wrap(
        w,
        h,
        body,
        "Furniture species — Janka hardness comparison",
        "Horizontal bar chart of side hardness for common historical furniture woods.",
        note,
    )


def bar_chart_density() -> str:
    w, h = 720, 420
    margin_l, margin_t, margin_b = 140, 40, 50
    chart_w = w - margin_l - 40
    chart_h = h - margin_t - margin_b
    max_d = max(s[3] for s in SPECIES)
    bars = []
    row_h = chart_h / len(SPECIES)
    for i, (name, _sci, _j, dens, color) in enumerate(SPECIES):
        y = margin_t + i * row_h + row_h * 0.15
        bh = row_h * 0.7
        bw = (dens / max_d) * chart_w
        bars.append(
            f'<text x="{margin_l - 8}" y="{y + bh/2 + 4}" text-anchor="end" '
            f'font-size="11" fill="#333">{esc(name)}</text>'
        )
        bars.append(f'<rect x="{margin_l}" y="{y}" width="{bw:.1f}" height="{bh:.1f}" fill="{color}" rx="2"/>')
        bars.append(
            f'<text x="{margin_l + bw + 6}" y="{y + bh/2 + 4}" font-size="10" fill="#444">{dens} kg/m³</text>'
        )
    axis = (
        f'<text x="{margin_l + chart_w/2}" y="{h - 8}" text-anchor="middle" font-size="11" fill="#555">'
        f"Oven-dry density (kg/m³)</text>"
    )
    body = "\n  ".join(bars + [axis])
    note = "Source: USDA FPL Wood Handbook, Ch. 5 property summaries (species means)."
    return svg_wrap(
        w,
        h,
        body,
        "Furniture species — oven-dry density",
        "Bar chart comparing mean oven-dry density.",
        note,
    )


def timeline_global() -> str:
    w, h = 800, 280
    y0 = 120
    x0, x1 = 60, 740
    span = x1 - x0
    t_min, t_max = 1520, 2030
    lines = [
        f'<line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y0}" stroke="#5a5045" stroke-width="3"/>',
        f'<text x="{x0}" y="{y0 + 28}" font-size="11" fill="#555">{t_min}</text>',
        f'<text x="{x1}" y="{y0 + 28}" text-anchor="end" font-size="11" fill="#555">{t_max}</text>',
    ]
    for year, label in TIMELINE_EVENTS:
        frac = (year - t_min) / (t_max - t_min)
        x = x0 + frac * span
        lines.append(f'<line x1="{x}" y1="{y0 - 8}" x2="{x}" y2="{y0 + 8}" stroke="#8B4513" stroke-width="2"/>')
        lines.append(f'<circle cx="{x}" cy="{y0}" r="5" fill="#8B4513"/>')
        ly = y0 - 24 if year % 2 == 0 else y0 + 36
        for j, part in enumerate(label.split("\n")):
            lines.append(
                f'<text x="{x}" y="{ly + j * 13}" text-anchor="middle" font-size="10" fill="#2c2416">{esc(part)}</text>'
            )
        lines.append(
            f'<text x="{x}" y="{y0 - 38 if year % 2 == 0 else y0 + 58}" text-anchor="middle" '
            f'font-size="9" fill="#777">{year}</text>'
        )
    body = "\n  ".join(lines)
    note = (
        "Milestone years are illustrative trade/policy markers; CITES: cites.org (Conv. 1973, "
        "appendix listings as noted)."
    )
    return svg_wrap(
        w,
        h,
        body,
        "500-year furniture timber trade — selected milestones",
        "Timeline from early modern Baltic oak exports to CITES-listed tropical trade.",
        note,
    )


def grain_cuts_diagram() -> str:
    w, h = 720, 360
    log_cx, log_cy, log_r = 200, 180, 70
    parts = [
        f'<circle cx="{log_cx}" cy="{log_cy}" r="{log_r}" fill="#D4A574" stroke="#8B6914" stroke-width="2"/>',
        f'<circle cx="{log_cx}" cy="{log_cy}" r="{log_r * 0.35}" fill="#f5e6d3" stroke="#8B6914"/>',
        f'<line x1="{log_cx - log_r}" y1="{log_cy}" x2="{log_cx + log_r}" y2="{log_cy}" stroke="#c0392b" stroke-width="2" stroke-dasharray="6 4"/>',
        f'<text x="{log_cx}" y="{log_cy - log_r - 12}" text-anchor="middle" font-size="12" fill="#c0392b">Flatsawn — tangential</text>',
        f'<line x1="{log_cx}" y1="{log_cy - log_r}" x2="{log_cx}" y2="{log_cy + log_r}" stroke="#2980b9" stroke-width="2"/>',
        f'<text x="{log_cx + log_r + 8}" y="{log_cy}" font-size="12" fill="#2980b9">Quartersawn — radial</text>',
    ]
    ang = 0.785
    dx = math.cos(ang) * log_r
    dy = math.sin(ang) * log_r
    parts.append(
        f'<line x1="{log_cx - dx}" y1="{log_cy - dy}" x2="{log_cx + dx}" y2="{log_cy + dy}" '
        f'stroke="#27ae60" stroke-width="2" stroke-dasharray="3 3"/>'
    )
    parts.append(
        f'<text x="{log_cx - log_r - 10}" y="{log_cy + log_r + 20}" text-anchor="end" '
        f'font-size="12" fill="#27ae60">Riftsawn (~30–60° to ray)</text>'
    )
    # end-grain panels
    px = 420
    for i, (label, pattern, col) in enumerate(
        [
            ("Flatsawn face", "arc", "#c0392b"),
            ("Quartersawn face", "lines", "#2980b9"),
            ("Riftsawn face", "diag", "#27ae60"),
        ]
    ):
        x = px + i * 95
        parts.append(f'<rect x="{x}" y="80" width="80" height="80" fill="#e8dcc8" stroke="#666"/>')
        if pattern == "arc":
            for a in range(4):
                parts.append(
                    f'<path d="M{x+10} {120+a*15} Q{x+40} {115+a*15} {x+70} {120+a*15}" '
                    f'fill="none" stroke="{col}" stroke-width="1.5"/>'
                )
        elif pattern == "lines":
            for a in range(6):
                parts.append(
                    f'<line x1="{x+8}" y1="{85+a*13}" x2="{x+72}" y2="{85+a*13}" stroke="{col}" stroke-width="1"/>'
                )
        else:
            for a in range(8):
                parts.append(
                    f'<line x1="{x+10+a*8}" y1="85" x2="{x+20+a*8}" y2="165" stroke="{col}" stroke-width="1"/>'
                )
        parts.append(
            f'<text x="{x + 40}" y="175" text-anchor="middle" font-size="10" fill="#333">{esc(label)}</text>'
        )
    parts.append(
        f'<text x="360" y="40" font-size="13" font-weight="600" fill="#2c2416">Log orientation → typical face grain</text>'
    )
    body = "\n  ".join(parts)
    note = "Diagram after standard woodworking texts (Hoadley, Understanding Wood); angles approximate."
    return svg_wrap(
        w,
        h,
        body,
        "Quartersawn, flatsawn, and riftsawn — log to face",
        "Schematic log cross-section with cut directions and resulting grain patterns.",
        note,
    )


def cites_map() -> str:
    w, h = 760, 400
    # Simplified world blocks (not geographic GIS — schematic regions)
    regions = [
        (80, 100, 220, 140, "#6B8E23", "North America"),
        (80, 260, 220, 80, "#CD853F", "South America"),
        (320, 80, 180, 100, "#4682B4", "Europe"),
        (320, 200, 200, 120, "#DAA520", "Africa"),
        (540, 120, 180, 100, "#2E8B57", "S & SE Asia"),
        (540, 240, 160, 90, "#8FBC8F", "Oceania"),
    ]
    parts = []
    for x, y, rw, rh, fill, name in regions:
        parts.append(f'<rect x="{x}" y="{y}" width="{rw}" height="{rh}" fill="{fill}" opacity="0.55" rx="4"/>')
        parts.append(
            f'<text x="{x + rw/2}" y="{y + rh/2}" text-anchor="middle" font-size="12" fill="#1a1a1a">{esc(name)}</text>'
        )
    y_note = 20
    for region, detail in CITES_REGIONS:
        parts.append(
            f'<text x="24" y="{y_note}" font-size="11" fill="#333"><tspan font-weight="600">{esc(region)}:</tspan> {esc(detail)}</text>'
        )
        y_note += 18
    body = "\n  ".join(parts)
    note = "Schematic regions only. Listing status: cites.org Appendices (checked 2024–2025 summaries)."
    return svg_wrap(
        w,
        h,
        body,
        "CITES & conservation — regional listing overview (schematic)",
        "Simplified map blocks with appendix notes for trade-relevant furniture species.",
        note,
    )


def species_profile(slug: str, name: str, sci: str, janka: int, dens: int, color: str, era: str) -> str:
    w, h = 480, 300
    max_j = 3500
    max_d = 1200
    jw = (janka / max_j) * 280
    dw = (dens / max_d) * 280
    body = f"""
  <text x="24" y="36" font-size="16" font-weight="600" fill="#2c2416">{esc(name)}</text>
  <text x="24" y="54" font-size="11" font-style="italic" fill="#555">{esc(sci)}</text>
  <text x="24" y="78" font-size="11" fill="#444">Peak furniture-trade era: {esc(era)}</text>
  <text x="24" y="110" font-size="11" fill="#333">Janka hardness</text>
  <rect x="24" y="118" width="280" height="18" fill="#e8e0d5" rx="2"/>
  <rect x="24" y="118" width="{jw:.0f}" height="18" fill="{color}" rx="2"/>
  <text x="310" y="132" font-size="10" fill="#444">{janka} lbf</text>
  <text x="24" y="168" font-size="11" fill="#333">Oven-dry density</text>
  <rect x="24" y="176" width="280" height="18" fill="#e8e0d5" rx="2"/>
  <rect x="24" y="176" width="{dw:.0f}" height="18" fill="{color}" opacity="0.85" rx="2"/>
  <text x="310" y="190" font-size="10" fill="#444">{dens} kg/m³</text>
"""
    note = "Property means: USDA FPL Wood Handbook / Wood Database. Trade era from historical furniture literature."
    return svg_wrap(w, h, body, f"{name} — species profile", f"Comparison bars for {name}.", note)


def trade_route_mini(slug: str, title: str, points: list[tuple[str, int]]) -> str:
    w, h = 640, 220
    x0, x1 = 50, 590
    y0 = 100
    span = x1 - x0
    t_min = min(p[1] for p in points)
    t_max = max(p[1] for p in points)
    lines = [
        f'<line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y0}" stroke="#5a5045" stroke-width="2"/>',
        f'<text x="24" y="32" font-size="14" font-weight="600" fill="#2c2416">{esc(title)}</text>',
    ]
    for label, year in points:
        frac = (year - t_min) / (t_max - t_min) if t_max > t_min else 0.5
        x = x0 + frac * span
        lines.append(f'<circle cx="{x}" cy="{y0}" r="4" fill="#8B4513"/>')
        lines.append(
            f'<text x="{x}" y="{y0 - 12}" text-anchor="middle" font-size="9" fill="#333">{esc(label)}</text>'
        )
        lines.append(
            f'<text x="{x}" y="{y0 + 20}" text-anchor="middle" font-size="9" fill="#777">{year}</text>'
        )
    body = "\n  ".join(lines)
    note = "Dates are order-of-magnitude trade milestones; see draft bibliography for primary sources."
    return svg_wrap(w, h, body, title, f"Regional trade timeline for {slug}.", note)


SPECIES_SLUGS = [
    ("species-oak-european", "European oak", "Quercus petraea/robur", 1120, 680, "#8B6914", "16th–19th c. Baltic & English"),
    ("species-oak-white", "White oak", "Quercus alba", 1360, 755, "#A67C00", "18th–20th c. American furniture"),
    ("species-mahogany-honduran", "Honduran mahogany", "Swietenia macrophylla", 900, 640, "#8B4513", "1720s–20th c. Atlantic trade"),
    ("species-walnut-black", "Black walnut", "Juglans nigra", 1010, 610, "#5C4033", "1680s–19th c. American & EU"),
    ("species-teak", "Teak", "Tectona grandis", 1155, 655, "#C4A35A", "19th–20th c. colonial & marine"),
    ("species-rosewood-indian", "Indian rosewood", "Dalbergia latifolia", 2440, 850, "#4A2C2A", "19th c. Victorian veneer"),
    ("species-rosewood-brazilian", "Brazilian rosewood", "Dalbergia nigra", 2790, 865, "#3D2317", "19th–20th c. luxury cabinetwork"),
    ("species-ebony-gabon", "Gabon ebony", "Diospyros crassiflora", 3220, 1080, "#1a1a1a", "18th–20th c. inlay & keys"),
    ("species-maple-hard", "Hard maple", "Acer saccharum", 1450, 705, "#E8D4A8", "19th–20th c. American factory"),
    ("species-cherry-black", "Black cherry", "Prunus serotina", 950, 560, "#A0522D", "18th–20th c. American"),
    ("species-pine-eastern-white", "Eastern white pine", "Pinus strobus", 380, 350, "#DEB887", "17th–19th c. colonial trim"),
    ("species-yew", "Yew", "Taxus baccata", 1500, 670, "#6B4423", "Medieval–18th c. turnery & veneer"),
    ("species-satinwood", "Ceylon satinwood", "Chloroxylon swietenia", 2270, 820, "#E6C87A", "Late 18th c. Neoclassical"),
    ("species-beech", "European beech", "Fagus sylvatica", 1450, 720, "#D2B48C", "19th–20th c. bentwood & frames"),
    ("species-ash-white", "White ash", "Fraxinus americana", 1320, 680, "#C9A66B", "19th–20th c. sporting & chairs"),
    ("species-cedar-atlas", "Atlas cedar", "Cedrus atlantica", 900, 560, "#B8860B", "18th–19th c. lining & chests"),
    ("species-boxwood", "Boxwood", "Buxus sempervirens", 3840, 915, "#D4AF37", "Inlay & turnery (small stock)"),
    ("species-padauk", "African padauk", "Pterocarpus soyauxii", 1970, 745, "#8B0000", "20th c. modernist accents"),
]

TRADE_MINIS = {
    "timber-trade-baltic-oak": (
        "Baltic oak export chain",
        [
            ("Riga market", 1580),
            ("Dutch shipping", 1650),
            ("Royal Navy stores", 1750),
            ("Rail + local oak", 1880),
        ],
    ),
    "timber-trade-mahogany-atlantic": (
        "Caribbean mahogany to London & Boston",
        [
            ("Jamaica exports", 1725),
            ("Chippendale peak", 1760),
            ("Cuba trade", 1820),
            ("CITES Swietenia", 1992),
        ],
    ),
    "timber-trade-teak-asia": (
        "Burma/India teak in empire trade",
        [
            ("Bombay dockyards", 1840),
            ("Irrawaddy float", 1870),
            ("Colonial reserves", 1920),
            ("Myanmar controls", 2014),
        ],
    ),
}


def stability_chart() -> str:
    """Relative ranking schematic (1=most stable) — literature consensus order, not measured per batch."""
    w, h = 620, 340
    ranked = [
        ("Teak", 1),
        ("Mahogany", 2),
        ("White oak", 3),
        ("Walnut", 4),
        ("Cherry", 5),
        ("Maple", 6),
        ("Rosewood", 7),
        ("Pine", 8),
    ]
    parts = []
    for i, (name, rank) in enumerate(ranked):
        y = 50 + i * 32
        bar_w = (9 - rank) / 8 * 400
        parts.append(f'<text x="24" y="{y + 14}" font-size="11" fill="#333">{esc(name)}</text>')
        parts.append(f'<rect x="120" y="{y}" width="{bar_w:.0f}" height="20" fill="#7d9a6a" rx="2"/>')
        parts.append(f'<text x="{130 + bar_w}" y="{y + 14}" font-size="10" fill="#555">rank {rank}/8</text>')
    body = "\n  ".join(parts)
    note = (
        "Qualitative stability ranking for indoor furniture (movement vs humidity); "
        "Hoadley (Understanding Wood) & FPL species guides — not site-specific EMC data."
    )
    return svg_wrap(
        w,
        h,
        body,
        "Dimensional stability — qualitative ranking (indoor furniture)",
        "Lower rank number indicates relatively smaller seasonal movement in typical use.",
        note,
    )


def cites_swietenia_detail() -> str:
    w, h = 700, 320
    body = """
  <text x="24" y="36" font-size="14" font-weight="600" fill="#2c2416">Swietenia spp. — CITES listing snapshot</text>
  <rect x="24" y="56" width="652" height="56" fill="#f5e8d0" stroke="#8B4513" rx="4"/>
  <text x="36" y="78" font-size="11" fill="#333">Appendix II (1992): S. macrophylla — international commercial trade requires permits.</text>
  <text x="36" y="96" font-size="11" fill="#333">Appendix I: S. mahagoni, S. humilis — stricter controls (range-limited native populations).</text>
  <rect x="24" y="130" width="300" height="120" fill="#6B8E23" opacity="0.5" rx="4"/>
  <text x="174" y="195" text-anchor="middle" font-size="12" fill="#1a1a1a">Neotropics (native range)</text>
  <rect x="360" y="130" width="316" height="56" fill="#4682B4" opacity="0.4" rx="4"/>
  <text x="518" y="162" text-anchor="middle" font-size="11" fill="#333">Historic import markets: UK, US, EU workshops</text>
  <text x="24" y="270" font-size="11" fill="#555">Use plantation-grown or documented pre-Convention stock where legally available.</text>
"""
    note = "Listing summary: cites.org species database (Swietenia); effective dates per COP decisions."
    return svg_wrap(w, h, body, "Honduran & related mahoganies — CITES schematic", "Trade control overview.", note)


def cites_dalbergia_detail() -> str:
    w, h = 700, 320
    body = """
  <text x="24" y="36" font-size="14" font-weight="600" fill="#2c2416">Dalbergia spp. — post-2017 Appendix II breadth</text>
  <text x="24" y="60" font-size="11" fill="#444">COP17 (2016, effective 2017): most Dalbergia spp. listed on Appendix II incl. D. nigra harmonization.</text>
  <rect x="24" y="80" width="200" height="100" fill="#8B4513" opacity="0.55" rx="4"/>
  <text x="124" y="135" text-anchor="middle" font-size="11" fill="#fff">Americas</text>
  <rect x="240" y="80" width="200" height="100" fill="#DAA520" opacity="0.55" rx="4"/>
  <text x="340" y="135" text-anchor="middle" font-size="11" fill="#1a1a1a">Africa (padauk relatives)</text>
  <rect x="456" y="80" width="220" height="100" fill="#2E8B57" opacity="0.55" rx="4"/>
  <text x="566" y="135" text-anchor="middle" font-size="11" fill="#fff">South &amp; SE Asia</text>
  <text x="24" y="210" font-size="11" fill="#333">Musical instruments, veneer, and furniture parts: export/import permits + CITES documentation chain.</text>
"""
    note = "CITES Notification 2017/003; cites.org Dalbergia annotations — verify current party measures."
    return svg_wrap(w, h, body, "Rosewoods & padauk relatives — CITES regions", "Regional schematic for Appendix II Dalbergia.", note)


def veneer_slicing_diagram() -> str:
    w, h = 680, 300
    body = """
  <text x="24" y="32" font-size="13" font-weight="600" fill="#2c2416">Veneer slicing from a flitch (schematic)</text>
  <rect x="80" y="60" width="120" height="160" fill="#C4A574" stroke="#666"/>
  <line x1="80" y1="100" x2="200" y2="100" stroke="#c0392b" stroke-width="1.5"/>
  <line x1="80" y1="140" x2="200" y2="140" stroke="#c0392b" stroke-width="1.5"/>
  <line x1="80" y1="180" x2="200" y2="180" stroke="#c0392b" stroke-width="1.5"/>
  <text x="140" y="240" text-anchor="middle" font-size="11" fill="#333">Flitch / cant</text>
  <path d="M220 140 L280 100 L280 180 L220 140" fill="none" stroke="#2980b9" stroke-width="2"/>
  <text x="300" y="110" font-size="11" fill="#2980b9">Knife path — rotary or flat slice</text>
  <rect x="400" y="90" width="240" height="12" fill="#e8dcc8" stroke="#8B6914"/>
  <rect x="400" y="110" width="240" height="12" fill="#e8dcc8" stroke="#8B6914"/>
  <rect x="400" y="130" width="240" height="12" fill="#e8dcc8" stroke="#8B6914"/>
  <text x="520" y="165" text-anchor="middle" font-size="11" fill="#333">Veneer leaves (0.6–1.0 mm typical)</text>
"""
    note = "Thickness range: ANSI/HPVA HP-1 nominal; process after Hoadley &amp; veneer industry practice guides."
    return svg_wrap(w, h, body, "Veneer slicing — flitch to leaves", "Side view of sequential veneer cuts.", note)


def workability_chart() -> str:
    w, h = 620, 340
    scores = [
        ("Eastern white pine", 9),
        ("Mahogany", 8),
        ("Black walnut", 8),
        ("Cherry", 7),
        ("Hard maple", 6),
        ("White oak", 5),
        ("Indian rosewood", 4),
        ("Gabon ebony", 3),
    ]
    parts = []
    for i, (name, score) in enumerate(scores):
        y = 50 + i * 32
        bar_w = score / 10 * 400
        parts.append(f'<text x="24" y="{y + 14}" font-size="11" fill="#333">{esc(name)}</text>')
        parts.append(f'<rect x="160" y="{y}" width="{bar_w:.0f}" height="20" fill="#b8956a" rx="2"/>')
        parts.append(f'<text x="{170 + bar_w}" y="{y + 14}" font-size="10" fill="#555">{score}/10</text>')
    body = "\n  ".join(parts)
    note = "Subjective hand-tool & machine workability index for narrative comparison; shop practice varies by figure."
    return svg_wrap(w, h, body, "Workability index (hand & machine)", "Higher score = easier typical processing.", note)


def main() -> None:
    write_svg(ASSETS / "species-comparison" / "janka-hardwoods.svg", bar_chart_janka())
    write_svg(ASSETS / "species-comparison" / "density-oven-dry.svg", bar_chart_density())
    write_svg(ASSETS / "species-comparison" / "dimensional-stability-ranking.svg", stability_chart())
    write_svg(ASSETS / "species-comparison" / "workability-index.svg", workability_chart())
    write_svg(ASSETS / "timber-trade-500y" / "timeline-global.svg", timeline_global())
    for slug, (title, pts) in TRADE_MINIS.items():
        write_svg(ASSETS / slug / "trade-milestones.svg", trade_route_mini(slug, title, pts))
    write_svg(ASSETS / "grain-cuts" / "quartersawn-flatsawn-rift.svg", grain_cuts_diagram())
    write_svg(ASSETS / "grain-cuts" / "veneer-slicing-flitch.svg", veneer_slicing_diagram())
    write_svg(ASSETS / "cites-conservation" / "regional-appendix-overview.svg", cites_map())
    write_svg(ASSETS / "cites-conservation" / "swietenia-cites-detail.svg", cites_swietenia_detail())
    write_svg(ASSETS / "cites-conservation" / "dalbergia-cites-detail.svg", cites_dalbergia_detail())
    for slug, name, sci, j, d, col, era in SPECIES_SLUGS:
        write_svg(ASSETS / slug / "species-profile.svg", species_profile(slug, name, sci, j, d, col, era))
    print(f"Wrote assets under {ASSETS}")


if __name__ == "__main__":
    main()
