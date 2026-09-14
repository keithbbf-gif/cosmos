#!/usr/bin/env python3
"""Insert round-1 <figure> blocks into drafts (idempotent)."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DRAFTS = ROOT / "drafts"

# alt + caption body (credit appended from license map)
SPECS: dict[str, dict[str, str]] = {
    "00-01-furniture-problem.md": {
        "asset": "met-cellaret-cabinet.jpg",
        "w": "1920",
        "h": "2400",
        "alt": "Mahogany cellaret cabinet with brass mounts photographed on a neutral museum background",
        "caption": "A Metropolitan Museum cellaret: the episode’s point is casework duty, not lifestyle styling.",
        "credit": "Metropolitan Museum of Art / <a href=\"https://creativecommons.org/publicdomain/zero/1.0/\">CC0</a> (Wikimedia Commons).",
    },
    "00-02-three-objects.md": {
        "asset": "cleveland-sideboard-cellarette.jpg",
        "w": "1920",
        "h": "1287",
        "alt": "Federal sideboard with matching cellarette in a museum gallery",
        "caption": "Sideboard and cellarette were often sold as one dining-room machine—two objects, one assignment.",
        "credit": "Cleveland Museum of Art / <a href=\"https://creativecommons.org/publicdomain/zero/1.0/\">CC0</a> (Wikimedia Commons).",
    },
    "00-03-who-is-talking.md": {
        "asset": "met-sideboard.jpg",
        "w": "1920",
        "h": "1245",
        "alt": "Early nineteenth-century American sideboard with drawers and cupboard doors",
        "caption": "Museum furniture we can name on camera: industry history with a catalog number, not a shop legend.",
        "credit": "Metropolitan Museum of Art / <a href=\"https://creativecommons.org/publicdomain/zero/1.0/\">CC0</a> (Wikimedia Commons).",
    },
    "00-04-stolen-words.md": {
        "asset": "butler-pantry-garfield.jpg",
        "w": "1920",
        "h": "1280",
        "alt": "Historic butler's pantry with sink, cabinets, and pass-through to dining service",
        "caption": "A butler’s pantry was a wet workroom—vocabulary matters before you call a cocktail wall a pantry.",
        "credit": "BC in Arizona / <a href=\"https://commons.wikimedia.org/wiki/File:Butler_pantry_-_Lawnfield_-_Garfield_House_Historic_Site_(30687623511).jpg\">CC BY-SA 2.0</a> (Wikimedia Commons).",
    },
    "01-05-little-cellars.md": {
        "asset": "met-cellaret-duncan-phyfe.jpg",
        "w": "1920",
        "h": "1593",
        "alt": "Duncan Phyfe style cellaret with brass banding on a museum pedestal",
        "caption": "The cellarette brought the cellar upstairs: a little box with rings for servants and partitions for bottles.",
        "credit": "Metropolitan Museum of Art / <a href=\"https://creativecommons.org/publicdomain/zero/1.0/\">CC0</a> (Wikimedia Commons).",
    },
    "01-06-cisterns-liners.md": {
        "asset": "met-wine-bottle-cooler.jpg",
        "w": "1920",
        "h": "1921",
        "alt": "Porcelain wine bottle cooler with gilt decoration in a museum display",
        "caption": "Historic coolers are wood or metal cases around a wet liner—here the liner is the lesson.",
        "credit": "Metropolitan Museum of Art / <a href=\"https://creativecommons.org/publicdomain/zero/1.0/\">CC0</a> (Wikimedia Commons).",
    },
    "01-07-adam-pedestals.md": {
        "asset": "otis-house-dining-room.jpg",
        "w": "1920",
        "h": "1378",
        "alt": "Federal era dining room with sideboard niche and classical woodwork",
        "caption": "Adam-era dining rooms hid storage in architecture—pedestals and urns before the fitted sideboard condensed the set.",
        "credit": "HABS / Library of Congress / <a href=\"https://commons.wikimedia.org/wiki/File:DINING_ROOM,_GENERAL_VIEW_-_Harrison_Gray_Otis_House_(second),_85_Mount_Vernon_Street,_Boston,_Suffolk_County,_MA_HABS_MASS,13-BOST,114-8.tif\">public domain</a> (Wikimedia Commons).",
    },
    "01-08-hepplewhite-sheraton.md": {
        "asset": "hepplewhite-sideboard-cape-ann.jpg",
        "w": "1920",
        "h": "1249",
        "alt": "Hepplewhite mahogany sideboard with inlay in a museum gallery",
        "caption": "Hepplewhite and Sheraton turned bottle wells and partitions into publishable drawings shops could repeat.",
        "credit": "Daderot / <a href=\"https://commons.wikimedia.org/wiki/File:Hepplewhite_sideboard,_North_Shore,_Massachusetts,_c._1790,_mahogany,_inlay_-_Cape_Ann_Museum_-_Gloucester,_MA_-_DSC01257.jpg\">public domain</a> (Wikimedia Commons).",
    },
    "01-09-sarcophagus.md": {
        "asset": "met-wine-cooler-with-bottle.jpg",
        "w": "1920",
        "h": "2618",
        "alt": "Neoclassical wine cooler shaped like an urn with a bottle in place",
        "caption": "The sarcophagus and urn silhouettes dressed utility as antiquity—fashion, not a secret code.",
        "credit": "Metropolitan Museum of Art / <a href=\"https://creativecommons.org/publicdomain/zero/1.0/\">CC0</a> (Wikimedia Commons).",
    },
    "01-10-locks-keys.md": {
        "asset": "prohibition-speakeasy-door.jpg",
        "w": "1920",
        "h": "2560",
        "alt": "Heavy wooden door with speakeasy slot and lock hardware in a museum display",
        "caption": "Locks on drink furniture controlled access—later concealment made the same habit louder.",
        "credit": "Myotus / <a href=\"https://commons.wikimedia.org/wiki/File:Speakeasy_door,_American_Prohibition_Museum-011.jpg\">CC BY 4.0</a> (Wikimedia Commons).",
    },
    "02-11-american-performance.md": {
        "asset": "victorian-dining-room-delaware.jpg",
        "w": "1920",
        "h": "1440",
        "alt": "Victorian dining room with table, sideboard, and patterned wall coverings",
        "caption": "The nineteenth-century dining room performed wealth—the sideboard and cooler are part of the set.",
        "credit": "National Park Service / <a href=\"https://commons.wikimedia.org/wiki/File:The_Dining_Room_at_219_North_Delaware_Street,_Another_View_(a12f94fc-1474-4d8e-bffb-de52f25bbd26).jpg\">public domain</a> (Wikimedia Commons).",
    },
    "02-12-sargent-dinner-party.md": {
        "asset": "henry-sargent-dinner-party.jpg",
        "w": "1280",
        "h": "1593",
        "alt": "Henry Sargent oil painting of a gentlemen's dinner with wine cooler at the table",
        "caption": "Sargent’s 1821 <em>Dinner Party</em> (MFA Boston acc. 19.13) keeps the cellarette at work—not as decoration.",
        "credit": "Henry Sargent / <a href=\"https://commons.wikimedia.org/wiki/File:Henry_Sargent_-_The_Dinner_Party_-_19.13_-_Museum_of_Fine_Arts.jpg\">public domain</a> (Wikimedia Commons).",
    },
    "02-13-regional-cellarettes.md": {
        "asset": "dayton-american-sideboard-1810.jpg",
        "w": "1920",
        "h": "1361",
        "alt": "American Federal sideboard in mahogany with tapered legs",
        "caption": "Regional American sideboards share a vocabulary—Boston, New York, Charleston—without pretending one shop made them all.",
        "credit": "Dayton Art Institute / <a href=\"https://creativecommons.org/publicdomain/zero/1.0/\">CC0</a> (Wikimedia Commons).",
    },
    "02-14-sideboard-stage.md": {
        "asset": "met-sideboard.jpg",
        "w": "1920",
        "h": "1245",
        "alt": "Sideboard with drawers and cupboard doors staged in a museum photo",
        "caption": "The sideboard is the dining room’s stage left—bottles, glass, and silver traffic through it.",
        "credit": "Metropolitan Museum of Art / <a href=\"https://creativecommons.org/publicdomain/zero/1.0/\">CC0</a> (Wikimedia Commons).",
    },
    "02-15-victorian-mass.md": {
        "asset": "victorian-dining-room-delaware.jpg",
        "w": "1920",
        "h": "1440",
        "alt": "Ornate Victorian dining room interior with heavy furniture mass",
        "caption": "Victorian mass changed scale—coolers and sideboards grew with the room they served.",
        "credit": "National Park Service / <a href=\"https://commons.wikimedia.org/wiki/File:The_Dining_Room_at_219_North_Delaware_Street,_Another_View_(a12f94fc-1474-4d8e-bffb-de52f25bbd26).jpg\">public domain</a> (Wikimedia Commons).",
    },
    "02-16-butlers-pantry.md": {
        "asset": "butler-pantry-garfield.jpg",
        "w": "1920",
        "h": "1280",
        "alt": "Butler's pantry counters and cabinets between kitchen and dining service",
        "caption": "The butler’s pantry is service infrastructure—sink, china, glass—not a cocktail stage.",
        "credit": "BC in Arizona / <a href=\"https://commons.wikimedia.org/wiki/File:Butler_pantry_-_Lawnfield_-_Garfield_House_Historic_Site_(30687623511).jpg\">CC BY-SA 2.0</a> (Wikimedia Commons).",
    },
    "03-17-lockable-before.md": {
        "asset": "prohibition-speakeasy-door.jpg",
        "w": "1920",
        "h": "2560",
        "alt": "Locked speakeasy-style door with viewing slot in a museum exhibit",
        "caption": "Lockable drink storage predates Prohibition—the brief made concealment fashionable, not invented.",
        "credit": "Myotus / <a href=\"https://commons.wikimedia.org/wiki/File:Speakeasy_door,_American_Prohibition_Museum-011.jpg\">CC BY 4.0</a> (Wikimedia Commons).",
    },
    "03-18-prohibition-brief.md": {
        "asset": "prohibition-speakeasy-door.jpg",
        "w": "1920",
        "h": "2560",
        "alt": "Prohibition museum display of a speakeasy entrance door",
        "caption": "1920–1933 is a dated legal brief—furniture responded, but do not claim every bookcase hid bottles.",
        "credit": "Myotus / <a href=\"https://commons.wikimedia.org/wiki/File:Speakeasy_door,_American_Prohibition_Museum-011.jpg\">CC BY 4.0</a> (Wikimedia Commons).",
    },
    "03-19-innocent-furniture.md": {
        "asset": "otis-house-dining-room.jpg",
        "w": "1920",
        "h": "1378",
        "alt": "Federal dining room interior with built-in sideboard niche",
        "caption": "Respectable dining rooms already had drink furniture—the concealment era re-read the same objects.",
        "credit": "HABS / Library of Congress / <a href=\"https://commons.wikimedia.org/wiki/File:DINING_ROOM,_GENERAL_VIEW_-_Harrison_Gray_Otis_House_(second),_85_Mount_Vernon_Street,_Boston,_Suffolk_County,_MA_HABS_MASS,13-BOST,114-8.tif\">public domain</a> (Wikimedia Commons).",
    },
    "03-20-art-deco-cabinet.md": {
        "asset": "absinthe-house-back-bar.jpg",
        "w": "1920",
        "h": "1440",
        "alt": "Ornate mirrored back bar with wood cabinetry in a historic New Orleans barroom",
        "caption": "Art Deco cocktail cabinets borrowed commercial bar language—mirrors, lacquer, fitted interiors.",
        "credit": "Bmaurizi / <a href=\"https://commons.wikimedia.org/wiki/File:Absinthe_House_Back_Barroom_Espresso_Machine_Clock.JPG\">CC BY-SA 3.0</a> (Wikimedia Commons).",
    },
    "03-21-repeal-homework.md": {
        "asset": "four-seasons-serving-cart.jpg",
        "w": "640",
        "h": "480",
        "alt": "Restaurant serving cart with glass and bottles staged for table service",
        "caption": "After repeal, home mixing needed homework—mobile carts and fitted cases answered the same brief.",
        "credit": "Terry Fox Baum / <a href=\"https://commons.wikimedia.org/wiki/File:The_Four_Seasons_Serving_Cart_03.JPG\">CC BY-SA 4.0</a> (Wikimedia Commons).",
    },
    "04-22-fitted-machine.md": {
        "asset": "absinthe-house-back-bar.jpg",
        "w": "1920",
        "h": "1440",
        "alt": "Back bar cabinetry with mirror and shelving for bottles and glass",
        "caption": "A fitted bar is a machine with a face—racks, mirrors, and landing zones in fixed order.",
        "credit": "Bmaurizi / <a href=\"https://commons.wikimedia.org/wiki/File:Absinthe_House_Back_Barroom_Espresso_Machine_Clock.JPG\">CC BY-SA 3.0</a> (Wikimedia Commons).",
    },
    "04-23-bar-cart.md": {
        "asset": "four-seasons-serving-cart.jpg",
        "w": "640",
        "h": "480",
        "alt": "Silver service cart used for dining room beverage service",
        "caption": "The bar cart is the hospitality piece that stayed mobile—hotels first, houses later.",
        "credit": "Terry Fox Baum / <a href=\"https://commons.wikimedia.org/wiki/File:The_Four_Seasons_Serving_Cart_03.JPG\">CC BY-SA 4.0</a> (Wikimedia Commons).",
    },
    "04-24-credenza-bars.md": {
        "asset": "met-sideboard.jpg",
        "w": "1920",
        "h": "1245",
        "alt": "Low dining storage piece with doors hiding interior bottle storage",
        "caption": "Mid-century credenza bars are sideboards with a job change—bottles behind doors, sometimes a drop front.",
        "credit": "Metropolitan Museum of Art / <a href=\"https://creativecommons.org/publicdomain/zero/1.0/\">CC0</a> (Wikimedia Commons).",
    },
    "04-25-rec-room-wet-bar.md": {
        "asset": "kitchen-standing-1973.jpg",
        "w": "1920",
        "h": "2549",
        "alt": "1970s kitchen interior with wood cabinets and standing figures",
        "caption": "Suburban wet bars often lived next to rec rooms—plumbing, paneling, and a counter, not only a cabinet.",
        "credit": "Infrogmation family photos / <a href=\"https://commons.wikimedia.org/wiki/File:Standing_in_the_Kitchen,_1973.jpg\">CC BY-SA 4.0</a> (Wikimedia Commons).",
    },
    "04-26-paneled-dens.md": {
        "asset": "kitchen-standing-1973.jpg",
        "w": "1920",
        "h": "2549",
        "alt": "Wood-paneled kitchen cabinets in a 1970s home interior photograph",
        "caption": "Paneled dens and basement bars share a period flavor—dark wood, low light, fixed counters.",
        "credit": "Infrogmation family photos / <a href=\"https://commons.wikimedia.org/wiki/File:Standing_in_the_Kitchen,_1973.jpg\">CC BY-SA 4.0</a> (Wikimedia Commons).",
    },
    "04-27-hotel-brass.md": {
        "asset": "sazerac-bar-mirror-nola.jpg",
        "w": "1920",
        "h": "1440",
        "alt": "Hotel bar mirror and brass rail above a wooden bar top in New Orleans",
        "caption": "Hotel brass and mirrored back bars leak into houses—restaurant parts, not cellarette DNA.",
        "credit": "Infrogmation of New Orleans / <a href=\"https://commons.wikimedia.org/wiki/File:SazeracBarMirrorJuly2009NOLA.JPG\">CC BY-SA 3.0</a> (Wikimedia Commons).",
    },
    "05-28-furniture-vs-builtin.md": {
        "asset": "hearst-castle-kitchen-builtins.jpg",
        "w": "1920",
        "h": "1272",
        "alt": "Built-in kitchen refrigerator and matching cabinetry in a historic estate kitchen",
        "caption": "Built-ins are scribed to the room—unfinished backs and site joints furniture does not carry.",
        "credit": "Scott Dexter / <a href=\"https://commons.wikimedia.org/wiki/File:Kitchen_Refrigerator_Cupboards_Counters_-_Hearst_Castle_South_Wing.jpg\">CC BY-SA 2.0</a> (Wikimedia Commons).",
    },
    "05-29-wet-bar-plumbing.md": {
        "asset": "gfci-outlet.jpg",
        "w": "1920",
        "h": "1336",
        "alt": "Ground-fault circuit interrupter electrical outlet on a wall plate",
        "caption": "Wet bars touch code—GFCI protection is the photograph, not a furniture finish schedule.",
        "credit": "Tony Webster / <a href=\"https://commons.wikimedia.org/wiki/File:Ground_Fault_Circuit_Interrupter_(GFCI)_Electrical_Outlet_(29268945818).jpg\">CC BY 2.0</a> (Wikimedia Commons).",
    },
    "05-30-honest-dry.md": {
        "asset": "met-cellaret-cabinet.jpg",
        "w": "1920",
        "h": "2400",
        "alt": "Closed cellaret cabinet without sink or plumbing connections",
        "caption": "An honest dry bar is storage and landing space—no pretend sink, no stolen wet vocabulary.",
        "credit": "Metropolitan Museum of Art / <a href=\"https://creativecommons.org/publicdomain/zero/1.0/\">CC0</a> (Wikimedia Commons).",
    },
    "05-31-pantry-revival.md": {
        "asset": "butler-pantry-garfield.jpg",
        "w": "1920",
        "h": "1280",
        "alt": "Historic butler's pantry with sink and upper cabinets",
        "caption": "Today’s pantry revival often wants display; the historic pantry wanted throughput.",
        "credit": "BC in Arizona / <a href=\"https://commons.wikimedia.org/wiki/File:Butler_pantry_-_Lawnfield_-_Garfield_House_Historic_Site_(30687623511).jpg\">CC BY-SA 2.0</a> (Wikimedia Commons).",
    },
    "05-32-kitchen-adjacent.md": {
        "asset": "efta-kitchen-wine-rack.jpg",
        "w": "768",
        "h": "1152",
        "alt": "Residential kitchen with wall-mounted wine rack and adjacent appliances",
        "caption": "Kitchen-adjacent bars share traffic with cooking—storage height and landing space matter.",
        "credit": "U.S. federal exhibit photo / <a href=\"https://commons.wikimedia.org/wiki/File:EFTA00001443_-_Kitchen_with_cream_cabinets_a_white_refrigerator_a_blue_carpet_and_stainless_steel_appliances_featuring_a_glass_cart_and_a_wine_rack_on_the_wall.jpg\">public domain</a> (Wikimedia Commons).",
    },
    "05-33-contemporary-millwork.md": {
        "asset": "hearst-castle-kitchen-builtins.jpg",
        "w": "1920",
        "h": "1272",
        "alt": "Large-scale fitted kitchen casework with integrated refrigeration",
        "caption": "Contemporary millwork bars are rooms in plywood—panels, fillers, and MEP coordination.",
        "credit": "Scott Dexter / <a href=\"https://commons.wikimedia.org/wiki/File:Kitchen_Refrigerator_Cupboards_Counters_-_Hearst_Castle_South_Wing.jpg\">CC BY-SA 2.0</a> (Wikimedia Commons).",
    },
    "06-34-bottle-geometry.md": {
        "asset": "schematic-bottle-clearances.svg",
        "w": "720",
        "h": "420",
        "alt": "Diagram of typical 750 milliliter bottle height and diameter clearances inside a cabinet bay",
        "caption": "Measure the client’s bottles—standard 750 ml heights and diameters are a starting point, not a mood board.",
        "credit": "Diagram: original to this pack / <a href=\"https://creativecommons.org/publicdomain/zero/1.0/\">CC0</a>.",
    },
    "06-35-glassware-rattle.md": {
        "asset": "efta-kitchen-wine-rack.jpg",
        "w": "768",
        "h": "1152",
        "alt": "Kitchen wall wine rack holding bottles near glassware storage",
        "caption": "Glass rattles when the carcase is thin—hanging stems steal headroom you still need for bottles.",
        "credit": "U.S. federal exhibit photo / <a href=\"https://commons.wikimedia.org/wiki/File:EFTA00001443_-_Kitchen_with_cream_cabinets_a_white_refrigerator_a_blue_carpet_and_stainless_steel_appliances_featuring_a_glass_cart_and_a_wine_rack_on_the_wall.jpg\">public domain</a> (Wikimedia Commons).",
    },
    "06-36-light-without-cooking.md": {
        "asset": "met-cellaret-cabinet.jpg",
        "w": "1920",
        "h": "2400",
        "alt": "Closed liquor cabinet case photographed in museum lighting",
        "caption": "Interior lights heat a void—LED is habit; halogen is how you cook a label.",
        "credit": "Metropolitan Museum of Art / <a href=\"https://creativecommons.org/publicdomain/zero/1.0/\">CC0</a> (Wikimedia Commons).",
    },
    "06-37-hardware-ghost.md": {
        "asset": "met-cellaret-duncan-phyfe.jpg",
        "w": "1920",
        "h": "1593",
        "alt": "Brass hardware and banding on a historic cellaret",
        "caption": "Hardware is the ghost of the hand—rings, locks, and hinges outlive the party.",
        "credit": "Metropolitan Museum of Art / <a href=\"https://creativecommons.org/publicdomain/zero/1.0/\">CC0</a> (Wikimedia Commons).",
    },
    "06-38-finish-climate.md": {
        "asset": "met-sideboard.jpg",
        "w": "1920",
        "h": "1245",
        "alt": "Historic dining sideboard finish and wood figure in museum light",
        "caption": "Alcohol, citrus, and water attack film finishes—climate is a maintenance schedule, not a vibe.",
        "credit": "Metropolitan Museum of Art / <a href=\"https://creativecommons.org/publicdomain/zero/1.0/\">CC0</a> (Wikimedia Commons).",
    },
    "06-39-tops-wet-line.md": {
        "asset": "met-wine-cooler-with-bottle.jpg",
        "w": "1920",
        "h": "2618",
        "alt": "Wine cooler with bottle showing the wet line at the top of the liner",
        "caption": "Stone and wood tops need an honest wet line—rings are physics, not betrayal.",
        "credit": "Metropolitan Museum of Art / <a href=\"https://creativecommons.org/publicdomain/zero/1.0/\">CC0</a> (Wikimedia Commons).",
    },
    "06-40-cold-machine.md": {
        "asset": "hearst-castle-kitchen-builtins.jpg",
        "w": "1920",
        "h": "1272",
        "alt": "Integrated refrigerator surrounded by matching kitchen cabinetry",
        "caption": "Undercounter refrigeration is a ventilated appliance, not a drawer box—read the cut sheet.",
        "credit": "Scott Dexter / <a href=\"https://commons.wikimedia.org/wiki/File:Kitchen_Refrigerator_Cupboards_Counters_-_Hearst_Castle_South_Wing.jpg\">CC BY-SA 2.0</a> (Wikimedia Commons).",
    },
    "06-41-closed-climate.md": {
        "asset": "met-wine-bottle-cooler.jpg",
        "w": "1920",
        "h": "1921",
        "alt": "Enclosed porcelain wine cooler vessel in a museum case",
        "caption": "Closed volumes trap heat and light—wine cares more than most spirits, but neither likes a sauna.",
        "credit": "Metropolitan Museum of Art / <a href=\"https://creativecommons.org/publicdomain/zero/1.0/\">CC0</a> (Wikimedia Commons).",
    },
    "06-42-trucks-vs-scribes.md": {
        "asset": "cleveland-sideboard-cellarette.jpg",
        "w": "1920",
        "h": "1287",
        "alt": "Movable sideboard and cellarette ensemble in a museum setting",
        "caption": "Furniture leaves on trucks; built-ins leave only when the house does.",
        "credit": "Cleveland Museum of Art / <a href=\"https://creativecommons.org/publicdomain/zero/1.0/\">CC0</a> (Wikimedia Commons).",
    },
    "06-43-codes-not-pretend.md": {
        "asset": "gfci-outlet.jpg",
        "w": "1920",
        "h": "1336",
        "alt": "GFCI protected electrical outlet required near wet locations",
        "caption": "Local code and licensed trades beat a furniture essay—GFCI is the easy photograph.",
        "credit": "Tony Webster / <a href=\"https://commons.wikimedia.org/wiki/File:Ground_Fault_Circuit_Interrupter_(GFCI)_Electrical_Outlet_(29268945818).jpg\">CC BY 2.0</a> (Wikimedia Commons).",
    },
    "07-44-read-the-room.md": {
        "asset": "otis-house-dining-room.jpg",
        "w": "1920",
        "h": "1378",
        "alt": "Historic dining room proportions with sideboard niche and windows",
        "caption": "Read the room before you draw a bar—architecture already decided where bottles may live.",
        "credit": "HABS / Library of Congress / <a href=\"https://commons.wikimedia.org/wiki/File:DINING_ROOM,_GENERAL_VIEW_-_Harrison_Gray_Otis_House_(second),_85_Mount_Vernon_Street,_Boston,_Suffolk_County,_MA_HABS_MASS,13-BOST,114-8.tif\">public domain</a> (Wikimedia Commons).",
    },
}


def figure_block(spec: dict[str, str]) -> str:
    return (
        "<figure>\n"
        f'  <img src="../assets/{spec["asset"]}" alt="{spec["alt"]}" '
        f'width="{spec["w"]}" height="{spec["h"]}" loading="lazy" decoding="async" />\n'
        f'  <figcaption>{spec["caption"]} {spec["credit"]}</figcaption>\n'
        "</figure>\n"
    )


def main() -> None:
    missing = []
    for name, spec in sorted(SPECS.items()):
        path = DRAFTS / name
        if not path.exists():
            missing.append(name)
            continue
        text = path.read_text(encoding="utf-8")
        if "<figure>" in text:
            continue
        m = re.match(r"(---\n.*?\n---\n\n)", text, re.DOTALL)
        if not m:
            raise SystemExit(f"no frontmatter: {name}")
        insert = m.group(1) + figure_block(spec) + "\n"
        path.write_text(insert + text[m.end() :], encoding="utf-8")
    if missing:
        raise SystemExit(f"missing drafts: {missing}")
    print(f"embedded figures in {len(SPECS)} drafts")


if __name__ == "__main__":
    main()
