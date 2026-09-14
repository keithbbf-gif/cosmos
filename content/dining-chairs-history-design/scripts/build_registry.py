#!/usr/bin/env python3
"""Emit assets/figures/REGISTRY.toml (museum + pack diagram plates)."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "figures" / "REGISTRY.toml"

# Strip utm_* from Commons URLs; verified 2026-09-14 via Wikimedia API.
PLATES: dict[str, dict] = {
    "met-hatnefer-chair": {
        "src": "https://upload.wikimedia.org/wikipedia/commons/8/8c/Hatnefer%27s_Chair_MET_DT2908.jpg",
        "width": 1200,
        "height": 960,
        "license": "CC0 1.0 (Met Open Access)",
        "institution": "The Metropolitan Museum of Art",
        "source_page": "https://commons.wikimedia.org/wiki/File:Hatnefer%27s_Chair_MET_DT2908.jpg",
        "credit": "Chair of Hatnefer, ca. 1492–1473 B.C.E.; Met 36.3.152 line.",
    },
    "met-reniseneb-chair": {
        "src": "https://upload.wikimedia.org/wikipedia/commons/a/af/Chair_of_Reniseneb_MET_DT536.jpg",
        "width": 1200,
        "height": 1500,
        "license": "CC0 1.0 (Met Open Access)",
        "institution": "The Metropolitan Museum of Art",
        "source_page": "https://commons.wikimedia.org/wiki/File:Chair_of_Reniseneb_MET_DT536.jpg",
        "credit": "Chair of Reniseneb; Met 68.58 line.",
    },
    "klismos-vase-mar": {
        "src": "https://upload.wikimedia.org/wikipedia/commons/3/3e/Woman_klismos_MAR_Palermo_NI2091.jpg",
        "width": 1200,
        "height": 1800,
        "license": "CC BY 2.5",
        "institution": "Museo Archeologico Regionale Antonio Salinas, Palermo",
        "source_page": "https://commons.wikimedia.org/wiki/File:Woman_klismos_MAR_Palermo_NI2091.jpg",
        "credit": "Red-figure vase with klismos chair; Palermo NI2091.",
    },
    "sella-curulis-relief": {
        "src": "https://upload.wikimedia.org/wikipedia/commons/d/d0/Relief_sella_curulis_Massimo.jpg",
        "width": 1200,
        "height": 657,
        "license": "CC BY 2.5",
        "institution": "Museo Nazionale Romano (Palazzo Massimo)",
        "source_page": "https://commons.wikimedia.org/wiki/File:Relief_sella_curulis_Massimo.jpg",
        "credit": "Relief with sella curulis folding stool.",
    },
    "joint-stool-met": {
        "src": "https://upload.wikimedia.org/wikipedia/commons/c/c7/Joint_Stool_MET_DT235347.jpg",
        "width": 1200,
        "height": 1500,
        "license": "CC0 1.0 (Met Open Access)",
        "institution": "The Metropolitan Museum of Art",
        "source_page": "https://commons.wikimedia.org/wiki/File:Joint_Stool_MET_DT235347.jpg",
        "credit": "English oak joint stool; Met American Wing.",
    },
    "sgabello-cc0": {
        "src": "https://upload.wikimedia.org/wikipedia/commons/a/a4/Sgabello_5KA3863.tif",
        "width": 1200,
        "height": 800,
        "license": "CC0 1.0",
        "institution": "Wikimedia Commons (museum scan)",
        "source_page": "https://commons.wikimedia.org/wiki/File:Sgabello_5KA3863.tif",
        "credit": "Italian Renaissance sgabello chair form.",
    },
    "met-william-mary-chair-142083": {
        "src": "https://upload.wikimedia.org/wikipedia/commons/6/6b/Side_Chair_MET_142083.jpg",
        "width": 1200,
        "height": 1830,
        "license": "CC0 1.0 (Met Open Access)",
        "institution": "The Metropolitan Museum of Art",
        "source_page": "https://commons.wikimedia.org/wiki/File:Side_Chair_MET_142083.jpg",
        "credit": "William and Mary–era American side chair.",
    },
    "met-queen-anne-chair-dp265158": {
        "src": "https://upload.wikimedia.org/wikipedia/commons/d/d6/Queen_Anne_Carved_Mahogany_Side_Chair_MET_DP265158.jpg",
        "width": 1200,
        "height": 1683,
        "license": "CC0 1.0 (Met Open Access)",
        "institution": "The Metropolitan Museum of Art",
        "source_page": "https://commons.wikimedia.org/wiki/File:Queen_Anne_Carved_Mahogany_Side_Chair_MET_DP265158.jpg",
        "credit": "Queen Anne carved mahogany side chair.",
    },
    "chippendale-director-plate": {
        "src": "https://upload.wikimedia.org/wikipedia/commons/2/26/The_Gentleman_and_Cabinet-Maker%27s_Director_MET_DP105205.jpg",
        "width": 1200,
        "height": 1772,
        "license": "CC0 1.0 (Met Open Access)",
        "institution": "The Metropolitan Museum of Art",
        "source_page": "https://commons.wikimedia.org/wiki/File:The_Gentleman_and_Cabinet-Maker%27s_Director_MET_DP105205.jpg",
        "credit": "Chippendale Director plate — published chair designs.",
    },
    "met-chippendale-chair-dp265161": {
        "src": "https://upload.wikimedia.org/wikipedia/commons/0/08/Chippendale_Carved_Mahogany_Side_Chair_MET_DP265161.jpg",
        "width": 1200,
        "height": 1723,
        "license": "CC0 1.0 (Met Open Access)",
        "institution": "The Metropolitan Museum of Art",
        "source_page": "https://commons.wikimedia.org/wiki/File:Chippendale_Carved_Mahogany_Side_Chair_MET_DP265161.jpg",
        "credit": "Chippendale carved mahogany side chair.",
    },
    "windsor-nutting-plate": {
        "src": "https://upload.wikimedia.org/wikipedia/commons/3/3a/Wallace_Nutting_Windsors_-_correct_Windsor_furniture._%281918%29_%2814592391377%29_retouched.jpg",
        "width": 1200,
        "height": 900,
        "license": "Public domain",
        "institution": "Wallace Nutting, Windsor Furniture (1918)",
        "source_page": "https://commons.wikimedia.org/wiki/File:Wallace_Nutting_Windsors_-_correct_Windsor_furniture._(1918)_(14592391377)_retouched.jpg",
        "credit": "Published Windsor chair forms — stick-and-saddle construction.",
    },
    "hepplewhite-shield-chair": {
        "src": "https://upload.wikimedia.org/wikipedia/commons/7/73/Hepplewhite_shield-shaped_dining_chair_in_%27country_house%27_condition%2C_May_2014.jpg",
        "width": 1200,
        "height": 1805,
        "license": "CC BY-SA 3.0",
        "institution": "Wikimedia Commons",
        "source_page": "https://commons.wikimedia.org/wiki/File:Hepplewhite_shield-shaped_dining_chair_in_%27country_house%27_condition,_May_2014.jpg",
        "credit": "Shield-back Hepplewhite side chair photograph.",
    },
    "met-rococo-chair-266251": {
        "src": "https://upload.wikimedia.org/wikipedia/commons/7/79/Side_Chair_MET_266251.jpg",
        "width": 1200,
        "height": 955,
        "license": "CC0 1.0 (Met Open Access)",
        "institution": "The Metropolitan Museum of Art",
        "source_page": "https://commons.wikimedia.org/wiki/File:Side_Chair_MET_266251.jpg",
        "credit": "Rococo Revival side chair — square and reeded postures in the same century.",
    },
    "met-gothic-chair-dp152859": {
        "src": "https://upload.wikimedia.org/wikipedia/commons/f/f0/Side_chair_MET_DP152859.jpg",
        "width": 1200,
        "height": 1540,
        "license": "CC0 1.0 (Met Open Access)",
        "institution": "The Metropolitan Museum of Art",
        "source_page": "https://commons.wikimedia.org/wiki/File:Side_chair_MET_DP152859.jpg",
        "credit": "Gothic Revival side chair.",
    },
    "met-side-chair-203079": {
        "src": "https://upload.wikimedia.org/wikipedia/commons/d/db/Side_Chair_MET_203079.jpg",
        "width": 1200,
        "height": 1523,
        "license": "CC0 1.0 (Met Open Access)",
        "institution": "The Metropolitan Museum of Art",
        "source_page": "https://commons.wikimedia.org/wiki/File:Side_Chair_MET_203079.jpg",
        "credit": "Stenciled factory side chair in the Hitchcock idiom.",
    },
    "thonet-14": {
        "src": "https://upload.wikimedia.org/wikipedia/commons/7/71/Michael_Thonet_14.jpg",
        "width": 888,
        "height": 1200,
        "license": "CC BY-SA 3.0",
        "institution": "Wikimedia Commons",
        "source_page": "https://commons.wikimedia.org/wiki/File:Michael_Thonet_14.jpg",
        "credit": "Thonet No. 14 bentwood chair.",
    },
    "met-slipper-chair-150203": {
        "src": "https://upload.wikimedia.org/wikipedia/commons/5/5e/Slipper_Chair_MET_150203.jpg",
        "width": 1200,
        "height": 1677,
        "license": "CC0 1.0 (Met Open Access)",
        "institution": "The Metropolitan Museum of Art",
        "source_page": "https://commons.wikimedia.org/wiki/File:Slipper_Chair_MET_150203.jpg",
        "credit": "Victorian slipper chair — long-course sitting.",
    },
    "stickley-tea-table-hnt": {
        "src": "https://upload.wikimedia.org/wikipedia/commons/1/15/Stickley_-_tea_table_-_top_-_HNT_-_Copy.jpg",
        "width": 1200,
        "height": 1256,
        "license": "CC BY-SA 4.0",
        "institution": "Wikimedia Commons",
        "source_page": "https://commons.wikimedia.org/wiki/File:Stickley_-_tea_table_-_top_-_HNT_-_Copy.jpg",
        "credit": "Stickley joinery — slat-back chairs share this shop culture.",
    },
    "breuer-cesca": {
        "src": "https://upload.wikimedia.org/wikipedia/commons/4/4a/Breuer_chair_2008.jpg",
        "width": 920,
        "height": 1200,
        "license": "CC BY-SA 3.0",
        "institution": "Wikimedia Commons",
        "source_page": "https://commons.wikimedia.org/wiki/File:Breuer_chair_2008.jpg",
        "credit": "Marcel Breuer Cesca (B32) cantilever side chair.",
    },
    "eames-lcw-ford": {
        "src": "https://upload.wikimedia.org/wikipedia/commons/b/bc/Eames_LCW_Chair_%281946-49%29%2C_Molded_Dining_Chair_%28c.1950%29%2C_Molded_Plywood_Leg_Splint_%28c.1943%29%2C_Mold_for_Eames_Fiberglass_Armchair_%281950-68%29_-_Fully_Furnished_-_Historic_Furniture_Exhibit_-_Henry_Ford_Museum.jpg",
        "width": 1200,
        "height": 1600,
        "license": "CC BY-SA 2.0",
        "institution": "The Henry Ford",
        "source_page": "https://commons.wikimedia.org/wiki/File:Eames_LCW_Chair_(1946-49),_Molded_Dining_Chair_(c.1950),_Molded_Plywood_Leg_Splint_(c.1943),_Mold_for_Eames_Fiberglass_Armchair_(1950-68)_-_Fully_Furnished_-_Historic_Furniture_Exhibit_-_Henry_Ford_Museum.jpg",
        "credit": "Eames molded plywood dining chair (DCM/LCW family) on display.",
    },
    "saarinen-tulip": {
        "src": "https://upload.wikimedia.org/wikipedia/commons/0/05/Eero_saarinen_per_knoll_international%2C_sedia_tulip_dalla_collezione_pedestal%2C_1955-56.jpg",
        "width": 1200,
        "height": 1777,
        "license": "CC BY 3.0",
        "institution": "Wikimedia Commons",
        "source_page": "https://commons.wikimedia.org/wiki/File:Eero_saarinen_per_knoll_international,_sedia_tulip_dalla_collezione_pedestal,_1955-56.jpg",
        "credit": "Eero Saarinen Pedestal side chair (Tulip), 1955–56.",
    },
    "wegner-wishbone-chair": {
        "src": "https://upload.wikimedia.org/wikipedia/commons/2/2e/Hans_Wegner_Wishbone_Chair.jpg",
        "width": 800,
        "height": 1200,
        "license": "CC BY-SA 2.0",
        "institution": "Wikimedia Commons",
        "source_page": "https://commons.wikimedia.org/wiki/File:Hans_Wegner_Wishbone_Chair.jpg",
        "credit": "Hans Wegner CH24 Wishbone chair.",
    },
    "jacobsen-series7": {
        "src": "https://upload.wikimedia.org/wikipedia/commons/1/14/Jacobsen%2C_7an.jpg",
        "width": 1200,
        "height": 1543,
        "license": "CC BY-SA 3.0",
        "institution": "Wikimedia Commons",
        "source_page": "https://commons.wikimedia.org/wiki/File:Jacobsen,_7an.jpg",
        "credit": "Arne Jacobsen Series 7 chair.",
    },
    "robin-day-poly-stack": {
        "src": "https://upload.wikimedia.org/wikipedia/commons/f/f5/Plastic_stacking_chairs_designed_by_Robin_Day.jpg",
        "width": 1200,
        "height": 1600,
        "license": "CC0 1.0",
        "institution": "Wikimedia Commons",
        "source_page": "https://commons.wikimedia.org/wiki/File:Plastic_stacking_chairs_designed_by_Robin_Day.jpg",
        "credit": "Robin Day polypropylene stacking chairs.",
    },
    "shaker-side-chair-met": {
        "src": "https://upload.wikimedia.org/wikipedia/commons/d/d4/Side_Chair_MET_190604.jpg",
        "width": 1200,
        "height": 1482,
        "license": "CC0 1.0 (Met Open Access)",
        "institution": "The Metropolitan Museum of Art",
        "source_page": "https://commons.wikimedia.org/wiki/File:Side_Chair_MET_190604.jpg",
        "credit": "Shaker side chair; Met American Wing.",
    },
    "ikea-lack": {
        "src": "https://upload.wikimedia.org/wikipedia/commons/1/15/IKEA_Lack.jpg",
        "width": 1050,
        "height": 1198,
        "license": "CC BY 3.0",
        "institution": "Wikimedia Commons",
        "source_page": "https://commons.wikimedia.org/wiki/File:IKEA_Lack.jpg",
        "credit": "IKEA LACK — flat-pack particleboard table (Ingolf essay cites boxed spindle chair; catalog still [VERIFY rights]).",
    },
    "hamptons-open-kitchen": {
        "src": "https://upload.wikimedia.org/wikipedia/commons/c/ca/Hamptons_Kitchen_Design_1.jpg",
        "width": 1200,
        "height": 800,
        "license": "CC BY-SA 4.0",
        "institution": "Wikimedia Commons",
        "source_page": "https://commons.wikimedia.org/wiki/File:Hamptons_Kitchen_Design_1.jpg",
        "credit": "Open kitchen/dining plan where banquettes replace freestanding chairs.",
    },
    "met-baltimore-painted-chair-dp144105": {
        "src": "https://upload.wikimedia.org/wikipedia/commons/b/b4/Side_Chair_MET_DP144105.jpg",
        "width": 1200,
        "height": 1573,
        "license": "CC0 1.0 (Met Open Access)",
        "institution": "The Metropolitan Museum of Art",
        "source_page": "https://commons.wikimedia.org/wiki/File:Side_Chair_MET_DP144105.jpg",
        "credit": "Painted American side chair.",
    },
    "quervelle-empire-pedestal-haa": {
        "src": "https://upload.wikimedia.org/wikipedia/commons/4/48/Rectangular_pedestal_dining_room_table_attributed_to_Gabriel_Quervelle_of_Philadelphia%2C_c._1820-1830%2C_mahogany%2C_HAA.JPG",
        "width": 1200,
        "height": 702,
        "license": "CC0 1.0",
        "institution": "Historic American Art (Commons)",
        "source_page": "https://commons.wikimedia.org/wiki/File:Rectangular_pedestal_dining_room_table_attributed_to_Gabriel_Quervelle_of_Philadelphia,_c._1820-1830,_mahogany,_HAA.JPG",
        "credit": "Empire dining furniture culture — pedestal and saber forms in the same rooms as tablet chairs.",
    },
}

DIAGRAM_SLUGS = [
    "the-chair-at-dinner",
    "eighteen-inches",
    "the-gap-under-the-apron",
    "seat-depth-and-the-knee",
    "rake-is-not-a-lounge",
    "lumbar-is-the-wrong-word",
    "the-front-rail-and-the-thigh",
    "arms-that-clear",
    "rack-is-the-dinner-test",
    "a-chair-a-wheelchair-can-meet",
    "how-to-measure-a-dining-chair",
    "children-at-the-table",
]


def main() -> None:
    lines = [
        "# Canonical plates for dining-chairs-history-design.",
        "# Museum rows: hot-linked Commons (no binaries in git). Diagram rows: pack SVG schematics.",
        "",
    ]
    for key, p in PLATES.items():
        lines.append(f"[plates.{key}]")
        for field in ("src", "width", "height", "license", "institution", "source_page", "credit"):
            val = p[field]
            if isinstance(val, int):
                lines.append(f"{field} = {val}")
            else:
                esc = str(val).replace('"', '\\"')
                lines.append(f'{field} = "{esc}"')
        lines.append("")
    for slug in DIAGRAM_SLUGS:
        key = f"diag-{slug}"
        rel = f"../assets/diagrams/{slug}.svg"
        lines.extend(
            [
                f"[plates.{key}]",
                f'src = "{rel}"',
                "width = 640",
                "height = 420",
                'license = "CC0-1.0 (pack schematic)"',
                'institution = "Bradley Brand editorial / pack"',
                f'source_page = "content/dining-chairs-history-design/assets/diagrams/{slug}.svg"',
                'credit = "Original line diagram; no AI-generated faces or stock people."',
                "",
            ]
        )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print("wrote", OUT, "plates", len(PLATES) + len(DIAGRAM_SLUGS))


if __name__ == "__main__":
    main()
