#!/usr/bin/env python3
"""Write original CC0 schematic SVGs for the healthcare institutional furniture pack."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIAGRAMS = ROOT / "assets" / "diagrams"

PALETTE = {
    "bg": "#f6f5f2",
    "ink": "#2e2a26",
    "muted": "#7a746c",
    "accent": "#1d5c4a",
    "warn": "#9a3b2e",
    "blue": "#1a4d7a",
    "panel": "#ebe6dd",
    "block": "#cfc5b8",
    "dash": "#b8aea3",
}


def wrap(title: str, desc: str, body: str, w: int = 960, h: int = 540) -> str:
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc">
  <title id="title">{title}</title>
  <desc id="desc">{desc}</desc>
  <rect width="{w}" height="{h}" fill="{PALETTE['bg']}"/>
{body}
</svg>
"""


def write(name: str, svg: str) -> None:
    DIAGRAMS.mkdir(parents=True, exist_ok=True)
    path = DIAGRAMS / name
    path.write_text(svg, encoding="utf-8")
    print("wrote", path.relative_to(ROOT))


def snf_single_room() -> None:
    p = PALETTE
    body = f"""
  <text x="480" y="36" text-anchor="middle" font-family="system-ui,sans-serif" font-size="17" font-weight="600" fill="{p['ink']}">SNF single room — usable rectangle (notional 100 ft² floor)</text>
  <rect x="80" y="60" width="800" height="420" fill="#fff" stroke="{p['ink']}" stroke-width="2"/>
  <rect x="520" y="90" width="120" height="200" fill="{p['panel']}" stroke="{p['accent']}" stroke-width="2"/>
  <text x="580" y="175" text-anchor="middle" font-family="system-ui,sans-serif" font-size="12" fill="{p['ink']}">Toilet</text>
  <text x="580" y="195" text-anchor="middle" font-family="system-ui,sans-serif" font-size="10" fill="{p['muted']}">(punched from plan)</text>
  <rect x="120" y="120" width="360" height="100" fill="{p['block']}" stroke="{p['ink']}" stroke-width="2"/>
  <text x="300" y="165" text-anchor="middle" font-family="system-ui,sans-serif" font-size="13" fill="{p['ink']}">Bed envelope + rails up</text>
  <rect x="120" y="240" width="90" height="50" fill="{p['panel']}" stroke="{p['muted']}"/>
  <text x="165" y="270" text-anchor="middle" font-family="system-ui,sans-serif" font-size="11">Nightstand</text>
  <rect x="230" y="300" width="70" height="70" fill="{p['panel']}" stroke="{p['muted']}"/>
  <text x="265" y="340" text-anchor="middle" font-family="system-ui,sans-serif" font-size="10">Chair</text>
  <rect x="320" y="300" width="100" height="24" fill="none" stroke="{p['blue']}" stroke-width="2" stroke-dasharray="6 4"/>
  <text x="370" y="318" text-anchor="middle" font-family="system-ui,sans-serif" font-size="10" fill="{p['blue']}">Overbed parked</text>
  <path d="M120 230 H480" stroke="{p['accent']}" stroke-width="3" marker-end="url(#arr)"/>
  <text x="300" y="222" text-anchor="middle" font-family="system-ui,sans-serif" font-size="11" fill="{p['accent']}">Working aisle / lift path</text>
  <rect x="400" y="300" width="80" height="180" fill="{p['panel']}" stroke="{p['muted']}"/>
  <text x="440" y="390" text-anchor="middle" font-family="system-ui,sans-serif" font-size="11">Wardrobe</text>
  <text x="120" y="500" font-family="system-ui,sans-serif" font-size="11" fill="{p['muted']}">CMS floor: ≥100 ft² single (42 CFR 483.90(e)(1)(ii)) — furniture lives in the leftover.</text>
  <defs><marker id="arr" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="{p['accent']}"/></marker></defs>
"""
    write(
        "snf-single-room-plan.svg",
        wrap(
            "SNF single room plan schematic",
            "Plan view showing bed envelope, working aisle, toilet punch-out, and case goods in a notional 100 square foot skilled nursing room.",
            body,
        ),
    )


def snf_double_room() -> None:
    p = PALETTE
    body = f"""
  <text x="480" y="34" text-anchor="middle" font-family="system-ui,sans-serif" font-size="16" font-weight="600" fill="{p['ink']}">SNF double — two 80 ft² floors, one width problem</text>
  <rect x="60" y="55" width="840" height="400" fill="#fff" stroke="{p['ink']}" stroke-width="2"/>
  <line x1="480" y1="55" x2="480" y2="455" stroke="{p['dash']}" stroke-width="2" stroke-dasharray="8 6"/>
  <text x="480" y="75" text-anchor="middle" font-family="system-ui,sans-serif" font-size="11" fill="{p['muted']}">Privacy curtain track</text>
  <rect x="90" y="100" width="170" height="90" fill="{p['block']}" stroke="{p['ink']}"/>
  <rect x="700" y="100" width="170" height="90" fill="{p['block']}" stroke="{p['ink']}"/>
  <text x="175" y="150" text-anchor="middle" font-family="system-ui,sans-serif" font-size="12">Bed A</text>
  <text x="785" y="150" text-anchor="middle" font-family="system-ui,sans-serif" font-size="12">Bed B</text>
  <rect x="90" y="210" width="55" height="45" fill="{p['panel']}" stroke="{p['muted']}"/>
  <rect x="815" y="210" width="55" height="45" fill="{p['panel']}" stroke="{p['muted']}"/>
  <text x="480" y="280" text-anchor="middle" font-family="system-ui,sans-serif" font-size="12" fill="{p['warn']}">Shared aisle — overbed + lift compete here</text>
  <path d="M260 320 H700" stroke="{p['accent']}" stroke-width="2"/>
  <text x="480" y="340" text-anchor="middle" font-family="system-ui,sans-serif" font-size="11" fill="{p['accent']}">Case-goods strip along wall only</text>
  <text x="90" y="430" font-family="system-ui,sans-serif" font-size="11" fill="{p['muted']}">≥80 ft² per resident in a multiple bedroom — width, not area, punishes paired nightstands.</text>
"""
    write(
        "snf-double-room-plan.svg",
        wrap("SNF double bedroom plan", "Two bed envelopes separated by curtain track with shared center aisle.", body),
    )


def entrapment_zones() -> None:
    p = PALETTE
    body = f"""
  <text x="480" y="32" text-anchor="middle" font-family="system-ui,sans-serif" font-size="16" font-weight="600" fill="{p['ink']}">Hospital bed system — seven entrapment zones (FDA 2006, educational)</text>
  <rect x="200" y="70" width="560" height="120" rx="6" fill="{p['panel']}" stroke="{p['ink']}" stroke-width="2"/>
  <text x="480" y="135" text-anchor="middle" font-family="system-ui,sans-serif" font-size="13">Mattress deck (side elevation)</text>
  <rect x="180" y="60" width="24" height="140" fill="{p['block']}" stroke="{p['warn']}" stroke-width="2"/>
  <rect x="756" y="60" width="24" height="140" fill="{p['block']}" stroke="{p['warn']}" stroke-width="2"/>
  <text x="192" y="220" text-anchor="middle" font-family="system-ui,sans-serif" font-size="9" fill="{p['warn']}">Z1</text>
  <text x="768" y="220" text-anchor="middle" font-family="system-ui,sans-serif" font-size="9" fill="{p['warn']}">Z1</text>
  <text x="300" y="205" font-family="system-ui,sans-serif" font-size="10" fill="{p['blue']}">Z2 under rail</text>
  <text x="420" y="195" font-family="system-ui,sans-serif" font-size="10" fill="{p['blue']}">Z3 rail–mattress</text>
  <text x="210" y="95" font-family="system-ui,sans-serif" font-size="10" fill="{p['blue']}">Z4 end bay</text>
  <text x="620" y="95" font-family="system-ui,sans-serif" font-size="10" fill="{p['muted']}">Z5 split gap</text>
  <text x="140" y="130" font-family="system-ui,sans-serif" font-size="10" fill="{p['muted']}">Z6 rail–board</text>
  <text x="720" y="130" font-family="system-ui,sans-serif" font-size="10" fill="{p['muted']}">Z7 board–mattress</text>
  <text x="480" y="260" text-anchor="middle" font-family="system-ui,sans-serif" font-size="11" fill="{p['ink']}">Zones 1–3: &lt;120 mm (4.75 in) recommended · Zone 4: &lt;60 mm (2.375 in) + angle table</text>
  <text x="480" y="285" text-anchor="middle" font-family="system-ui,sans-serif" font-size="11" fill="{p['muted']}">Zones 5–7 named in guidance — not “safe by silence.” Open FDA/HBSW drawings for assessment.</text>
  <rect x="80" y="310" width="800" height="200" fill="#fff" stroke="{p['muted']}" stroke-width="1"/>
  <text x="100" y="340" font-family="system-ui,sans-serif" font-size="12" fill="{p['ink']}">Furniture-adjacent: Zone 3 (mattress width/softness) · Zone 6 (decorative headboard) · Zone 7 (footboard gap)</text>
  <text x="100" y="365" font-family="system-ui,sans-serif" font-size="11" fill="{p['muted']}">Not a substitute for HBSW measurement methods or clinical assessment.</text>
"""
    write(
        "seven-entrapment-zones.svg",
        wrap("Seven bed entrapment zones diagram", "Side elevation schematic labeling FDA Hospital Bed Safety Workgroup zones 1 through 7.", body),
    )


def side_rail_geometry() -> None:
    p = PALETTE
    body = f"""
  <text x="480" y="32" text-anchor="middle" font-family="system-ui,sans-serif" font-size="16" font-weight="600" fill="{p['ink']}">Side rail nicknames vs. openings (geometry, not restraint paperwork)</text>
  <g font-family="system-ui,sans-serif" font-size="11" fill="{p['ink']}">
    <text x="120" y="70" font-weight="600">Full rail</text>
    <rect x="100" y="85" width="200" height="100" fill="{p['panel']}" stroke="{p['ink']}"/>
    <rect x="95" y="80" width="12" height="110" fill="{p['block']}" stroke="{p['warn']}"/>
    <rect x="293" y="80" width="12" height="110" fill="{p['block']}" stroke="{p['warn']}"/>
    <text x="200" y="205" text-anchor="middle" fill="{p['muted']}">Wall with holes (Zones 1–2)</text>
    <text x="400" y="70" font-weight="600">Half rail</text>
    <rect x="380" y="85" width="200" height="100" fill="{p['panel']}" stroke="{p['ink']}"/>
    <rect x="375" y="120" width="12" height="70" fill="{p['block']}" stroke="{p['warn']}"/>
    <text x="480" y="205" text-anchor="middle" fill="{p['muted']}">End bay + torso gap (Zones 4–6)</text>
    <text x="680" y="70" font-weight="600">Intermediate</text>
    <rect x="660" y="85" width="200" height="100" fill="{p['panel']}" stroke="{p['ink']}"/>
    <rect x="655" y="100" width="12" height="45" fill="{p['block']}" stroke="{p['accent']}" transform="rotate(-25 661 122)"/>
    <text x="760" y="205" text-anchor="middle" fill="{p['accent']}">Left “kind” — measure anyway</text>
  </g>
  <text x="480" y="280" text-anchor="middle" font-family="system-ui,sans-serif" font-size="12" fill="{p['ink']}">Measure at flat, articulated, and intermediate — mattress vendor on the same line as the rail.</text>
  <text x="480" y="305" text-anchor="middle" font-family="system-ui,sans-serif" font-size="11" fill="{p['muted']}">Wooden caps and bumpers are accessories; they change openings.</text>
"""
    write(
        "side-rail-geometry.svg",
        wrap("Side rail geometry schematic", "Educational comparison of full, half, and intermediate rail positions relative to mattress openings.", body),
    )


def room_walkthrough() -> None:
    p = PALETTE
    body = f"""
  <text x="480" y="32" text-anchor="middle" font-family="system-ui,sans-serif" font-size="16" font-weight="600" fill="{p['ink']}">Walk-through path — door sightline to bed face</text>
  <rect x="100" y="60" width="760" height="400" fill="#fff" stroke="{p['ink']}" stroke-width="2"/>
  <rect x="100" y="360" width="80" height="100" fill="{p['panel']}" stroke="{p['accent']}" stroke-width="2"/>
  <text x="140" y="415" text-anchor="middle" font-family="system-ui,sans-serif" font-size="11">Door</text>
  <path d="M180 410 Q400 200 620 150" fill="none" stroke="{p['accent']}" stroke-width="2" marker-end="url(#arr)"/>
  <text x="400" y="240" text-anchor="middle" font-family="system-ui,sans-serif" font-size="11" fill="{p['accent']}">Staff sightline</text>
  <rect x="580" y="120" width="220" height="100" fill="{p['block']}" stroke="{p['ink']}"/>
  <text x="690" y="175" text-anchor="middle" font-family="system-ui,sans-serif" font-size="12">Head of bed</text>
  <text x="120" y="100" font-family="system-ui,sans-serif" font-size="11" fill="{p['muted']}">1. Threshold · 2. Crash path · 3. Rail state · 4. Overbed parked · 5. Oxygen zone</text>
  <defs><marker id="arr" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="{p['accent']}"/></marker></defs>
"""
    write(
        "room-walkthrough-sightline.svg",
        wrap("SNF room walk-through sightline", "Plan schematic from door to bed head for survey-style walk-through.", body),
    )


def ada_turn() -> None:
    p = PALETTE
    body = f"""
  <text x="480" y="32" text-anchor="middle" font-family="system-ui,sans-serif" font-size="16" font-weight="600" fill="{p['ink']}">Wheelchair turning — resident room (educational, not ADA certification)</text>
  <circle cx="480" cy="280" r="120" fill="none" stroke="{p['blue']}" stroke-width="2" stroke-dasharray="10 6"/>
  <text x="480" y="285" text-anchor="middle" font-family="system-ui,sans-serif" font-size="12" fill="{p['blue']}">60 in circle (common clear floor)</text>
  <rect x="120" y="120" width="740" height="320" fill="#fff" stroke="{p['muted']}" stroke-width="1"/>
  <rect x="140" y="140" width="200" height="90" fill="{p['block']}" stroke="{p['ink']}"/>
  <text x="240" y="190" text-anchor="middle" font-family="system-ui,sans-serif" font-size="11">Bed</text>
  <text x="480" y="430" font-family="system-ui,sans-serif" font-size="11" fill="{p['muted']}">Draw the turn before the wardrobe door swing — state licensure may exceed federal room area.</text>
"""
    write(
        "ada-resident-room-turn.svg",
        wrap("Wheelchair turning clearance in resident room", "Plan view with notional 60-inch turning circle and bed footprint.", body),
    )


def overbed_clearance() -> None:
    p = PALETTE
    body = f"""
  <text x="480" y="32" text-anchor="middle" font-family="system-ui,sans-serif" font-size="16" font-weight="600" fill="{p['ink']}">Overbed table — base vs. wheelchair footplate</text>
  <rect x="200" y="100" width="400" height="80" fill="{p['panel']}" stroke="{p['ink']}"/>
  <text x="400" y="145" text-anchor="middle" font-family="system-ui,sans-serif" font-size="12">Bed deck</text>
  <rect x="250" y="200" width="300" height="20" fill="{p['block']}" stroke="{p['accent']}"/>
  <text x="400" y="215" text-anchor="middle" font-family="system-ui,sans-serif" font-size="10">Table top</text>
  <ellipse cx="320" cy="320" rx="50" ry="30" fill="none" stroke="{p['warn']}" stroke-width="2"/>
  <text x="320" y="325" text-anchor="middle" font-family="system-ui,sans-serif" font-size="10" fill="{p['warn']}">Footplate</text>
  <text x="480" y="400" text-anchor="middle" font-family="system-ui,sans-serif" font-size="11" fill="{p['muted']}">Apron height and base width are politics in the aisle.</text>
"""
    write(
        "overbed-table-clearance.svg",
        wrap("Overbed table clearance schematic", "Side view showing table base relative to wheelchair footplate zone.", body),
    )


def nurses_station() -> None:
    p = PALETTE
    body = f"""
  <text x="480" y="32" text-anchor="middle" font-family="system-ui,sans-serif" font-size="16" font-weight="600" fill="{p['ink']}">Nurses' station — seated-to-seated sightline</text>
  <rect x="80" y="80" width="800" height="60" fill="{p['block']}" stroke="{p['ink']}" stroke-width="2"/>
  <text x="480" y="115" text-anchor="middle" font-family="system-ui,sans-serif" font-size="12">Transaction counter (standing height)</text>
  <circle cx="200" cy="280" r="28" fill="{p['panel']}" stroke="{p['muted']}"/>
  <circle cx="760" cy="280" r="28" fill="{p['panel']}" stroke="{p['muted']}"/>
  <text x="200" y="285" text-anchor="middle" font-family="system-ui,sans-serif" font-size="10">CNA seated</text>
  <text x="760" y="285" text-anchor="middle" font-family="system-ui,sans-serif" font-size="10">Resident seated</text>
  <line x1="228" y1="280" x2="732" y2="280" stroke="{p['accent']}" stroke-width="2" stroke-dasharray="6 4"/>
  <text x="480" y="260" text-anchor="middle" font-family="system-ui,sans-serif" font-size="11" fill="{p['accent']}">Can one seated person see another?</text>
"""
    write(
        "nurses-station-sightline.svg",
        wrap("Nurses station sightline schematic", "Elevation showing seated sightline question at transaction height millwork.", body),
    )


def mattress_gap() -> None:
    p = PALETTE
    body = f"""
  <text x="480" y="32" text-anchor="middle" font-family="system-ui,sans-serif" font-size="16" font-weight="600" fill="{p['ink']}">Zone 3 — rail-to-mattress canyon (mattress mismatch)</text>
  <rect x="160" y="100" width="640" height="100" fill="{p['panel']}" stroke="{p['ink']}"/>
  <rect x="140" y="90" width="20" height="120" fill="{p['block']}" stroke="{p['warn']}"/>
  <rect x="800" y="90" width="20" height="120" fill="{p['block']}" stroke="{p['warn']}"/>
  <rect x="200" y="110" width="520" height="70" fill="#fff" stroke="{p['accent']}" stroke-width="2"/>
  <text x="460" y="155" text-anchor="middle" font-family="system-ui,sans-serif" font-size="12" fill="{p['accent']}">Gap opens when deck + mattress ≠ rail design</text>
  <text x="480" y="280" text-anchor="middle" font-family="system-ui,sans-serif" font-size="11" fill="{p['muted']}">Foam softening and articulation change the number you took on install day.</text>
"""
    write(
        "mattress-zone3-gap.svg",
        wrap("Zone 3 mattress gap schematic", "Side view highlighting rail-to-mattress opening when mattress does not match bed system.", body),
    )


def low_bed() -> None:
    p = PALETTE
    body = f"""
  <text x="480" y="32" text-anchor="middle" font-family="system-ui,sans-serif" font-size="16" font-weight="600" fill="{p['ink']}">Low bed deck height vs. fall culture (notional)</text>
  <line x1="100" y1="380" x2="860" y2="380" stroke="{p['ink']}" stroke-width="2"/>
  <rect x="280" y="280" width="400" height="100" fill="{p['panel']}" stroke="{p['ink']}"/>
  <text x="480" y="335" text-anchor="middle" font-family="system-ui,sans-serif" font-size="12">Standard deck</text>
  <rect x="280" y="320" width="400" height="60" fill="{p['block']}" stroke="{p['accent']}" stroke-width="2"/>
  <text x="480" y="355" text-anchor="middle" font-family="system-ui,sans-serif" font-size="12" fill="{p['accent']}">Low deck</text>
  <text x="480" y="420" text-anchor="middle" font-family="system-ui,sans-serif" font-size="11" fill="{p['muted']}">Lower deck changes reach to nightstand and rail assist — not a furniture catalog toggle.</text>
"""
    write(
        "low-bed-deck-height.svg",
        wrap("Low bed deck height comparison", "Side elevation comparing standard and low mattress deck heights.", body),
    )


def channel_punchout() -> None:
    p = PALETTE
    body = f"""
  <text x="480" y="32" text-anchor="middle" font-family="system-ui,sans-serif" font-size="16" font-weight="600" fill="{p['ink']}">Distributor punchout — rectangle between mill and dock</text>
  <rect x="80" y="100" width="180" height="80" fill="{p['panel']}" stroke="{p['muted']}"/>
  <text x="170" y="145" text-anchor="middle" font-family="system-ui,sans-serif" font-size="12">Mill cut list</text>
  <rect x="380" y="90" width="200" height="100" fill="{p['block']}" stroke="{p['ink']}" stroke-width="2"/>
  <text x="480" y="135" text-anchor="middle" font-family="system-ui,sans-serif" font-size="13">Catalog / punchout</text>
  <text x="480" y="155" text-anchor="middle" font-family="system-ui,sans-serif" font-size="10" fill="{p['muted']}">no logos in staging art</text>
  <rect x="700" y="100" width="180" height="80" fill="{p['panel']}" stroke="{p['muted']}"/>
  <text x="790" y="145" text-anchor="middle" font-family="system-ui,sans-serif" font-size="12">SNF dock</text>
  <path d="M260 140 H380" stroke="{p['accent']}" stroke-width="3" marker-end="url(#arr)"/>
  <path d="M580 140 H700" stroke="{p['accent']}" stroke-width="3" marker-end="url(#arr)"/>
  <defs><marker id="arr" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="{p['accent']}"/></marker></defs>
"""
    write(
        "medline-channel-punchout.svg",
        wrap("Medical distributor punchout channel schematic", "Flow from mill documentation through catalog punchout to facility receiving.", body),
    )


def hospital_vs_residential() -> None:
    p = PALETTE
    body = f"""
  <text x="480" y="32" text-anchor="middle" font-family="system-ui,sans-serif" font-size="16" font-weight="600" fill="{p['ink']}">Residential twin vs. hospital bed envelope</text>
  <rect x="120" y="120" width="300" height="70" fill="{p['panel']}" stroke="{p['muted']}"/>
  <text x="270" y="160" text-anchor="middle" font-family="system-ui,sans-serif" font-size="12">Twin mattress (~39 in class)</text>
  <rect x="540" y="100" width="360" height="110" fill="{p['block']}" stroke="{p['ink']}" stroke-width="2"/>
  <text x="720" y="145" text-anchor="middle" font-family="system-ui,sans-serif" font-size="12">Hospital deck + rails + articulation</text>
  <text x="480" y="280" text-anchor="middle" font-family="system-ui,sans-serif" font-size="11" fill="{p['muted']}">The SNF room is dimensioned for the machine, not the comforter set.</text>
"""
    write(
        "hospital-vs-residential-bed.svg",
        wrap("Hospital bed vs residential twin schematic", "Plan-width comparison of residential twin versus hospital bed envelope.", body),
    )


def ward_to_private() -> None:
    p = PALETTE
    body = f"""
  <text x="480" y="32" text-anchor="middle" font-family="system-ui,sans-serif" font-size="16" font-weight="600" fill="{p['ink']}">Ward row → private room — footprint shift</text>
  <g font-family="system-ui,sans-serif" font-size="11">
    <text x="200" y="70" text-anchor="middle" font-weight="600">Ward (many beds, one air)</text>
    <rect x="60" y="85" width="280" height="180" fill="#fff" stroke="{p['muted']}"/>
    <rect x="75" y="100" width="50" height="150" fill="{p['panel']}" stroke="{p['dash']}"/>
    <rect x="135" y="100" width="50" height="150" fill="{p['panel']}" stroke="{p['dash']}"/>
    <rect x="195" y="100" width="50" height="150" fill="{p['panel']}" stroke="{p['dash']}"/>
    <rect x="255" y="100" width="50" height="150" fill="{p['panel']}" stroke="{p['dash']}"/>
    <text x="620" y="70" text-anchor="middle" font-weight="600">Private room (one envelope)</text>
    <rect x="480" y="85" width="280" height="180" fill="#fff" stroke="{p['ink']}" stroke-width="2"/>
    <rect x="520" y="110" width="200" height="90" fill="{p['block']}" stroke="{p['accent']}"/>
    <rect x="520" y="210" width="60" height="40" fill="{p['panel']}" stroke="{p['muted']}"/>
  </g>
  <path d="M350 175 H470" stroke="{p['accent']}" stroke-width="3" marker-end="url(#arr)"/>
  <defs><marker id="arr" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="{p['accent']}"/></marker></defs>
"""
    write(
        "ward-to-private-room.svg",
        wrap("Ward to private room layout shift", "Comparison of multi-bed ward row versus single resident room envelope.", body),
    )


def privacy_curtain() -> None:
    p = PALETTE
    body = f"""
  <text x="480" y="32" text-anchor="middle" font-family="system-ui,sans-serif" font-size="16" font-weight="600" fill="{p['ink']}">Cubicle track bend + mesh at sprinkler (plan)</text>
  <path d="M120 200 Q480 80 840 200" fill="none" stroke="{p['ink']}" stroke-width="3"/>
  <circle cx="480" cy="120" r="14" fill="{p['warn']}" stroke="{p['ink']}"/>
  <text x="500" y="125" font-family="system-ui,sans-serif" font-size="10" fill="{p['warn']}">Sprinkler</text>
  <rect x="440" y="180" width="80" height="40" fill="none" stroke="{p['blue']}" stroke-width="2" stroke-dasharray="4 3"/>
  <text x="480" y="250" text-anchor="middle" font-family="system-ui,sans-serif" font-size="11" fill="{p['muted']}">Mesh panel — laundry path, not a permanent wall.</text>
"""
    write(
        "privacy-curtain-track.svg",
        wrap("Privacy curtain track schematic", "Plan view of curved cubicle track with sprinkler clearance callout.", body),
    )


def spec_sheet() -> None:
    p = PALETTE
    body = f"""
  <text x="480" y="32" text-anchor="middle" font-family="system-ui,sans-serif" font-size="16" font-weight="600" fill="{p['ink']}">Spec sheet anatomy — what the mill needs</text>
  <rect x="120" y="70" width="720" height="380" fill="#fff" stroke="{p['ink']}" stroke-width="2"/>
  <line x1="120" y1="120" x2="840" y2="120" stroke="{p['muted']}"/>
  <text x="140" y="105" font-family="system-ui,sans-serif" font-size="12">W × D × H · finish · edge · hardware · freight class</text>
  <rect x="140" y="140" width="320" height="50" fill="{p['panel']}" stroke="{p['muted']}"/>
  <text x="300" y="170" text-anchor="middle" font-family="system-ui,sans-serif" font-size="11">Materials + fire tags</text>
  <rect x="140" y="210" width="640" height="80" fill="{p['panel']}" stroke="{p['muted']}"/>
  <text x="460" y="255" text-anchor="middle" font-family="system-ui,sans-serif" font-size="11">Install / anchor / anti-tip</text>
  <rect x="140" y="310" width="640" height="50" fill="{p['block']}" stroke="{p['accent']}"/>
  <text x="460" y="340" text-anchor="middle" font-family="system-ui,sans-serif" font-size="11">Mattress line + bed model (if adjacent)</text>
"""
    write(
        "spec-sheet-anatomy.svg",
        wrap("Healthcare furniture spec sheet anatomy", "Labeled blocks for dimensions, fire materials, install, and bed adjacency.", body),
    )


def bariatric_envelope() -> None:
    p = PALETTE
    body = f"""
  <text x="480" y="32" text-anchor="middle" font-family="system-ui,sans-serif" font-size="16" font-weight="600" fill="{p['ink']}">Bariatric bed envelope — aisle theft</text>
  <rect x="180" y="140" width="520" height="120" fill="{p['block']}" stroke="{p['warn']}" stroke-width="2"/>
  <text x="440" y="205" text-anchor="middle" font-family="system-ui,sans-serif" font-size="13">Wider deck + motors</text>
  <path d="M120 280 H840" stroke="{p['accent']}" stroke-width="2"/>
  <text x="480" y="300" text-anchor="middle" font-family="system-ui,sans-serif" font-size="11" fill="{p['accent']}">Remaining aisle after “upgrade” bed</text>
"""
    write(
        "bariatric-bed-envelope.svg",
        wrap("Bariatric bed envelope schematic", "Plan view showing wider bed footprint consuming aisle width.", body),
    )


def fire_labels() -> None:
    p = PALETTE
    body = f"""
  <text x="480" y="32" text-anchor="middle" font-family="system-ui,sans-serif" font-size="16" font-weight="600" fill="{p['ink']}">CAL TB 117-2013 vs. NFPA 101 — sticker is not a program</text>
  <rect x="160" y="120" width="240" height="120" fill="#fff" stroke="{p['ink']}"/>
  <text x="280" y="175" text-anchor="middle" font-family="system-ui,sans-serif" font-size="12">TB 117-2013 label</text>
  <rect x="560" y="120" width="240" height="120" fill="#fff" stroke="{p['ink']}"/>
  <text x="680" y="175" text-anchor="middle" font-family="system-ui,sans-serif" font-size="12">NFPA 101 adoption</text>
  <text x="480" y="320" text-anchor="middle" font-family="system-ui,sans-serif" font-size="11" fill="{p['muted']}">Read the state adoption book — a tag photo is evidence, not a life-safety program.</text>
"""
    write(
        "fire-code-labels.svg",
        wrap("Fire code labels schematic", "Two-panel schematic contrasting California TB 117 furniture label and NFPA 101 adoption context.", body),
    )


def bifma_stamp() -> None:
    p = PALETTE
    body = f"""
  <text x="480" y="32" text-anchor="middle" font-family="system-ui,sans-serif" font-size="16" font-weight="600" fill="{p['ink']}">BIFMA stamp ≠ healthcare bed-system stamp</text>
  <rect x="140" y="120" width="280" height="100" rx="8" fill="{p['panel']}" stroke="{p['muted']}"/>
  <text x="280" y="175" text-anchor="middle" font-family="system-ui,sans-serif" font-size="13">Office / contract casegood</text>
  <rect x="540" y="120" width="280" height="100" rx="8" fill="{p['block']}" stroke="{p['warn']}" stroke-width="2"/>
  <text x="680" y="175" text-anchor="middle" font-family="system-ui,sans-serif" font-size="13">Bed + rail + mattress system</text>
  <text x="480" y="300" text-anchor="middle" font-family="system-ui,sans-serif" font-size="11" fill="{p['muted']}">Different test houses — do not swap certificates in a punchout line item.</text>
"""
    write(
        "bifma-vs-bed-system.svg",
        wrap("BIFMA vs healthcare bed system schematic", "Comparison panels for office furniture testing versus hospital bed entrapment system.", body),
    )


def room_package() -> None:
    p = PALETTE
    body = f"""
  <text x="480" y="32" text-anchor="middle" font-family="system-ui,sans-serif" font-size="16" font-weight="600" fill="{p['ink']}">Room package — bid tab meets cut list</text>
  <rect x="100" y="90" width="360" height="300" fill="#fff" stroke="{p['muted']}"/>
  <text x="280" y="120" text-anchor="middle" font-family="system-ui,sans-serif" font-size="12">Bid tab (qty × room type)</text>
  <rect x="500" y="90" width="360" height="300" fill="#fff" stroke="{p['ink']}" stroke-width="2"/>
  <text x="680" y="120" text-anchor="middle" font-family="system-ui,sans-serif" font-size="12">Shop cut list</text>
  <path d="M460 240 H500" stroke="{p['accent']}" stroke-width="3" marker-end="url(#arr)"/>
  <text x="480" y="270" text-anchor="middle" font-family="system-ui,sans-serif" font-size="10" fill="{p['accent']}">One marriage</text>
  <defs><marker id="arr" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="{p['accent']}"/></marker></defs>
"""
    write(
        "room-package-cutlist.svg",
        wrap("SNF room package schematic", "Two documents: bid quantity tab and mill cut list linked for install.", body),
    )


def memory_care() -> None:
    p = PALETTE
    body = f"""
  <text x="480" y="32" text-anchor="middle" font-family="system-ui,sans-serif" font-size="16" font-weight="600" fill="{p['ink']}">Memory care — wander loop vs. anchored furniture</text>
  <rect x="120" y="80" width="720" height="360" fill="#fff" stroke="{p['ink']}"/>
  <path d="M200 200 H760 V360 H200 Z" fill="none" stroke="{p['blue']}" stroke-width="2" stroke-dasharray="8 5"/>
  <text x="480" y="400" text-anchor="middle" font-family="system-ui,sans-serif" font-size="11" fill="{p['blue']}">Circulation loop (not a maze graphic)</text>
  <rect x="240" y="240" width="80" height="50" fill="{p['panel']}" stroke="{p['accent']}"/>
  <text x="280" y="270" text-anchor="middle" font-family="system-ui,sans-serif" font-size="10">Anchored seating</text>
"""
    write(
        "memory-care-loop.svg",
        wrap("Memory care furniture layout schematic", "Plan with circulation loop and anchored seating footprint.", body),
    )


def cms_tags() -> None:
    p = PALETTE
    body = f"""
  <text x="480" y="32" text-anchor="middle" font-family="system-ui,sans-serif" font-size="16" font-weight="600" fill="{p['ink']}">CMS tags that touch furniture — F584 · F917 (educational)</text>
  <rect x="120" y="100" width="340" height="140" fill="{p['panel']}" stroke="{p['ink']}"/>
  <text x="290" y="150" text-anchor="middle" font-family="system-ui,sans-serif" font-size="13">F584 — belongings / homelike</text>
  <rect x="500" y="100" width="340" height="140" fill="{p['panel']}" stroke="{p['ink']}"/>
  <text x="670" y="150" text-anchor="middle" font-family="system-ui,sans-serif" font-size="13">F917 — accident hazards</text>
  <text x="480" y="320" text-anchor="middle" font-family="system-ui,sans-serif" font-size="11" fill="{p['muted']}">Open the current SOM — tag text moves; furniture shows up in the interpretive examples.</text>
"""
    write(
        "cms-f584-f917-tags.svg",
        wrap("CMS F584 and F917 furniture tags schematic", "Two-panel educational schematic for survey tags that reference resident belongings and hazards.", body),
    )


def main() -> int:
    snf_single_room()
    snf_double_room()
    entrapment_zones()
    side_rail_geometry()
    room_walkthrough()
    ada_turn()
    overbed_clearance()
    nurses_station()
    mattress_gap()
    low_bed()
    channel_punchout()
    hospital_vs_residential()
    ward_to_private()
    privacy_curtain()
    spec_sheet()
    bariatric_envelope()
    fire_labels()
    bifma_stamp()
    room_package()
    memory_care()
    cms_tags()
    print(f"done — {len(list(DIAGRAMS.glob('*.svg')))} diagrams")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
