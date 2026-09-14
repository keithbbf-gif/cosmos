#!/usr/bin/env python3
"""Shop-paper SVG plates for the millwork-molding-history pack."""

from __future__ import annotations

import html
from pathlib import Path

from pack_data import ARTICLES, PACK

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"

PAPER = "#f4efe6"
INK = "#2c2416"
MUTED = "#6b5a45"
RULE = "#c4b49a"
OCHRE = "#8b5a2b"
CREAM = "#efe6d4"
WHITE = "#fffaf0"


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def header(title: str, sub: str, w: int = 760, h: int = 460) -> list[str]:
    return [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc">',
        f'  <title id="title">{esc(title)}</title>',
        f'  <desc id="desc">{esc(sub)}</desc>',
        f'  <rect width="100%" height="100%" fill="{PAPER}"/>',
        f'  <text x="24" y="36" font-family="Source Serif 4, Georgia, serif" font-size="20" font-weight="600" fill="{INK}">{esc(title[:78])}</text>',
        f'  <text x="24" y="58" font-family="IBM Plex Sans, system-ui, sans-serif" font-size="12" fill="{MUTED}">{esc(sub)}</text>',
    ]


def footer(h: int = 460) -> str:
    return (
        f'  <text x="24" y="{h - 14}" font-family="IBM Plex Sans, system-ui, sans-serif" '
        f'font-size="11" fill="{MUTED}">Illustrative shop plate — not a grind template. BBF millwork lane, staged.</text>\n</svg>\n'
    )


def timeline_svg(art: dict) -> str:
    title = f"{art['title']} — dated anchors"
    sub = "Milestones for the essay. Dates marked soft in prose stay soft."
    lines = header(title, sub)
    y0 = 80
    for i, (when, what) in enumerate(art["anchors"]):
        y = y0 + i * 78
        if i:
            lines.append(f'  <line x1="118" y1="{y - 50}" x2="118" y2="{y + 8}" stroke="{RULE}" stroke-width="2"/>')
        fill = OCHRE if i % 2 == 0 else CREAM
        fg = WHITE if i % 2 == 0 else OCHRE
        lines.append(f'  <rect x="24" y="{y}" width="88" height="28" rx="4" fill="{fill}" stroke="{RULE}"/>')
        lines.append(
            f'  <text x="68" y="{y + 19}" text-anchor="middle" font-family="IBM Plex Sans, system-ui, sans-serif" font-size="11" font-weight="600" fill="{fg}">{esc(when)}</text>'
        )
        lines.append(
            f'  <text x="128" y="{y + 14}" font-family="IBM Plex Sans, system-ui, sans-serif" font-size="14" font-weight="600" fill="{INK}">{esc(what[:70])}</text>'
        )
        lines.append(
            f'  <text x="128" y="{y + 32}" font-family="IBM Plex Sans, system-ui, sans-serif" font-size="12" fill="{MUTED}">Verify in the essay before a print caption locks the year.</text>'
        )
    lines.append(footer())
    return "\n".join(lines)


# Profile helpers: local coordinates, then placed.
def _ovolo(x, y, s, quirk=False):
    # quarter-round opening down-right from top-left
    d = f"M {x} {y} Q {x + s} {y} {x + s} {y + s}"
    if quirk:
        d = f"M {x} {y - 4} L {x} {y} Q {x + s * 1.15} {y + 2} {x + s} {y + s}"
    return d


def profile_path(kind: str, x: float, y: float, s: float = 36) -> str:
    """Return an open path drawing a section from top to bottom, left = wall."""
    if kind == "fillet":
        return f"M {x} {y} L {x + s * 0.35} {y} L {x + s * 0.35} {y + s * 0.35} L {x} {y + s * 0.35}"
    if kind == "ovolo":
        return f"M {x} {y} Q {x + s} {y} {x + s} {y + s}"
    if kind == "ovolo_quirk":
        return f"M {x + 6} {y - 6} L {x + 6} {y} Q {x + s * 1.2} {y + 4} {x + s} {y + s}"
    if kind == "cavetto":
        return f"M {x + s} {y} Q {x} {y} {x} {y + s}"
    if kind == "gorge":
        return f"M {x + s * 1.4} {y} Q {x - 4} {y + 8} {x} {y + s * 1.3}"
    if kind == "cyma_recta":
        return f"M {x} {y} C {x + s * 0.2} {y + s * 0.15} {x + s * 0.15} {y + s * 0.45} {x + s * 0.5} {y + s * 0.5} C {x + s * 0.9} {y + s * 0.55} {x + s} {y + s * 0.75} {x + s} {y + s}"
    if kind == "cyma_reversa":
        return f"M {x} {y} C {x + s * 0.85} {y + s * 0.05} {x + s} {y + s * 0.35} {x + s * 0.55} {y + s * 0.5} C {x + s * 0.1} {y + s * 0.65} {x + s * 0.15} {y + s * 0.9} {x + s * 0.2} {y + s}"
    if kind == "torus":
        return f"M {x} {y} A {s * 0.5} {s * 0.5} 0 0 1 {x} {y + s}"
    if kind == "astragal":
        return f"M {x} {y} A {s * 0.28} {s * 0.28} 0 0 1 {x} {y + s * 0.56}"
    if kind == "scotia":
        return f"M {x + s * 0.15} {y} C {x + s} {y} {x + s} {y + s} {x + s * 0.15} {y + s}"
    if kind == "corona":
        return f"M {x} {y} L {x + s} {y} L {x + s} {y + s * 0.28} L {x + s * 0.22} {y + s * 0.28} L {x + s * 0.22} {y + s * 0.55}"
    if kind == "gothic_roll":
        return f"M {x} {y} A {s * 0.35} {s * 0.35} 0 0 1 {x + s * 0.7} {y + s * 0.2} L {x + s * 0.7} {y + s * 0.35} C {x + s} {y + s * 0.55} {x + s * 0.15} {y + s * 0.7} {x} {y + s}"
    if kind == "bead":
        return f"M {x} {y} A {s * 0.22} {s * 0.22} 0 0 1 {x} {y + s * 0.44}"
    return f"M {x} {y} L {x + s * 0.5} {y + s}"


def stroke_path(d: str, width: float = 2.2) -> str:
    return f'  <path d="{d}" fill="none" stroke="{INK}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"/>'


def label(x: float, y: float, text: str) -> str:
    return (
        f'  <text x="{x}" y="{y}" font-family="IBM Plex Sans, system-ui, sans-serif" '
        f'font-size="12" fill="{INK}">{esc(text)}</text>'
    )


def plate_svg(art: dict) -> str:
    title = f"{art['title']} — shop plate"
    sub = "Line sections for the second heading. Not a knife grind."
    kind = art["plate"]
    lines = header(title, sub)
    lines.append(f'  <rect x="24" y="72" width="712" height="360" fill="{CREAM}" stroke="{RULE}"/>')

    # default: a few labeled profiles
    catalog: dict[str, list[tuple[str, str]]] = {
        "words": [("ovolo", "profile"), ("fillet", "length"), ("cyma_recta", "a stick")],
        "eight": [
            ("fillet", "fillet"),
            ("astragal", "astragal"),
            ("cyma_reversa", "ogee"),
            ("cyma_recta", "cyma recta"),
            ("cavetto", "cavetto"),
            ("ovolo", "ovolo"),
            ("scotia", "scotia"),
            ("torus", "torus"),
        ],
        "greek_roman": [("ovolo", "Roman ovolo"), ("ovolo_quirk", "Greek quirked")],
        "gorge": [("gorge", "Egyptian gorge"), ("cavetto", "small cavetto")],
        "gothic": [("gothic_roll", "roll + hollow"), ("fillet", "fillet")],
        "tuscan_cornice": [("cyma_recta", "cyma"), ("corona", "corona"), ("cyma_reversa", "bedmould")],
        "gibbs": [("cyma_recta", "Gibbs cyma"), ("fillet", "listel"), ("corona", "corona")],
        "ilissus": [("ovolo_quirk", "Ilissus quirk"), ("ovolo", "Roman abacus")],
        "benjamin_exp": [
            ("ovolo", "Roman ovolo"),
            ("ovolo_quirk", "Greek quirk"),
            ("cyma_recta", "covering cyma"),
        ],
        "arris": [("ovolo_quirk", "arris"), ("ovolo_quirk", "arris")],
        "catalog": [("cyma_recta", "SKU crown"), ("corona", "missing corona")],
        "revival_casing": [("ovolo", "Revival casing"), ("ovolo_quirk", "Greek door")],
        "mill_flow": [("fillet", "log"), ("ovolo", "planer"), ("cyma_recta", "sticker")],
        "species_belt": [("ovolo", "oak"), ("cyma_recta", "pine")],
        "four_head": [("fillet", "bottom"), ("ovolo", "right"), ("cavetto", "left"), ("cyma_recta", "top")],
        "skinny": [("cyma_recta", "2-1/4 sprung"), ("corona", "built-up")],
        "materials": [("fillet", "solid"), ("ovolo", "finger-joint"), ("cavetto", "MDF")],
        "cnc_vs": [("fillet", "each / CNC"), ("cyma_recta", "feet / sticker")],
        "clean_edge": [("ovolo", "dust ledge"), ("fillet", "radiused clean")],
        "room_order": [("torus", "base"), ("astragal", "chair"), ("cyma_recta", "crown")],
        "cyma_pair": [("cyma_recta", "recta"), ("cyma_reversa", "reversa")],
        "ogee": [("cyma_reversa", "plain ogee"), ("cyma_reversa", "quirked")],
        "ovolo3": [("ovolo", "Roman"), ("ovolo_quirk", "Greek"), ("ovolo", "router 1/4")],
        "cavetto": [("cavetto", "cavetto"), ("gorge", "sprung cove")],
        "ropes": [("torus", "torus"), ("astragal", "astragal"), ("bead", "bead")],
        "attic_base": [("torus", "upper torus"), ("scotia", "scotia"), ("torus", "lower torus")],
        "corona": [("corona", "with soffit"), ("cyma_recta", "no corona")],
        "built_up": [("cyma_recta", "cyma"), ("corona", "corona"), ("cyma_reversa", "bed")],
        "base": [("fillet", "plinth"), ("ovolo", "base cap"), ("bead", "shoe")],
        "casing": [("ovolo", "clamshell"), ("cyma_reversa", "stepped"), ("ovolo_quirk", "eared")],
        "rails": [("cyma_reversa", "chair / dado"), ("ovolo", "picture")],
        "panel": [("ovolo", "stuck"), ("cyma_reversa", "applied"), ("cyma_reversa", "bolection")],
        "cup": [("cyma_recta", "dry cup"), ("cyma_recta", "wet cup")],
        "knife": [("ovolo", "hook"), ("fillet", "land")],
        "spring": [("cyma_recta", "38° nest"), ("cyma_recta", "45° nest")],
        "species": [("ovolo", "poplar"), ("ovolo_quirk", "oak"), ("cyma_recta", "walnut"), ("fillet", "pine")],
        "plinth": [("fillet", "plinth"), ("ovolo", "casing"), ("cyma_reversa", "backband")],
        "drawing": [("fillet", "paper"), ("ovolo", "grind")],
        "finish": [("fillet", "booth"), ("ovolo", "site")],
        "install": [("fillet", "scribe"), ("ovolo", "caulk")],
        "match": [("ovolo_quirk", "house cookie"), ("ovolo", "catalog cousin")],
        "cheap": [("cyma_recta", "3-5/8 stock"), ("corona", "built-up 7")],
        "stair": [("fillet", "tread"), ("ovolo", "nosing"), ("cyma_reversa", "skirt")],
        "quote": [("fillet", "setup"), ("cyma_recta", "feet"), ("ovolo", "each")],
    }
    items = catalog.get(kind, [("ovolo", kind)])
    n = len(items)
    gap = 712 / max(n, 1)
    for i, (pk, name) in enumerate(items):
        cx = 24 + gap * i + gap * 0.28
        cy = 150
        lines.append(stroke_path(profile_path(pk, cx, cy, 48 if n <= 4 else 34)))
        lines.append(label(cx - 8, 360, name))
        lines.append(
            f'  <line x1="{cx - 10}" y1="140" x2="{cx - 10}" y2="310" stroke="{RULE}" stroke-dasharray="3 4"/>'
        )
    lines.append(
        f'  <text x="36" y="400" font-family="IBM Plex Sans, system-ui, sans-serif" font-size="12" fill="{MUTED}">Wall / fence is the dashed line. Curves are shop language, not CAD export.</text>'
    )
    lines.append(footer())
    return "\n".join(lines)


def write_all() -> None:
    n = 0
    for art in ARTICLES:
        d = ASSETS / art["slug"]
        d.mkdir(parents=True, exist_ok=True)
        (d / "historical-timeline.svg").write_text(timeline_svg(art), encoding="utf-8")
        (d / "shop-plate.svg").write_text(plate_svg(art), encoding="utf-8")
        n += 2
    print(f"wrote {n} svgs under {ASSETS}")


if __name__ == "__main__":
    write_all()
