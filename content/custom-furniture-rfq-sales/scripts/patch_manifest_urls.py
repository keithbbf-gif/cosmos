#!/usr/bin/env python3
"""Patch download_url fields in image_assets.json with verified Commons thumbs."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "image_assets.json"

URLS: dict[str, str | None] = {
    "cf-rfq-01-vintage-furniture-price-list.jpg": "https://thumb.wikimedia.org/wikipedia/commons/thumb/e/ed/Price_list_and_barbers%27_purchasing_guide_of_barbers%27_chairs%2C_furniture%2C_and_barbers%27_supplies_%281884%29_%2814597488498%29.jpg/1920px-Price_list_and_barbers%27_purchasing_guide_of_barbers%27_chairs%2C_furniture%2C_and_barbers%27_supplies_%281884%29_%2814597488498%29.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail",
    "cf-rfq-07-kitchen-measure-prep.jpg": None,
    "cf-rfq-09-tape-measure-wall.jpg": None,
    "cf-rfq-12-baseboard-case-piece.jpg": "https://thumb.wikimedia.org/wikipedia/commons/thumb/5/53/Open_plan_house%3B_kitchen_and_sitting_room_in_Corinda%2C_Queensland_01.jpg/1920px-Open_plan_house%3B_kitchen_and_sitting_room_in_Corinda%2C_Queensland_01.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail",
    "cf-rfq-15-ceiling-fixture-clearance.jpg": "https://upload.wikimedia.org/wikipedia/commons/c/ca/Hamptons_Kitchen_Design_1.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail_unscaled",
    "cf-rfq-17-two-tapes-measure.jpg": None,
    "cf-rfq-20-hardwood-lumber-yard.jpg": "https://thumb.wikimedia.org/wikipedia/commons/thumb/c/c9/Berkey_and_Gay_Furniture_Company_Factory_-1.jpg/1920px-Berkey_and_Gay_Furniture_Company_Factory_-1.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail",
    "cf-rfq-21-woodworking-shop-interior.jpg": "https://upload.wikimedia.org/wikipedia/commons/4/49/Wharton_Esherick_House_%26_Studio%2C_1520_Horsehoe_Trail%2C_Malvern_%28Chester_County%2C_Pennsylvania%29.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail_unscaled",
    "cf-rfq-24-calendar-planning.jpg": "https://thumb.wikimedia.org/wikipedia/commons/thumb/7/75/Berkey_and_Gay_Furniture_Company_Factory%2C_aerial_view%2C_1924.jpg/1920px-Berkey_and_Gay_Furniture_Company_Factory%2C_aerial_view%2C_1924.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail",
    "cf-rfq-31-wood-finish-samples.jpg": None,
    "cf-rfq-32-smartphone-color-screen.jpg": None,
    "cf-rfq-33-furniture-showroom-interior.jpg": "https://thumb.wikimedia.org/wikipedia/commons/thumb/9/90/Furniture_store_interior_LCCN2011634378.tif/lossy-page1-1920px-Furniture_store_interior_LCCN2011634378.tif.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail",
    "cf-rfq-35-shipping-crates-warehouse.jpg": "https://upload.wikimedia.org/wikipedia/commons/7/72/EFTA00002265_-_Cluttered_warehouse_with_stacked_boxes_a_fan_and_shelves_filled_with_supplies_under_industrial_lighting.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail_unscaled",
    "cf-rfq-37-clipboard-checklist.jpg": None,
    "cf-rfq-39-customer-supplied-lumber.jpg": "https://thumb.wikimedia.org/wikipedia/commons/thumb/7/75/Berkey_and_Gay_Furniture_Company_Factory%2C_aerial_view%2C_1924.jpg/1920px-Berkey_and_Gay_Furniture_Company_Factory%2C_aerial_view%2C_1924.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail",
    "cf-rfq-42-empty-showroom-chair.jpg": "https://thumb.wikimedia.org/wikipedia/commons/thumb/b/b5/De_Groot_showroom%2C_Rushcutters_Bay.jpg/1920px-De_Groot_showroom%2C_Rushcutters_Bay.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail",
    "cf-rfq-43-walking-away-door.jpg": "https://thumb.wikimedia.org/wikipedia/commons/thumb/b/b5/De_Groot_showroom%2C_Rushcutters_Bay.jpg/1920px-De_Groot_showroom%2C_Rushcutters_Bay.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail",
}

FILE_RENAMES = {
    "cf-rfq-32-smartphone-color-screen.jpg": "schematic-phone-vs-room-light.svg",
    "cf-rfq-37-clipboard-checklist.jpg": "schematic-rfq-checklist.svg",
}


def main() -> int:
    assets = json.loads(MANIFEST.read_text(encoding="utf-8"))
    for a in assets:
        fname = a["file"]
        if fname in FILE_RENAMES:
            a["file"] = FILE_RENAMES[fname]
            a["kind"] = "svg"
            a["license"] = "CC0 1.0"
            a["commons_url"] = ""
            a["download_url"] = ""
            a["credit"] = "Original line art for this pack"
            if "phone" in fname:
                a["alt"] = "Diagram contrasting saturated phone display colors with a finish board viewed in room light"
        if fname in URLS:
            val = URLS[fname]
            a["download_url"] = val or ""
        new = a["file"]
        if new in URLS and new not in FILE_RENAMES:
            val = URLS.get(new)
            if val is not None:
                a["download_url"] = val or ""
    MANIFEST.write_text(json.dumps(assets, indent=2) + "\n", encoding="utf-8")
    print("patched", MANIFEST)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
