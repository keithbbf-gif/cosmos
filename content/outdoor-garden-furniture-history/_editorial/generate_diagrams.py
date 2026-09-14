#!/usr/bin/env python3
"""Generate original OGFH editorial SVGs (object/schematic only — no faces)."""

from __future__ import annotations

from pathlib import Path

from svg_common import ACCENT, BG, GREEN, INK, METAL, MUTED, WATER, WOOD, label, wrap

OUT = Path(__file__).resolve().parents[1] / "assets" / "diagrams"
SHARED = Path(__file__).resolve().parents[1] / "assets" / "_shared"


def featured() -> str:
    body = f"""
  <rect x="60" y="80" width="760" height="360" fill="#e8eef2" stroke="{INK}" stroke-width="1.5"/>
  <path d="M120,320 L280,200 L440,280 L600,180 L760,260" fill="none" stroke="{ACCENT}" stroke-width="3"/>
  <rect x="200" y="300" width="120" height="12" fill="{WOOD}" stroke="{INK}"/>
  <rect x="520" y="290" width="140" height="10" fill="{METAL}" stroke="{INK}"/>
  {label(440, 60, "Outdoor & garden furniture — history & materials", 16)}
  {label(440, 420, "Weather · materials · shop honesty (BBF editorial schematic)", 11, fill=MUTED)}
"""
    return wrap(
        "OGFH series type plate",
        "Series header schematic with bench and chair silhouettes on a timeline stroke.",
        body,
    )


DIAGRAMS: dict[str, tuple[str, str, str]] = {}


def add(stem: str, title: str, desc: str, body: str) -> None:
    DIAGRAMS[stem] = (title, desc, body)


def build_all() -> None:
    add(
        "00-01-weather-problem",
        "Outdoor furniture weather forces",
        "Rain, ultraviolet, and freeze acting on a seat joint.",
        f"""
  {label(440, 48, "THREE CLIENTS ON ONE BENCH", 13)}
  <rect x="320" y="200" width="240" height="24" fill="{WOOD}" stroke="{INK}"/>
  <circle cx="200" cy="160" r="36" fill="none" stroke="{ACCENT}" stroke-width="2"/>
  {label(200, 165, "UV", 12)}
  <path d="M200,196 L360,212" stroke="{ACCENT}" stroke-width="1.5" marker-end="url(#a)"/>
  <path d="M440,120 L440,200" stroke="{WATER}" stroke-width="3"/>
  {label(440, 108, "RAIN", 12)}
  <path d="M520,300 L680,300" stroke="{MUTED}" stroke-width="2" stroke-dasharray="8 6"/>
  {label(600, 288, "FREEZE LINE", 10)}
  <polygon points="680,280 700,320 660,320" fill="{WATER}" opacity="0.5"/>
  {label(440, 360, "Joint / film / fastener fails in public", 11, fill=MUTED)}
""",
    )
    add(
        "00-02-three-climates",
        "Porch patio and open lawn climates",
        "Three outdoor sitting assignments with different roof and splash exposure.",
        f"""
  {label(160, 50, "PORCH (roof)", 12)}
  <polygon points="80,120 240,120 260,200 60,200" fill="#e2e8f0" stroke="{INK}"/>
  <rect x="100" y="200" width="120" height="8" fill="{WOOD}" stroke="{INK}"/>
  {label(440, 50, "PATIO (slab)", 12)}
  <rect x="360" y="200" width="160" height="12" fill="#cbd5e1" stroke="{INK}"/>
  <rect x="400" y="170" width="80" height="6" fill="{METAL}" stroke="{INK}"/>
  {label(720, 50, "LAWN (open sky)", 12)}
  <ellipse cx="720" cy="220" rx="100" ry="40" fill="{GREEN}" opacity="0.35"/>
  <rect x="680" y="200" width="80" height="8" fill="{WOOD}" stroke="{INK}"/>
  {label(440, 400, "One word — outdoor — hides three specifications", 11, fill=MUTED)}
""",
    )
    add(
        "00-03-who-is-talking",
        "Indoor shop adjacent to outdoor teaching",
        "Truck leaving indoor casegoods shop beside outdoor climate diagram.",
        f"""
  <rect x="80" y="140" width="280" height="200" fill="#f1f5f9" stroke="{INK}"/>
  {label(220, 170, "BBF indoor casegoods", 12)}
  <rect x="120" y="220" width="200" height="60" fill="{WOOD}" stroke="{INK}"/>
  <path d="M360,240 L520,240" stroke="{INK}" stroke-width="2"/>
  {label(440, 228, "teach weather", 10)}
  <rect x="520" y="120" width="280" height="220" fill="#fff7ed" stroke="{ACCENT}" stroke-width="1.5"/>
  {label(660, 150, "Outdoor history", 12)}
  {label(660, 280, "No invented patio SKU", 11, fill=MUTED)}
""",
    )
    add(
        "00-04-stolen-words",
        "Stolen outdoor furniture words",
        "Labels showing marketing words diverging from material meaning.",
        f"""
  {label(440, 55, "WORD → OLD MEANING → CATALOG MEANING", 12)}
  <line x1="120" y1="120" x2="760" y2="120" stroke="{MUTED}"/>
  <line x1="120" y1="200" x2="760" y2="200" stroke="{MUTED}"/>
  <line x1="120" y1="280" x2="760" y2="280" stroke="{MUTED}"/>
  {label(200, 110, "teak", 11, "start")}
  {label(520, 110, "tree + oil", 11, "start")}
  {label(720, 110, "color", 11, "start")}
  {label(200, 190, "wrought", 11, "start")}
  {label(520, 190, "smith iron", 11, "start")}
  {label(720, 190, "scroll", 11, "start")}
  {label(200, 270, "all-weather", 11, "start")}
  {label(520, 270, "climate duty", 11, "start")}
  {label(720, 270, "feeling", 11, "start")}
""",
    )
    add(
        "01-05-peristyle",
        "Roman peristyle courtyard plan",
        "Colonade around a central garden court.",
        f"""
  <rect x="200" y="100" width="480" height="320" fill="{GREEN}" opacity="0.25" stroke="{INK}"/>
  <rect x="160" y="80" width="40" height="360" fill="#e2e8f0" stroke="{INK}"/>
  <rect x="680" y="80" width="40" height="360" fill="#e2e8f0" stroke="{INK}"/>
  <rect x="200" y="80" width="480" height="40" fill="#e2e8f0" stroke="{INK}"/>
  <rect x="200" y="400" width="480" height="40" fill="#e2e8f0" stroke="{INK}"/>
  <circle cx="440" cy="260" r="40" fill="{WATER}" opacity="0.5"/>
  {label(440, 50, "COLONNADE = SHADE FURNITURE", 12)}
  {label(440, 460, "Outdoor room by architecture, not by sofa", 11, fill=MUTED)}
""",
    )
    add(
        "01-06-marble-bronze",
        "Material survival bias in garden history",
        "Stone and bronze surviving while wood evidence is lost.",
        f"""
  <rect x="120" y="180" width="100" height="160" fill="#d1d5db" stroke="{INK}"/>
  {label(170, 360, "marble", 10)}
  <rect x="280" y="220" width="80" height="120" fill="{METAL}" stroke="{INK}"/>
  {label(320, 360, "bronze", 10)}
  <rect x="420" y="260" width="120" height="80" fill="{WOOD}" stroke="{INK}" stroke-dasharray="6 4" opacity="0.5"/>
  {label(480, 360, "wood (lost)", 10)}
  {label(440, 80, "Museum bias toward what weather spared", 12)}
""",
    )
    add(
        "01-07-islamic-courtyard",
        "Courtyard shade and water section",
        "Shaded walk, fountain, and hard seat in hot climate.",
        f"""
  <rect x="100" y="80" width="680" height="360" fill="#fffbeb" stroke="{INK}"/>
  <rect x="100" y="80" width="120" height="360" fill="#e2e8f0"/>
  <rect x="660" y="80" width="120" height="360" fill="#e2e8f0"/>
  <rect x="380" y="300" width="120" height="20" fill="#d6d3d1" stroke="{INK}"/>
  <ellipse cx="440" cy="220" rx="50" ry="30" fill="{WATER}" opacity="0.6"/>
  {label(440, 60, "SHADE IS LAW", 13)}
""",
    )
    add(
        "01-08-chinese-garden-seat",
        "Porcelain garden drum seat",
        "Drum-shaped pierced garden seat silhouette.",
        f"""
  <ellipse cx="440" cy="320" rx="140" ry="40" fill="#e2e8f0" stroke="{INK}"/>
  <rect x="300" y="180" width="280" height="140" rx="20" fill="#f8fafc" stroke="{INK}" stroke-width="2"/>
  <circle cx="380" cy="250" r="18" fill="none" stroke="{MUTED}"/>
  <circle cx="500" cy="250" r="18" fill="none" stroke="{MUTED}"/>
  {label(440, 80, "DRUM STOOL — GARDEN SEAT, NOT NIGHTSTAND", 12)}
""",
    )
    add(
        "01-09-italian-villa-stone",
        "Villa bench aimed at a view",
        "Stone bench on axis toward a landscape prospect.",
        f"""
  <path d="M80,380 L800,380" stroke="{GREEN}" stroke-width="2"/>
  <path d="M440,380 L440,120" stroke="{ACCENT}" stroke-width="2" stroke-dasharray="6 4"/>
  <rect x="360" y="300" width="160" height="24" fill="#d1d5db" stroke="{INK}"/>
  <polygon points="440,100 520,200 360,200" fill="none" stroke="{MUTED}" stroke-width="1.5"/>
  {label(440, 70, "BENCH AS VIEWING MACHINE", 12)}
""",
    )
    add(
        "02-10-french-garden-theater",
        "French garden axis blocking",
        "Seat placed on a formal axis as staging.",
        f"""
  <path d="M440,80 L440,440" stroke="{MUTED}" stroke-width="1"/>
  <path d="M120,260 L760,260" stroke="{MUTED}" stroke-width="1"/>
  <rect x="400" y="320" width="80" height="16" fill="{METAL}" stroke="{INK}"/>
  <circle cx="440" cy="260" r="60" fill="none" stroke="{GREEN}" stroke-width="1.5"/>
  {label(440, 50, "FURNITURE AS BLOCKING ON AXIS", 12)}
""",
    )
    add(
        "02-11-english-landscape-bench",
        "English landscape bench at a vista",
        "Rustic bench at a rise overlooking composed view.",
        f"""
  <path d="M80,340 Q440,120 800,300" fill="none" stroke="{GREEN}" stroke-width="2"/>
  <rect x="300" y="280" width="140" height="12" fill="{WOOD}" stroke="{INK}"/>
  <line x1="300" y1="292" x2="280" y2="340" stroke="{INK}"/>
  <line x1="440" y1="292" x2="460" y2="340" stroke="{INK}"/>
  {label(440, 80, "BENCH = CAMERA FOR A FAKE WILDERNESS", 11)}
""",
    )
    add(
        "02-12-coalbrookdale",
        "Cast iron garden seat pattern",
        "Victorian cast back with fern motif on foundry bench.",
        f"""
  <path d="M200,360 L680,360" stroke="{INK}" stroke-width="3"/>
  <path d="M240,360 L240,220 Q440,120 640,220 L640,360" fill="none" stroke="{METAL}" stroke-width="4"/>
  <path d="M300,200 Q340,160 380,200 Q420,240 460,200" fill="none" stroke="{GREEN}" stroke-width="2"/>
  {label(440, 80, "FERN IS A PATTERN PLATE", 13)}
  {label(440, 420, "Weight · rust · foundry — not woodland spirit", 11, fill=MUTED)}
""",
    )
    add(
        "02-13-victorian-display",
        "Victorian garden display overload",
        "Many outdoor objects in rain.",
        f"""
  <ellipse cx="440" cy="120" rx="200" ry="60" fill="#e2e8f0" stroke="{MUTED}"/>
  <path d="M360,120 L380,200 M440,120 L440,200 M520,120 L500,200" stroke="{WATER}" stroke-width="2"/>
  <rect x="200" y="280" width="60" height="40" fill="{METAL}" stroke="{INK}"/>
  <rect x="300" y="300" width="50" height="30" fill="{WOOD}" stroke="{INK}"/>
  <circle cx="500" cy="300" r="30" fill="#d1d5db" stroke="{INK}"/>
  <rect x="580" y="290" width="70" height="35" fill="{WOOD}" stroke="{INK}"/>
  {label(440, 400, "Display habit + rain = first casualties", 11, fill=MUTED)}
""",
    )
    add(
        "02-14-conservatory-lie",
        "Conservatory versus open patio",
        "Glazed room furniture versus sky furniture.",
        f"""
  <rect x="80" y="120" width="320" height="280" fill="#e0f2fe" stroke="{INK}" opacity="0.5"/>
  <line x1="80" y1="120" x2="400" y2="120" stroke="{INK}" stroke-width="2"/>
  <line x1="200" y1="120" x2="200" y2="400" stroke="{INK}" stroke-width="1"/>
  <rect x="140" y="300" width="100" height="40" fill="{WOOD}" stroke="{INK}"/>
  {label(240, 90, "CONSERVATORY", 11)}
  <rect x="480" y="320" width="320" height="20" fill="#cbd5e1" stroke="{INK}"/>
  <rect x="560" y="260" width="120" height="60" fill="#fca5a5" stroke="{INK}" opacity="0.4"/>
  {label(640, 90, "OPEN PATIO", 11)}
  {label(640, 380, "Upholstery without glass = lie", 10, fill=MUTED)}
""",
    )
    add(
        "03-15-american-porch",
        "American porch as roofed room",
        "House porch section between street and interior.",
        f"""
  <rect x="120" y="200" width="200" height="180" fill="#f1f5f9" stroke="{INK}"/>
  <polygon points="100,200 220,140 340,200" fill="#e2e8f0" stroke="{INK}"/>
  <rect x="360" y="200" width="400" height="180" fill="#fff7ed" stroke="{ACCENT}"/>
  {label(260, 320, "porch room", 11)}
  {label(560, 320, "street / yard", 11)}
  {label(440, 80, "ROOF IS THE SPEC", 13)}
""",
    )
    add(
        "03-16-porch-rocker",
        "Porch rocking chair runners",
        "Rocking chair with runners for a roofed floor.",
        f"""
  <path d="M280,340 Q320,300 360,340 Q400,380 440,340 Q480,300 520,340" fill="none" stroke="{WOOD}" stroke-width="6"/>
  <rect x="320" y="220" width="160" height="80" fill="{WOOD}" stroke="{INK}" opacity="0.8"/>
  <line x1="340" y1="220" x2="360" y2="160" stroke="{INK}" stroke-width="3"/>
  <line x1="460" y1="220" x2="440" y2="160" stroke="{INK}" stroke-width="3"/>
  {label(440, 80, "RUNNERS FOR A ROOFED FLOOR", 12)}
""",
    )
    add(
        "03-17-adirondack",
        "Adirondack plank chair elevation",
        "Wide-arm slatted outdoor chair side view.",
        f"""
  <polygon points="300,360 340,280 380,200 420,180 460,200 500,280 540,360" fill="{WOOD}" stroke="{INK}" opacity="0.7"/>
  <rect x="280" y="200" width="280" height="16" fill="{WOOD}" stroke="{INK}"/>
  <line x1="280" y1="216" x2="240" y2="260" stroke="{INK}" stroke-width="3"/>
  <line x1="560" y1="216" x2="600" y2="260" stroke="{INK}" stroke-width="3"/>
  {label(440, 80, "ELEVEN BOARDS — PLANK MACHINE", 12)}
""",
    )
    add(
        "03-18-mission-porch",
        "Mission oak porch under roof",
        "Straight oak chair under porch roof line.",
        f"""
  <line x1="120" y1="160" x2="760" y2="160" stroke="{INK}" stroke-width="4"/>
  <rect x="340" y="240" width="200" height="120" fill="{WOOD}" stroke="{INK}"/>
  <rect x="360" y="200" width="20" height="160" fill="{WOOD}" stroke="{INK}"/>
  <rect x="500" y="200" width="20" height="160" fill="{WOOD}" stroke="{INK}"/>
  {label(440, 100, "OAK HONESTY — STILL NEEDS THE ROOF", 11)}
""",
    )
    add(
        "03-19-porch-wicker",
        "Porch wicker needs a roof",
        "Woven skin chair under porch versus rain.",
        f"""
  <polygon points="200,160 680,160 700,200 180,200" fill="#e2e8f0" stroke="{INK}"/>
  <ellipse cx="360" cy="300" rx="100" ry="80" fill="none" stroke="{ACCENT}" stroke-width="2"/>
  <path d="M320,280 Q360,320 400,280" fill="none" stroke="{ACCENT}"/>
  <path d="M520,120 L540,320" stroke="{WATER}" stroke-width="3"/>
  {label(360, 400, "Wicker under roof", 10)}
  {label(600, 400, "Rain on patio", 10, fill=MUTED)}
""",
    )
    add(
        "03-20-patio-ate-porch",
        "Patio slab without porch roof",
        "Backyard slab with sky-exposed seating.",
        f"""
  <rect x="200" y="280" width="480" height="120" fill="#cbd5e1" stroke="{INK}"/>
  <rect x="120" y="200" width="80" height="160" fill="#f1f5f9" stroke="{INK}" opacity="0.4"/>
  {label(160, 190, "porch (empty)", 9, fill=MUTED)}
  <rect x="360" y="240" width="160" height="40" fill="{METAL}" stroke="{INK}"/>
  {label(440, 80, "SKY FURNITURE ON A SLAB", 13)}
""",
    )
    add(
        "03-21-aluminum-after-war",
        "Postwar aluminum stacking chairs",
        "Light tubular aluminum chairs that stack.",
        f"""
  <rect x="280" y="300" width="60" height="6" fill="{METAL}" stroke="{INK}"/>
  <rect x="360" y="290" width="60" height="6" fill="{METAL}" stroke="{INK}"/>
  <rect x="440" y="280" width="60" height="6" fill="{METAL}" stroke="{INK}"/>
  <line x1="300" y1="306" x2="300" y2="360" stroke="{METAL}" stroke-width="3"/>
  <line x1="380" y1="296" x2="380" y2="350" stroke="{METAL}" stroke-width="3"/>
  <line x1="460" y1="286" x2="460" y2="340" stroke="{METAL}" stroke-width="3"/>
  {label(440, 80, "STACK · LIGHT · HEAT", 13)}
""",
    )
    add(
        "04-22-teak-oil-silica",
        "Teak oil and silica in wood",
        "Cross-section callouts for natural oil and silica.",
        f"""
  <rect x="300" y="160" width="280" height="200" fill="{WOOD}" stroke="{INK}"/>
  <line x1="300" y1="200" x2="580" y2="240" stroke="{MUTED}" stroke-width="1"/>
  <line x1="300" y1="260" x2="580" y2="300" stroke="{MUTED}" stroke-width="1"/>
  {label(440, 120, "TEAK — OIL + SILICA, NOT A CAN COLOR", 12)}
  {label(440, 400, "Silvering = sun on the surface", 11, fill=MUTED)}
""",
    )
    add(
        "04-23-cedar-cypress",
        "Cedar and cypress extractives",
        "Outdoor heartwood boards with rot resistance note.",
        f"""
  <rect x="240" y="200" width="160" height="120" fill="#c4a484" stroke="{INK}"/>
  <rect x="480" y="200" width="160" height="120" fill="#a8b5a0" stroke="{INK}"/>
  {label(320, 350, "cedar", 11)}
  {label(560, 350, "cypress", 11)}
  {label(440, 90, "EXTRACTIVES HELP — STILL WOOD", 12)}
""",
    )
    add(
        "04-24-ipe-hardness",
        "Ipe hardness and fasteners",
        "Dense deck board with screw callout.",
        f"""
  <rect x="260" y="220" width="360" height="80" fill="#8b5a2b" stroke="{INK}"/>
  <circle cx="320" cy="260" r="8" fill="{METAL}"/>
  <circle cx="400" cy="260" r="8" fill="{METAL}"/>
  <circle cx="480" cy="260" r="8" fill="{METAL}"/>
  {label(440, 100, "HARDNESS TAX ON BITS & JOINTS", 12)}
""",
    )
    add(
        "04-25-oak-outdoors",
        "White oak versus red oak outdoors",
        "Tyloses in white oak heartwood schematic.",
        f"""
  <rect x="200" y="200" width="200" height="140" fill="{WOOD}" stroke="{INK}"/>
  {label(300, 360, "white oak (tyloses)", 10)}
  <rect x="480" y="200" width="200" height="140" fill="{WOOD}" stroke="{INK}" opacity="0.6"/>
  <path d="M500,240 L660,280" stroke="{WATER}" stroke-width="2"/>
  {label(580, 360, "red oak (open)", 10)}
  {label(440, 90, "DINING OAK ≠ PATIO OAK", 12)}
""",
    )
    add(
        "04-26-pressure-treated",
        "Pressure-treated lumber cylinder",
        "Wood in treatment cylinder with chemical note.",
        f"""
  <rect x="360" y="120" width="160" height="280" rx="20" fill="none" stroke="{INK}" stroke-width="3"/>
  <rect x="380" y="200" width="120" height="160" fill="{WOOD}" stroke="{INK}"/>
  <path d="M440,140 L440,180" stroke="{WATER}" stroke-width="4"/>
  {label(440, 80, "PRESERVATIVE PROCESS — NOT A SPECIES", 11)}
""",
    )
    add(
        "04-27-joinery-rain",
        "Outdoor joint that sheds water",
        "Mortise shoulder shedding water versus trapped puddle.",
        f"""
  <path d="M280,300 L280,220 L400,220 L400,300 Z" fill="{WOOD}" stroke="{INK}"/>
  <path d="M480,300 L480,240 L600,240 L600,300 Z" fill="{WOOD}" stroke="{INK}"/>
  <ellipse cx="540" cy="270" rx="30" ry="12" fill="{WATER}" opacity="0.6"/>
  {label(340, 360, "sheds", 10)}
  {label(540, 360, "cistern", 10, fill=ACCENT)}
  {label(440, 90, "JOINTS MUST SHED OR MOVE", 12)}
""",
    )
    add(
        "05-28-cast-iron-foundry",
        "Cast iron garden seat weight",
        "Heavy cast legs and brittle snap risk.",
        f"""
  <rect x="300" y="200" width="280" height="20" fill="{METAL}" stroke="{INK}"/>
  <rect x="320" y="220" width="20" height="140" fill="{METAL}" stroke="{INK}"/>
  <rect x="540" y="220" width="20" height="140" fill="{METAL}" stroke="{INK}"/>
  {label(440, 80, "POURED · HEAVY · BRITTLE", 13)}
""",
    )
    add(
        "05-29-wrought-vs-steel",
        "Wrought iron name on mild steel",
        "Scroll form with material label correction.",
        f"""
  <path d="M300,320 Q340,200 400,280 Q460,360 520,240" fill="none" stroke="{METAL}" stroke-width="4"/>
  {label(300, 360, "scroll (same)", 10, "start")}
  {label(620, 280, "historic wrought", 10, "start")}
  {label(620, 320, "modern mild steel", 10, "start")}
  {label(440, 80, "GRANDMOTHER'S NAME ON A COUSIN", 11)}
""",
    )
    add(
        "05-30-aluminum-light",
        "Aluminum frame lightness and wind",
        "Tubular aluminum chair blowing in wind arrow.",
        f"""
  <polyline points="360,320 400,220 440,320 480,220 520,320" fill="none" stroke="{METAL}" stroke-width="4"/>
  <path d="M600,260 L720,260" stroke="{ACCENT}" stroke-width="2"/>
  <polygon points="720,260 700,250 700,270" fill="{ACCENT}"/>
  {label(440, 80, "LIGHT MEANS WIND & STACKING COUNT", 11)}
""",
    )
    add(
        "05-31-powder-coat",
        "Powder coat film on metal",
        "Chip in baked film exposing metal underneath.",
        f"""
  <rect x="280" y="200" width="320" height="120" fill="{METAL}" stroke="{INK}"/>
  <rect x="280" y="200" width="320" height="120" fill="#fbbf24" opacity="0.35"/>
  <path d="M420,240 L460,280 L400,300 Z" fill="{BG}" stroke="{ACCENT}" stroke-width="2"/>
  {label(440, 80, "FILM CHIPS — METAL IS THE SPEC", 12)}
""",
    )
    add(
        "06-32-rattan-vine",
        "Rattan climbing palm pole",
        "Vine pole cross-section thirsty in weather.",
        f"""
  <path d="M440,120 Q400,220 440,320 Q480,420 440,420" fill="none" stroke="{GREEN}" stroke-width="6"/>
  <circle cx="440" cy="260" r="40" fill="{WOOD}" stroke="{INK}"/>
  {label(440, 80, "VINE — NOT A STYLE", 13)}
""",
    )
    add(
        "06-33-wicker-method",
        "Wicker weaving method",
        "Weave around a frame regardless of fiber.",
        f"""
  <rect x="340" y="200" width="200" height="120" fill="none" stroke="{INK}" stroke-width="2"/>
  <path d="M340,220 h200 M340,260 h200 M340,300 h200" stroke="{ACCENT}" stroke-width="2"/>
  <path d="M360,200 v120 M400,200 v120 M440,200 v120 M480,200 v120 M520,200 v120" stroke="{ACCENT}" stroke-width="2"/>
  {label(440, 80, "METHOD — FRAME + FIBER", 12)}
""",
    )
    add(
        "06-34-all-weather-weave",
        "Resin wicker on aluminum frame",
        "Extruded polymer weave on outdoor frame.",
        f"""
  <rect x="320" y="240" width="240" height="80" fill="none" stroke="{METAL}" stroke-width="3"/>
  <ellipse cx="380" cy="280" rx="30" ry="15" fill="none" stroke="#94a3b8" stroke-width="3"/>
  <ellipse cx="440" cy="280" rx="30" ry="15" fill="none" stroke="#94a3b8" stroke-width="3"/>
  <ellipse cx="500" cy="280" rx="30" ry="15" fill="none" stroke="#94a3b8" stroke-width="3"/>
  {label(440, 80, "PLASTIC WITH A MEMORY OF RATTAN", 11)}
""",
    )
    add(
        "06-35-lloyd-loom",
        "Lloyd Loom paper on wire",
        "Regular woven paper sheet on wire grid.",
        f"""
  <line x1="280" y1="200" x2="600" y2="200" stroke="{MUTED}"/>
  <line x1="280" y1="240" x2="600" y2="240" stroke="{MUTED}"/>
  <line x1="280" y1="280" x2="600" y2="280" stroke="{MUTED}"/>
  <line x1="320" y1="160" x2="320" y2="320" stroke="{MUTED}"/>
  <line x1="400" y1="160" x2="400" y2="320" stroke="{MUTED}"/>
  <line x1="480" y1="160" x2="480" y2="320" stroke="{MUTED}"/>
  <line x1="560" y1="160" x2="560" y2="320" stroke="{MUTED}"/>
  {label(440, 80, "PAPER ON WIRE — REGULARITY IS THE TELL", 11)}
""",
    )
    add(
        "07-36-stone-cold-sit",
        "Stone bench thermal honesty",
        "Heavy stone slab bench.",
        f"""
  <rect x="280" y="260" width="320" height="40" fill="#d1d5db" stroke="{INK}"/>
  <rect x="300" y="300" width="40" height="80" fill="#9ca3af" stroke="{INK}"/>
  <rect x="540" y="300" width="40" height="80" fill="#9ca3af" stroke="{INK}"/>
  {label(440, 80, "COLD SIT YOU CAN LEAVE OUT", 12)}
""",
    )
    add(
        "07-37-concrete",
        "Concrete bench spall risk",
        "Concrete seat with hairline crack and rebar hint.",
        f"""
  <rect x="300" y="240" width="280" height="60" fill="#d1d5db" stroke="{INK}"/>
  <path d="M360,270 L420,290" stroke="{ACCENT}" stroke-width="2"/>
  <circle cx="500" cy="270" r="6" fill="#b45309"/>
  {label(440, 80, "MIX · REINFORCEMENT · FREEZE", 12)}
""",
    )
    add(
        "07-38-sling-mesh",
        "Sling seat drainage",
        "Fabric sling draining between frame rails.",
        f"""
  <line x1="300" y1="200" x2="300" y2="360" stroke="{METAL}" stroke-width="4"/>
  <line x1="580" y1="200" x2="580" y2="360" stroke="{METAL}" stroke-width="4"/>
  <path d="M300,220 Q440,320 580,220" fill="none" stroke="#0ea5e9" stroke-width="3"/>
  <path d="M420,300 L420,340" stroke="{WATER}" stroke-width="2"/>
  {label(440, 80, "REFUSES TO HOLD A PUDDLE", 12)}
""",
    )
    add(
        "07-39-cushions-not-furniture",
        "Outdoor cushion zippered package",
        "Foam cushion as replaceable weather argument.",
        f"""
  <rect x="320" y="220" width="240" height="100" rx="12" fill="#fbbf24" stroke="{INK}" opacity="0.5"/>
  <line x1="340" y1="240" x2="540" y2="240" stroke="{INK}" stroke-dasharray="4 3"/>
  {label(440, 235, "zipper", 9)}
  <rect x="360" y="340" width="160" height="40" fill="#e2e8f0" stroke="{INK}"/>
  {label(440, 80, "CUSHION ≠ FRAME", 13)}
""",
    )
    add(
        "08-40-fasteners-rust-first",
        "Outdoor fastener galvanic pairs",
        "Screw rust at joint before board fails.",
        f"""
  <rect x="300" y="240" width="280" height="40" fill="{WOOD}" stroke="{INK}"/>
  <circle cx="360" cy="260" r="10" fill="{METAL}" stroke="{ACCENT}" stroke-width="2"/>
  <circle cx="440" cy="260" r="10" fill="#b45309" stroke="{INK}"/>
  <circle cx="520" cy="260" r="10" fill="{METAL}" stroke="{ACCENT}" stroke-width="2"/>
  {label(440, 80, "FASTENER RUSTS FIRST", 13)}
""",
    )
    add(
        "08-41-finish-die-public",
        "Outdoor finish failure modes",
        "Chalk, peel, and silver paths on wood.",
        f"""
  <rect x="200" y="220" width="160" height="120" fill="{WOOD}" stroke="{INK}"/>
  <rect x="400" y="220" width="160" height="120" fill="#e5e7eb" stroke="{INK}"/>
  <path d="M400,220 L560,340" fill="none" stroke="{ACCENT}" stroke-width="2"/>
  <rect x="600" y="220" width="80" height="120" fill="{WOOD}" stroke="{INK}" opacity="0.5"/>
  {label(440, 80, "PICK AN HONEST DEATH", 12)}
""",
    )
    add(
        "08-42-winter-brief",
        "Winter storage for outdoor furniture",
        "Stacked chairs under cover in shed.",
        f"""
  <rect x="260" y="160" width="360" height="240" fill="#f1f5f9" stroke="{INK}"/>
  <polygon points="240,160 440,100 640,160" fill="#e2e8f0" stroke="{INK}"/>
  <rect x="340" y="280" width="80" height="6" fill="{METAL}" stroke="{INK}"/>
  <rect x="360" y="270" width="80" height="6" fill="{METAL}" stroke="{INK}"/>
  {label(440, 80, "DRAW JANUARY IN SEPTEMBER", 12)}
""",
    )
    add(
        "08-43-read-the-patio",
        "Site walk before specifying patio set",
        "Plan view: sun, roof, path, storage.",
        f"""
  <rect x="280" y="200" width="320" height="200" fill="#cbd5e1" stroke="{INK}"/>
  <circle cx="600" cy="160" r="40" fill="{ACCENT}" opacity="0.4"/>
  {label(600, 160, "sun", 9)}
  <rect x="120" y="220" width="120" height="160" fill="#e2e8f0" stroke="{INK}"/>
  {label(180, 210, "storage", 9)}
  <path d="M200,400 L280,300" stroke="{MUTED}" stroke-width="2" stroke-dasharray="5 4"/>
  {label(440, 80, "WALK ROOF · SUN · WATER · PATH", 11)}
""",
    )
    add(
        "08-44-bbf-collections-adjacent",
        "BBF indoor collections beside outdoor history",
        "Indoor dining table adjacent to outdoor teaching map.",
        f"""
  <rect x="160" y="240" width="240" height="100" fill="{WOOD}" stroke="{INK}"/>
  {label(280, 230, "BBF indoor collections", 10)}
  <rect x="480" y="200" width="240" height="160" fill="#fff7ed" stroke="{ACCENT}"/>
  {label(600, 190, "outdoor history (adjacent)", 10)}
  <path d="M400,290 L480,290" stroke="{INK}" stroke-width="1.5"/>
  {label(440, 80, "SHARED DUTIES — NOT INVENTED PATIO SKUs", 11)}
""",
    )


def write_files() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    SHARED.mkdir(parents=True, exist_ok=True)
    (SHARED / "series-featured.svg").write_text(featured(), encoding="utf-8")
    for stem, (title, desc, body) in DIAGRAMS.items():
        path = OUT / f"{stem}.svg"
        path.write_text(wrap(title, desc, body), encoding="utf-8")
    print(f"wrote {len(DIAGRAMS)} diagrams + series-featured.svg")


def main() -> None:
    build_all()
    write_files()


if __name__ == "__main__":
    main()
