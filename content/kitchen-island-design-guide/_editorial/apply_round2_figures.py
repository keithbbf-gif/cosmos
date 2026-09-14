#!/usr/bin/env python3
"""Insert round-2 <figure> blocks for drafts that missed round 1."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DRAFTS = ROOT / "drafts"

# draft filename -> (asset, width, height, alt, figcaption HTML body)
ROUND2: dict[str, tuple[str, int, int, str, str]] = {
    "13-length-people-and-prep.md": (
        "showroom-bar-stools-counter-height.jpg",
        1800,
        1200,
        "Showroom counter-height bar stools lined along a kitchen island display",
        "Stool spacing along a long island edge: the photograph is a layout reference, not a seat count for your room. Photo: Lionel Allorge / "
        '<a href="https://commons.wikimedia.org/wiki/File:Castorama_aux_Ulis_le_19_avril_2017_-_47.jpg">CC BY-SA 3.0</a> (Wikimedia Commons).',
    ),
    "14-triangle-intersection.md": (
        "schematic-work-zones.svg",
        900,
        520,
        "Schematic comparing classic work triangle paths with island obstruction zones",
        "When an island sits inside the old triangle legs, zones overlap — the schematic is planning geometry, not a code drawing. Line art: Bradley island design guide (CC0 1.0).",
    ),
    "15-landing-zones.md": (
        "kitchen-with-island-new-orleans-2007.jpg",
        1800,
        1197,
        "Kitchen island with clear landing space beside the cooktop run",
        "Landing zones are empty counter beside heat and water; this island shows finished aisles where landing can actually happen. Photo: MeRyan / "
        '<a href="https://commons.wikimedia.org/wiki/File:Kitchen_with_island,_New_Orleans_2007.jpg">CC BY 2.0</a> (Wikimedia Commons).',
    ),
    "16-two-cook-kitchens.md": (
        "open-plan-kitchen-corinda-queensland.jpg",
        1800,
        1200,
        "Open-plan kitchen and living room with circulation behind the island",
        "Two-cook kitchens need parallel aisles; open plans still punish a skinny path behind seating. Photo: Kgbo / "
        '<a href="https://commons.wikimedia.org/wiki/File:Open_plan_house;_kitchen_and_sitting_room_in_Corinda,_Queensland_01.jpg">CC BY-SA 4.0</a> (Wikimedia Commons).',
    ),
    "17-when-to-refuse-an-island.md": (
        "humble-kitchen-tight-layout.jpg",
        1800,
        1200,
        "Compact galley-style kitchen without room for a central island",
        "Some rooms should keep the table and skip the island — tight layouts are easier to read than a forced rectangle. Photo: Korman / "
        '<a href="https://commons.wikimedia.org/wiki/File:Humble_kitchen08.jpg">CC BY-SA 3.0</a> (Wikimedia Commons).',
    ),
    "20-woods-that-earn-the-top.md": (
        "end-grain-cutting-board.jpg",
        1800,
        1200,
        "Close view of end-grain hardwood butcher-block surface",
        "Species choice shows up in grain direction and hardness; end-grain tops trade weight for knife forgiveness. Photo: Hu Nhu / "
        '<a href="https://commons.wikimedia.org/wiki/File:End_grain_cutting_board.jpg">CC BY-SA 4.0</a> (Wikimedia Commons).',
    ),
    "22-wood-moves.md": (
        "mineral-oil-butcher-block.jpg",
        1200,
        900,
        "Mineral oil being applied to a butcher-block countertop",
        "Wood movement is managed with joinery and finish — oiling documents care, not a warranty against seasonal gap. Photo: Timtempleton / "
        '<a href="https://commons.wikimedia.org/wiki/File:Mineral_oil_treating_butcher_block.png">CC BY-SA 3.0</a> (Wikimedia Commons).',
    ),
    "27-mixed-tops.md": (
        "granite-countertop-slab-display.jpg",
        1800,
        1200,
        "Granite slab display beside contrasting stone samples at a countertop yard",
        "Mixed tops start at the yard: two stones means two support stories and two seam details on one island. Photo: Stilfehler / "
        '<a href="https://commons.wikimedia.org/wiki/File:Granite_for_Countertops_12.jpg">CC BY-SA 4.0</a> (Wikimedia Commons).',
    ),
    "28-weight-and-the-box.md": (
        "sektion-island-bracket-junction-box.jpg",
        1800,
        1200,
        "Island support bracket and electrical junction box under a stone overhang",
        "Weight lands in the box and brackets long before the stone shows stress — rough-in photos are structure, not decor. Photo: Stilfehler / "
        '<a href="https://commons.wikimedia.org/wiki/File:Sektion_Kitchen_Island_Support_Bracket_with_Junction_Box.jpg">CC BY-SA 4.0</a> (Wikimedia Commons).',
    ),
    "33-supporting-wood-overhang.md": (
        "schematic-overhang-knee-space.svg",
        900,
        520,
        "Schematic of wood island overhang with knee space and support limits",
        "Wood overhangs need corbels or steel before they flex; the schematic marks knee space, not a span table. Line art: Bradley island design guide (CC0 1.0).",
    ),
    "35-two-tier-islands.md": (
        "hamptons-style-kitchen-island.jpg",
        1800,
        1200,
        "Counter-height island with raised eating tier in a Hamptons-style kitchen",
        "Two-tier islands separate prep height from perch height — the raised tier is visible structure, not a second room. Photo: JessofWoodnCo / "
        '<a href="https://commons.wikimedia.org/wiki/File:Hamptons_Kitchen_Design_1.jpg">CC BY-SA 4.0</a> (Wikimedia Commons).',
    ),
    "36-when-seating-is-a-lie.md": (
        "showroom-bar-stools-counter-height.jpg",
        1800,
        1200,
        "Bar stools tucked under a display island with minimal knee clearance",
        "Showroom stools hide tight knee space — if the overhang is shallow, seating is a photo prop. Photo: Lionel Allorge / "
        '<a href="https://commons.wikimedia.org/wiki/File:Castorama_aux_Ulis_le_19_avril_2017_-_47.jpg">CC BY-SA 3.0</a> (Wikimedia Commons).',
    ),
    "38-future-provisions.md": (
        "popup-electrical-outlet-island.jpg",
        1800,
        1200,
        "Listed pop-up electrical outlet installed in a kitchen island countertop",
        "Future provisions mean conduit and box locations before stone — pop-ups are one listed finish, not the only legal path. Photo: Stilfehler / "
        '<a href="https://commons.wikimedia.org/wiki/File:US_Pop-up_Electrical_Outlet_3.jpg">CC BY-SA 4.0</a> (Wikimedia Commons).',
    ),
    "43-usb-and-what-belongs-below.md": (
        "gfci-electrical-outlet.jpg",
        1800,
        1200,
        "GFCI-protected electrical outlet on a kitchen backsplash",
        "USB ports belong in the electrical plan with GFCI protection — outlets are code objects, not drawer accessories. Photo: Tony Webster / "
        '<a href="https://commons.wikimedia.org/wiki/File:Ground_Fault_Circuit_Interrupter_(GFCI)_Electrical_Outlet_(29268945818).jpg">CC BY 2.0</a> (Wikimedia Commons).',
    ),
    "45-storage-that-isnt-junk.md": (
        "frameless-cabinet-toe-kick-u-kitchen.jpg",
        1800,
        1200,
        "Frameless cabinet boxes and toe-kick detail on a U-shaped kitchen run",
        "Useful island storage is box depth and drawer width — frameless boxes show real volume, not filler doors. Photo: Stilfehler / "
        '<a href="https://commons.wikimedia.org/wiki/File:F%C3%B6rb%C3%A4ttra_Toe_Kick_U-Kitchen.jpg">CC BY-SA 4.0</a> (Wikimedia Commons).',
    ),
    "46-spec-sheet-for-a-dealer.md": (
        "kitchen-tape-measure-prep.jpg",
        1800,
        1200,
        "Tape measure on a kitchen counter during layout prep",
        "Dealer spec sheets start with field dimensions — measure the room before you name a SKU. Photo: Shixart1985 / "
        '<a href="https://commons.wikimedia.org/wiki/File:Measuring_a_green_apple_beside_fresh_juice_in_a_bright_kitchen_setting_during_a_healthy_lifestyle_moment.jpg">CC BY 2.0</a> (Wikimedia Commons).',
    ),
    "48-aftercare.md": (
        "mineral-oil-butcher-block.jpg",
        1200,
        900,
        "Maintaining a butcher-block island top with food-safe mineral oil",
        "Aftercare for wood tops is re-oiling and honest expectations about scratches — not a one-time factory finish. Photo: Timtempleton / "
        '<a href="https://commons.wikimedia.org/wiki/File:Mineral_oil_treating_butcher_block.png">CC BY-SA 3.0</a> (Wikimedia Commons).',
    ),
}

FIG_RE = re.compile(r"<figure>.*?</figure>\s*", re.S)


def insert_figure(body: str, asset: str, w: int, h: int, alt: str, cap: str) -> str:
    block = (
        f'<figure>\n'
        f'  <img src="../assets/{asset}" alt="{alt}" width="{w}" height="{h}" loading="lazy" decoding="async" />\n'
        f"  <figcaption>{cap}</figcaption>\n"
        f"</figure>\n\n"
    )
    if "<figure>" in body:
        return body
    paras = body.split("\n\n", 1)
    if len(paras) == 1:
        return block + body
    return paras[0] + "\n\n" + block + paras[1]


def main() -> int:
    for name, spec in ROUND2.items():
        path = DRAFTS / name
        if not path.is_file():
            raise SystemExit(f"missing draft {name}")
        raw = path.read_text(encoding="utf-8")
        m = re.match(r"^(---\n.*?\n---\n)(.*)$", raw, re.S)
        if not m:
            raise SystemExit(f"no frontmatter: {name}")
        fm, body = m.group(1), m.group(2)
        asset, w, h, alt, cap = spec
        new_body = insert_figure(body.lstrip("\n"), asset, w, h, alt, cap)
        path.write_text(fm + new_body, encoding="utf-8")
        print("updated", name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
