#!/usr/bin/env python3
"""Write original schematic SVGs for the RFQ sales pack (CC0)."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"

PALETTE = {
    "bg": "#f8f7f4",
    "ink": "#3d3832",
    "muted": "#8a8278",
    "accent": "#2f6f4e",
    "blue": "#1d5a8a",
    "panel": "#e8e4dc",
    "block": "#c9bfb0",
}


def wrap(title: str, desc: str, body: str, w: int = 720, h: int = 420) -> str:
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc">
  <title id="title">{title}</title>
  <desc id="desc">{desc}</desc>
  <rect width="{w}" height="{h}" fill="{PALETTE['bg']}"/>
{body}
</svg>
"""


def write(name: str, svg: str) -> None:
    path = ASSETS / name
    path.write_text(svg, encoding="utf-8")
    print("wrote", path.name)


def process_flow() -> None:
    body = f"""
  <text x="360" y="36" text-anchor="middle" font-family="system-ui,sans-serif" font-size="16" font-weight="600" fill="{PALETTE['ink']}">Custom order: measure → quote → acknowledgment</text>
  <rect x="40" y="70" width="180" height="100" rx="8" fill="{PALETTE['panel']}" stroke="{PALETTE['muted']}" stroke-width="2"/>
  <text x="130" y="110" text-anchor="middle" font-family="system-ui,sans-serif" font-size="14" fill="{PALETTE['ink']}">1. Measure</text>
  <text x="130" y="132" text-anchor="middle" font-family="system-ui,sans-serif" font-size="11" fill="{PALETTE['muted']}">tape, path, room</text>
  <path d="M220 120 H260" stroke="{PALETTE['accent']}" stroke-width="3" marker-end="url(#arr)"/>
  <rect x="270" y="70" width="180" height="100" rx="8" fill="{PALETTE['panel']}" stroke="{PALETTE['muted']}" stroke-width="2"/>
  <text x="360" y="110" text-anchor="middle" font-family="system-ui,sans-serif" font-size="14" fill="{PALETTE['ink']}">2. Quote</text>
  <text x="360" y="132" text-anchor="middle" font-family="system-ui,sans-serif" font-size="11" fill="{PALETTE['muted']}">object, inches, finish</text>
  <path d="M450 120 H490" stroke="{PALETTE['accent']}" stroke-width="3" marker-end="url(#arr)"/>
  <rect x="500" y="70" width="180" height="100" rx="8" fill="{PALETTE['block']}" stroke="{PALETTE['ink']}" stroke-width="2"/>
  <text x="590" y="110" text-anchor="middle" font-family="system-ui,sans-serif" font-size="14" fill="{PALETTE['ink']}">3. Ack</text>
  <text x="590" y="132" text-anchor="middle" font-family="system-ui,sans-serif" font-size="11" fill="{PALETTE['muted']}">date, deposit, spec</text>
  <text x="360" y="220" text-anchor="middle" font-family="system-ui,sans-serif" font-size="12" fill="{PALETTE['blue']}">Educational flow — not your signed contract</text>
  <rect x="80" y="260" width="560" height="120" rx="6" fill="#fff" stroke="{PALETTE['muted']}" stroke-width="1"/>
  <text x="100" y="288" font-family="system-ui,sans-serif" font-size="12" fill="{PALETTE['ink']}">Measure owns the inch · Quote names the build · Ack starts the queue clock</text>
  <text x="100" y="312" font-family="system-ui,sans-serif" font-size="11" fill="{PALETTE['muted']}">Skip a step and the number on paper stops matching the room.</text>
  <defs><marker id="arr" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="{PALETTE['accent']}"/></marker></defs>
"""
    write(
        "process-measure-quote-ack.svg",
        wrap(
            "Measure quote acknowledgment process",
            "Three-step diagram: site measure, written quote, signed acknowledgment for custom furniture orders.",
            body,
            720,
            400,
        ),
    )


def rfq_packet() -> None:
    body = f"""
  <text x="360" y="32" text-anchor="middle" font-family="system-ui,sans-serif" font-size="15" font-weight="600" fill="{PALETTE['ink']}">RFQ packet (one page anatomy)</text>
  <rect x="60" y="50" width="600" height="320" fill="#fff" stroke="{PALETTE['ink']}" stroke-width="2"/>
  <line x1="60" y1="90" x2="660" y2="90" stroke="{PALETTE['muted']}"/>
  <text x="80" y="78" font-family="system-ui,sans-serif" font-size="12" fill="{PALETTE['ink']}">Object · Inches · Path · Finish · Freight · Requested date</text>
  <rect x="80" y="110" width="260" height="50" fill="{PALETTE['panel']}" stroke="{PALETTE['muted']}"/>
  <text x="210" y="140" text-anchor="middle" font-family="system-ui,sans-serif" font-size="12">What we are building</text>
  <rect x="360" y="110" width="280" height="50" fill="{PALETTE['panel']}" stroke="{PALETTE['muted']}"/>
  <text x="500" y="140" text-anchor="middle" font-family="system-ui,sans-serif" font-size="12">Who measured / when</text>
  <rect x="80" y="180" width="560" height="60" fill="{PALETTE['panel']}" stroke="{PALETTE['muted']}"/>
  <text x="360" y="215" text-anchor="middle" font-family="system-ui,sans-serif" font-size="12">Delivery path: door, stair, landing, soffit</text>
  <rect x="80" y="260" width="270" height="50" fill="{PALETTE['block']}" stroke="{PALETTE['muted']}"/>
  <text x="215" y="290" text-anchor="middle" font-family="system-ui,sans-serif" font-size="12">Finish direction + samples</text>
  <rect x="370" y="260" width="270" height="50" fill="{PALETTE['block']}" stroke="{PALETTE['muted']}"/>
  <text x="505" y="290" text-anchor="middle" font-family="system-ui,sans-serif" font-size="12">Ship-to + install tier</text>
"""
    write(
        "schematic-rfq-packet.svg",
        wrap("RFQ one-page anatomy", "Labeled blocks for object, measure, path, finish, and freight fields.", body, 720, 390),
    )


def dining_clearances() -> None:
    body = f"""
  <rect x="40" y="40" width="640" height="340" fill="{PALETTE['panel']}" stroke="{PALETTE['muted']}" stroke-width="2"/>
  <rect x="200" y="120" width="320" height="120" fill="{PALETTE['block']}" stroke="{PALETTE['ink']}" stroke-width="2"/>
  <text x="360" y="185" text-anchor="middle" font-family="system-ui,sans-serif" font-size="13">Table (plan view)</text>
  <text x="120" y="185" text-anchor="middle" font-family="system-ui,sans-serif" font-size="11" fill="{PALETTE['blue']}">36 in min</text>
  <text x="600" y="185" text-anchor="middle" font-family="system-ui,sans-serif" font-size="11" fill="{PALETTE['blue']}">36 in min</text>
  <text x="360" y="95" text-anchor="middle" font-family="system-ui,sans-serif" font-size="11" fill="{PALETTE['accent']}">42 in pass (example)</text>
  <circle cx="150" cy="180" r="14" fill="none" stroke="{PALETTE['ink']}" stroke-width="1.5"/>
  <circle cx="570" cy="180" r="14" fill="none" stroke="{PALETTE['ink']}" stroke-width="1.5"/>
  <text x="360" y="320" text-anchor="middle" font-family="system-ui,sans-serif" font-size="11" fill="{PALETTE['muted']}">NKBA-style planning numbers — verify against your edition</text>
"""
    write(
        "schematic-dining-clearances.svg",
        wrap(
            "Dining table clearance diagram",
            "Top-down table with 36-inch chair zones and 42-inch pass aisle example.",
            body,
        ),
    )


def island_aisles() -> None:
    body = f"""
  <rect x="40" y="40" width="640" height="340" fill="{PALETTE['panel']}" stroke="{PALETTE['muted']}" stroke-width="2"/>
  <rect x="220" y="120" width="280" height="180" fill="{PALETTE['block']}" stroke="{PALETTE['ink']}" stroke-width="2"/>
  <text x="360" y="215" text-anchor="middle" font-family="system-ui,sans-serif" font-size="13">Island</text>
  <text x="360" y="82" text-anchor="middle" font-family="system-ui,sans-serif" font-size="12" fill="{PALETTE['accent']}">42 in walk aisle (example)</text>
  <text x="175" y="215" text-anchor="end" font-family="system-ui,sans-serif" font-size="11" fill="{PALETTE['blue']}">48 in work aisle (example)</text>
"""
    write(
        "schematic-island-aisles.svg",
        wrap("Kitchen island aisle widths", "Rectangular island with labeled walk and work aisles.", body),
    )


def lead_time_stack() -> None:
    colors = ["#5c5348", "#6b8e4e", "#8a6f4e", "#4a7c9e", "#7a5c8a", "#9a6b4a"]
    labels = ["Queue", "Lumber", "Mill", "Finish", "Buyouts", "Freight"]
    body = ""
    x = 60
    for i, (lab, col) in enumerate(zip(labels, colors)):
        body += f'  <rect x="{x}" y="120" width="90" height="160" fill="{col}" opacity="0.85"/>\n'
        body += f'  <text x="{x + 45}" y="300" text-anchor="middle" font-family="system-ui,sans-serif" font-size="11" fill="{PALETTE["ink"]}">{lab}</text>\n'
        if i < len(labels) - 1:
            body += f'  <path d="M{x + 90} 200 H{x + 110}" stroke="{PALETTE["ink"]}" stroke-width="2" marker-end="url(#arr)"/>\n'
        x += 100
    body += f"""
  <text x="360" y="48" text-anchor="middle" font-family="system-ui,sans-serif" font-size="15" font-weight="600" fill="{PALETTE['ink']}">Lead time is a stack, not a stamp</text>
  <defs><marker id="arr" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="{PALETTE['ink']}"/></marker></defs>
"""
    write(
        "schematic-lead-time-stack.svg",
        wrap("Lead time stack diagram", "Sequential shop stages from queue through freight.", body, 720, 340),
    )


def delivery_path() -> None:
    body = f"""
  <polyline points="80,300 180,300 180,220 320,220 320,140 480,140 480,80 620,80" fill="none" stroke="{PALETTE['accent']}" stroke-width="4"/>
  <circle cx="80" cy="300" r="8" fill="{PALETTE['ink']}"/>
  <text x="80" y="330" text-anchor="middle" font-family="system-ui,sans-serif" font-size="10">Truck</text>
  <text x="180" y="250" text-anchor="middle" font-family="system-ui,sans-serif" font-size="10">Door</text>
  <text x="320" y="250" text-anchor="middle" font-family="system-ui,sans-serif" font-size="10">Hall</text>
  <text x="480" y="110" text-anchor="middle" font-family="system-ui,sans-serif" font-size="10">Stair / landing</text>
  <text x="620" y="110" text-anchor="middle" font-family="system-ui,sans-serif" font-size="10">Room</text>
  <text x="360" y="40" text-anchor="middle" font-family="system-ui,sans-serif" font-size="14" font-weight="600" fill="{PALETTE['ink']}">Delivery path (plan + section sketch)</text>
"""
    write(
        "schematic-delivery-path.svg",
        wrap("Furniture delivery path", "Path from truck through door, hall, stair, and into the room.", body),
    )


def out_of_square() -> None:
    body = f"""
  <polygon points="120,280 520,260 500,80 100,100" fill="{PALETTE['panel']}" stroke="{PALETTE['ink']}" stroke-width="2"/>
  <text x="310" y="200" text-anchor="middle" font-family="system-ui,sans-serif" font-size="13">Room plan (not square)</text>
  <text x="310" y="40" text-anchor="middle" font-family="system-ui,sans-serif" font-size="14" font-weight="600" fill="{PALETTE['ink']}">Measure the real corners</text>
  <text x="520" y="270" font-family="system-ui,sans-serif" font-size="11" fill="{PALETTE['blue']}">91° example</text>
"""
    write(
        "schematic-out-of-square-room.svg",
        wrap("Out-of-square room sketch", "Four-sided room polygon with unequal angles.", body),
    )


def ack_form() -> None:
    body = f"""
  <rect x="100" y="60" width="520" height="300" fill="#fff" stroke="{PALETTE['ink']}" stroke-width="2"/>
  <text x="360" y="95" text-anchor="middle" font-family="system-ui,sans-serif" font-size="14" font-weight="600">Acknowledgment (educational blank)</text>
  <line x1="130" y1="130" x2="590" y2="130" stroke="{PALETTE['muted']}"/>
  <text x="140" y="155" font-family="system-ui,sans-serif" font-size="12">Promised week of: ___________</text>
  <text x="140" y="185" font-family="system-ui,sans-serif" font-size="12">Deposit received: ___________</text>
  <text x="140" y="215" font-family="system-ui,sans-serif" font-size="12">Drawing revision: ___________</text>
  <text x="140" y="260" font-family="system-ui,sans-serif" font-size="11" fill="{PALETTE['blue']}">The date on the ack — not the hallway maybe</text>
"""
    write(
        "schematic-ack-form.svg",
        wrap("Acknowledgment date fields", "Blank acknowledgment with date, deposit, and drawing revision lines.", body),
    )


def approval_drawing() -> None:
    body = f"""
  <rect x="80" y="50" width="560" height="300" fill="#fff" stroke="{PALETTE['ink']}" stroke-width="2"/>
  <rect x="100" y="70" width="360" height="220" fill="{PALETTE['panel']}" stroke="{PALETTE['muted']}"/>
  <text x="280" y="190" text-anchor="middle" font-family="system-ui,sans-serif" font-size="12">Elevation / plan</text>
  <rect x="480" y="70" width="140" height="220" fill="{PALETTE['block']}" stroke="{PALETTE['muted']}"/>
  <text x="550" y="120" text-anchor="middle" font-family="system-ui,sans-serif" font-size="11">Rev</text>
  <text x="550" y="145" text-anchor="middle" font-family="system-ui,sans-serif" font-size="11">Date</text>
  <text x="550" y="170" text-anchor="middle" font-family="system-ui,sans-serif" font-size="11">Initial</text>
  <text x="360" y="32" text-anchor="middle" font-family="system-ui,sans-serif" font-size="14" font-weight="600">Approval drawing is the order</text>
"""
    write(
        "schematic-approval-drawing.svg",
        wrap("Shop approval drawing layout", "Drawing sheet with revision block.", body, 720, 370),
    )


def rfq_checklist() -> None:
    items = ["Object named", "Inches + path", "Finish", "Freight tier", "Requested date"]
    body = f'<text x="360" y="36" text-anchor="middle" font-family="system-ui,sans-serif" font-size="15" font-weight="600" fill="{PALETTE["ink"]}">One-sitting RFQ checklist</text>\n'
    y = 70
    for item in items:
        body += f'  <rect x="120" y="{y}" width="24" height="24" fill="#fff" stroke="{PALETTE["ink"]}"/>\n'
        body += f'  <text x="160" y="{y + 17}" font-family="system-ui,sans-serif" font-size="13">{item}</text>\n'
        y += 44
    write(
        "schematic-rfq-checklist.svg",
        wrap("RFQ checklist", "Checkbox list for a complete request for quote.", body, 720, 320),
    )


def generic_schematic(name: str, title: str, desc: str, line: str) -> None:
    body = f"""
  <text x="360" y="48" text-anchor="middle" font-family="system-ui,sans-serif" font-size="15" font-weight="600" fill="{PALETTE['ink']}">{title}</text>
  <rect x="100" y="100" width="520" height="200" rx="8" fill="{PALETTE['panel']}" stroke="{PALETTE['muted']}" stroke-width="2"/>
  <text x="360" y="210" text-anchor="middle" font-family="system-ui,sans-serif" font-size="13" fill="{PALETTE['ink']}">{line}</text>
"""
    write(name, wrap(title, desc, body, 720, 330))


def main() -> int:
    ASSETS.mkdir(parents=True, exist_ok=True)
    process_flow()
    rfq_packet()
    dining_clearances()
    island_aisles()
    lead_time_stack()
    delivery_path()
    out_of_square()
    ack_form()
    approval_drawing()
    rfq_checklist()
    generic_schematic(
        "schematic-three-prices.svg",
        "Three prices that are not quotes",
        "Ballpark, catalog list, and allowance versus written quote.",
        "Ballpark · List price · Allowance — not the ack",
    )
    generic_schematic(
        "schematic-custom-vs-stock.svg",
        "Custom versus made-to-order versus stock",
        "Three-channel comparison for RFQ routing.",
        "Custom · MTO · Stock SKU",
    )
    generic_schematic(
        "schematic-deposit-split.svg",
        "Deposit versus balance",
        "Educational split bar for deposit and progress.",
        "Deposit buys queue slot · Balance buys completion",
    )
    generic_schematic(
        "schematic-change-order-clock.svg",
        "Change order clock",
        "Timeline showing revision cutoff before mill.",
        "Revision window closes before cut list",
    )
    generic_schematic(
        "schematic-freight-tiers.svg",
        "Freight and white-glove tiers",
        "Threshold, room-of-choice, and white-glove labels.",
        "Threshold · Room · White glove (define on ack)",
    )
    generic_schematic(
        "schematic-commercial-vs-house.svg",
        "Commercial RFQ versus house RFQ",
        "Spec section contrast for millwork-grade jobs.",
        "AWI spec block · House packet",
    )
    body = f"""
  <rect x="80" y="80" width="200" height="360" rx="16" fill="#222" stroke="{PALETTE['ink']}" stroke-width="2"/>
  <rect x="95" y="100" width="170" height="280" fill="#4a90d9"/>
  <text x="180" y="420" text-anchor="middle" font-family="system-ui,sans-serif" font-size="11">Phone display (saturated)</text>
  <rect x="360" y="120" width="280" height="200" fill="{PALETTE['block']}" stroke="{PALETTE['muted']}" stroke-width="2"/>
  <text x="500" y="210" text-anchor="middle" font-family="system-ui,sans-serif" font-size="12">Finish board in room light</text>
  <text x="360" y="48" text-anchor="middle" font-family="system-ui,sans-serif" font-size="14" font-weight="600">Screen color ≠ stain in the room</text>
"""
    write(
        "schematic-phone-vs-room-light.svg",
        wrap(
            "Phone screen versus room-light sample",
            "Contrast between saturated phone display and physical finish sample.",
            body,
            720,
            460,
        ),
    )
    print(f"SVG count in {ASSETS}: {len(list(ASSETS.glob('*.svg')))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
