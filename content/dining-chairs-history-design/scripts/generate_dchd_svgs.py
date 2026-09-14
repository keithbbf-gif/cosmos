#!/usr/bin/env python3
"""Generate original CC0 schematic SVGs for dining-chairs-history-design (no faces)."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "diagrams"

PALETTE = {
    "bg": "#E8E4DC",
    "ink": "#2A2622",
    "muted": "#5A554F",
    "wood": "#8B6F47",
    "line": "#6B6560",
    "accent": "#3D6B8E",
    "tape": "#C45C3E",
}


def wrap(title: str, desc: str, body: str, w: int = 640, h: int = 420) -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-labelledby="title desc">
  <title id="title">{title}</title>
  <desc id="desc">{desc}</desc>
  <rect width="100%" height="100%" fill="{PALETTE['bg']}"/>
{body}
</svg>
"""


def chair_table_gap() -> str:
    body = f"""
  <rect x="80" y="220" width="480" height="12" fill="{PALETTE['wood']}" stroke="{PALETTE['ink']}" stroke-width="2"/>
  <rect x="120" y="232" width="400" height="18" fill="{PALETTE['wood']}" opacity="0.35"/>
  <text x="320" y="248" text-anchor="middle" font-family="Helvetica,Arial,sans-serif" font-size="11" fill="{PALETTE['muted']}">apron</text>
  <rect x="200" y="250" width="160" height="10" fill="{PALETTE['wood']}" stroke="{PALETTE['ink']}"/>
  <line x1="200" y1="260" x2="200" y2="310" stroke="{PALETTE['ink']}" stroke-width="3"/>
  <line x1="360" y1="260" x2="360" y2="310" stroke="{PALETTE['ink']}" stroke-width="3"/>
  <rect x="190" y="300" width="180" height="14" fill="{PALETTE['wood']}" stroke="{PALETTE['ink']}" stroke-width="2"/>
  <text x="280" y="292" text-anchor="middle" font-family="Georgia,serif" font-size="12" fill="{PALETTE['ink']}">seat</text>
  <line x1="280" y1="250" x2="280" y2="300" stroke="{PALETTE['tape']}" stroke-width="2" marker-end="url(#arrow)"/>
  <text x="300" y="275" font-family="Helvetica,Arial,sans-serif" font-size="13" fill="{PALETTE['tape']}">thigh gap</text>
  <defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="{PALETTE['tape']}"/></marker></defs>
"""
    return wrap(
        "Seat-to-apron clearance at dinner",
        "Side elevation: table apron above chair seat; vertical gap labeled for dining ergonomics.",
        body,
    )


def seat_height() -> str:
    body = f"""
  <line x1="100" y1="360" x2="540" y2="360" stroke="{PALETTE['line']}" stroke-width="2"/>
  <rect x="220" y="300" width="200" height="12" fill="{PALETTE['wood']}" stroke="{PALETTE['ink']}" stroke-width="2"/>
  <line x1="180" y1="360" x2="180" y2="312" stroke="{PALETTE['tape']}" stroke-width="2"/>
  <line x1="460" y1="360" x2="460" y2="312" stroke="{PALETTE['tape']}" stroke-width="2"/>
  <line x1="180" y1="336" x2="460" y2="336" stroke="{PALETTE['tape']}" stroke-width="2"/>
  <text x="320" y="328" text-anchor="middle" font-family="Helvetica,Arial,sans-serif" font-size="14" fill="{PALETTE['tape']}">finished seat height (measure after pad settles)</text>
  <text x="320" y="388" text-anchor="middle" font-family="Georgia,serif" font-size="13" fill="{PALETTE['muted']}">finished floor — not carpet nap alone</text>
"""
    return wrap("Measuring finished seat height", "Tape from floor to top of seat rail.", body)


def apron_gap() -> str:
    return chair_table_gap()


def seat_depth() -> str:
    body = f"""
  <rect x="160" y="180" width="320" height="14" fill="{PALETTE['wood']}" stroke="{PALETTE['ink']}" stroke-width="2"/>
  <line x1="160" y1="280" x2="160" y2="194" stroke="{PALETTE['ink']}" stroke-width="3"/>
  <line x1="480" y1="280" x2="480" y2="194" stroke="{PALETTE['ink']}" stroke-width="3"/>
  <line x1="160" y1="194" x2="420" y2="194" stroke="{PALETTE['tape']}" stroke-width="2"/>
  <text x="290" y="186" text-anchor="middle" font-size="13" fill="{PALETTE['tape']}" font-family="Helvetica,Arial,sans-serif">seat depth (front rail to back)</text>
  <circle cx="420" cy="194" r="5" fill="{PALETTE['tape']}"/>
  <text x="430" y="210" font-size="12" fill="{PALETTE['muted']}" font-family="Helvetica,Arial,sans-serif">leave knee free</text>
"""
    return wrap("Seat depth at the dining chair", "Plan view: depth from front rail toward back rail.", body)


def back_rake() -> str:
    body = f"""
  <line x1="280" y1="320" x2="280" y2="120" stroke="{PALETTE['ink']}" stroke-width="4"/>
  <line x1="320" y1="320" x2="350" y2="130" stroke="{PALETTE['accent']}" stroke-width="4"/>
  <line x1="280" y1="320" x2="350" y2="320" stroke="{PALETTE['line']}" stroke-width="2"/>
  <path d="M280 320 A60 60 0 0 0 330 270" fill="none" stroke="{PALETTE['tape']}" stroke-width="2"/>
  <text x="360" y="200" font-family="Helvetica,Arial,sans-serif" font-size="13" fill="{PALETTE['tape']}">back rake</text>
  <text x="120" y="340" font-family="Georgia,serif" font-size="12" fill="{PALETTE['muted']}">too much rake → reach and lounge, not dinner</text>
"""
    return wrap("Back rake versus vertical", "Side view comparing vertical post and raked back.", body)


def lumbar_abstract() -> str:
    body = f"""
  <rect x="200" y="100" width="80" height="200" rx="8" fill="none" stroke="{PALETTE['line']}" stroke-width="2" stroke-dasharray="6 4"/>
  <text x="240" y="90" text-anchor="middle" font-size="11" fill="{PALETTE['muted']}" font-family="Helvetica,Arial,sans-serif">torso outline only</text>
  <rect x="250" y="160" width="40" height="50" fill="none" stroke="{PALETTE['tape']}" stroke-width="2"/>
  <text x="310" y="188" font-size="12" fill="{PALETTE['tape']}" font-family="Helvetica,Arial,sans-serif">office lumbar zone</text>
  <line x1="200" y1="220" x2="330" y2="220" stroke="{PALETTE['wood']}" stroke-width="3"/>
  <text x="320" y="250" font-size="12" fill="{PALETTE['ink']}" font-family="Georgia,serif">dining: shoulder blades meet the splat</text>
"""
    return wrap(
        "Lumbar zone versus dining contact",
        "Abstract torso outline without a face; compares task-chair lumbar band to dining back contact.",
        body,
    )


def front_rail() -> str:
    body = f"""
  <rect x="140" y="200" width="360" height="20" fill="{PALETTE['wood']}" stroke="{PALETTE['ink']}" stroke-width="2"/>
  <text x="320" y="215" text-anchor="middle" font-size="12" fill="{PALETTE['ink']}" font-family="Helvetica,Arial,sans-serif">sharp front rail</text>
  <rect x="140" y="260" width="360" height="20" rx="8" fill="{PALETTE['wood']}" stroke="{PALETTE['ink']}" stroke-width="2"/>
  <text x="320" y="275" text-anchor="middle" font-size="12" fill="{PALETTE['ink']}" font-family="Helvetica,Arial,sans-serif">radiused front rail</text>
  <text x="320" y="330" text-anchor="middle" font-family="Georgia,serif" font-size="13" fill="{PALETTE['muted']}">thigh contact, not catalog glamour</text>
"""
    return wrap("Front rail arris versus radius", "Cross-section comparison of sharp and radiused front rails.", body)


def arm_clearance() -> str:
    body = f"""
  <rect x="100" y="200" width="440" height="16" fill="{PALETTE['wood']}" opacity="0.5"/>
  <text x="320" y="212" text-anchor="middle" font-size="11" fill="{PALETTE['muted']}">table apron zone</text>
  <path d="M180 320 L180 220 L240 200 L240 320 Z" fill="{PALETTE['wood']}" stroke="{PALETTE['ink']}" stroke-width="2"/>
  <path d="M400 320 L400 210 L460 190 L460 320 Z" fill="{PALETTE['accent']}" opacity="0.35" stroke="{PALETTE['accent']}" stroke-width="2"/>
  <line x1="240" y1="200" x2="400" y2="210" stroke="{PALETTE['tape']}" stroke-width="2" stroke-dasharray="5 4"/>
  <text x="320" y="195" text-anchor="middle" font-size="13" fill="{PALETTE['tape']}" font-family="Helvetica,Arial,sans-serif">arm must clear apron</text>
"""
    return wrap("Arm height versus apron", "Plan sketch: arm path crossing apron clearance.", body)


def rack_test() -> str:
    body = f"""
  <polygon points="200,300 360,300 380,120 220,120" fill="none" stroke="{PALETTE['ink']}" stroke-width="3"/>
  <polygon points="200,300 340,310 360,130 220,120" fill="none" stroke="{PALETTE['tape']}" stroke-width="2" stroke-dasharray="6 4"/>
  <text x="320" y="340" text-anchor="middle" font-family="Georgia,serif" font-size="13" fill="{PALETTE['muted']}">lean-back rack: posts no longer square</text>
"""
    return wrap("Racking under diagonal load", "Chair frame skewed to a parallelogram when leaned.", body)


def wheelchair_table() -> str:
    body = f"""
  <rect x="80" y="160" width="480" height="20" fill="{PALETTE['wood']}" stroke="{PALETTE['ink']}"/>
  <rect x="200" y="220" width="240" height="100" rx="6" fill="none" stroke="{PALETTE['accent']}" stroke-width="2"/>
  <text x="320" y="270" text-anchor="middle" font-size="12" fill="{PALETTE['accent']}" font-family="Helvetica,Arial,sans-serif">wheelchair footprint</text>
  <line x1="120" y1="160" x2="120" y2="120" stroke="{PALETTE['tape']}" stroke-width="2"/>
  <line x1="520" y1="160" x2="520" y2="120" stroke="{PALETTE['tape']}" stroke-width="2"/>
  <line x1="120" y1="140" x2="520" y2="140" stroke="{PALETTE['tape']}" stroke-width="2"/>
  <text x="320" y="132" text-anchor="middle" font-size="13" fill="{PALETTE['tape']}">knee clearance + apron height</text>
"""
    return wrap(
        "Wheelchair approach to dining table",
        "Underside clearance dimensions without depicting a person.",
        body,
    )


def measure_points() -> str:
    body = f"""
  <rect x="250" y="240" width="140" height="12" fill="{PALETTE['wood']}" stroke="{PALETTE['ink']}"/>
  <circle cx="250" cy="246" r="4" fill="{PALETTE['tape']}"/>
  <circle cx="390" cy="246" r="4" fill="{PALETTE['tape']}"/>
  <circle cx="320" cy="200" r="4" fill="{PALETTE['tape']}"/>
  <text x="180" y="246" font-size="11" fill="{PALETTE['tape']}">width</text>
  <text x="320" y="190" text-anchor="middle" font-size="11" fill="{PALETTE['tape']}">back height</text>
  <text x="320" y="300" text-anchor="middle" font-family="Georgia,serif" font-size="12" fill="{PALETTE['muted']}">measure wood, not cushion fantasy</text>
"""
    return wrap("Chair measurement points", "Key dimensions on a schematic side chair.", body)


def children_booster() -> str:
    body = f"""
  <rect x="160" y="260" width="320" height="14" fill="{PALETTE['wood']}" stroke="{PALETTE['ink']}"/>
  <rect x="220" y="200" width="200" height="60" fill="none" stroke="{PALETTE['accent']}" stroke-width="2"/>
  <text x="320" y="235" text-anchor="middle" font-size="12" fill="{PALETTE['accent']}">booster / firm seat</text>
  <line x1="320" y1="200" x2="320" y2="160" stroke="{PALETTE['tape']}" stroke-width="2"/>
  <text x="330" y="175" font-size="12" fill="{PALETTE['tape']}">popliteal height</text>
  <text x="320" y="330" text-anchor="middle" font-family="Georgia,serif" font-size="12" fill="{PALETTE['muted']}">no identifiable child — tape and furniture only</text>
"""
    return wrap(
        "Booster seat and table height",
        "Schematic booster block and vertical measure; no faces.",
        body,
    )


DIAGRAMS: dict[str, str] = {
    "the-chair-at-dinner": chair_table_gap(),
    "eighteen-inches": seat_height(),
    "the-gap-under-the-apron": apron_gap(),
    "seat-depth-and-the-knee": seat_depth(),
    "rake-is-not-a-lounge": back_rake(),
    "lumbar-is-the-wrong-word": lumbar_abstract(),
    "the-front-rail-and-the-thigh": front_rail(),
    "arms-that-clear": arm_clearance(),
    "rack-is-the-dinner-test": rack_test(),
    "a-chair-a-wheelchair-can-meet": wheelchair_table(),
    "how-to-measure-a-dining-chair": measure_points(),
    "children-at-the-table": children_booster(),
}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for slug, svg in DIAGRAMS.items():
        path = OUT / f"{slug}.svg"
        path.write_text(svg.strip() + "\n", encoding="utf-8")
        print("wrote", path.relative_to(ROOT))
    print(f"{len(DIAGRAMS)} diagrams")


if __name__ == "__main__":
    main()
