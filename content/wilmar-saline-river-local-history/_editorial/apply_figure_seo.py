#!/usr/bin/env python3
"""Apply figure SEO, historical Figure 2, and voice_check: edited across the pack."""
from __future__ import annotations

import json
import re
from pathlib import Path

PACK = Path(__file__).resolve().parents[1]
ARTICLES = PACK / "articles"
REGISTRY = json.loads((PACK / "assets/photos/registry.json").read_text(encoding="utf-8"))
BY_ID = {r["id"]: r for r in REGISTRY}

# series_no -> asset id
PHOTO_BY_SERIES: dict[int, str] = {
    1: "wsr-1859-colton-arkansas-railroads",
    2: "wsr-cotton-pickers-pulaski-met",
    3: "wsr-mopac-depot-charleston",
    4: "wsr-lumber-survey-crew-1929",
    5: "wsr-wpa-building-wilmar",
    6: "wsr-woods-crew-1929",
    7: "wsr-iron-mountain-railroad-map-loc",
    8: "wsr-woods-crew-1929",
    9: "wsr-lumber-survey-crew-1929",
    10: "wsr-arkansas-review-1911",
    11: "wsr-cotton-bale-warehouse-haer",
    12: "wsr-arkansas-review-1911",
    13: "wsr-wilmar-high-school",
    14: "wsr-wpa-building-wilmar",
    15: "wsr-wilmar-high-school",
    16: "wsr-general-order-3-juneteenth",
    17: "wsr-general-order-3-juneteenth",
    18: "wsr-cotton-pickers-pulaski-met",
    19: "wsr-leland-giants-1910",
    20: "wsr-wpa-building-wilmar",
    21: "wsr-wilmar-high-school",
    22: "wsr-mopac-depot-charleston",
    23: "wsr-wpa-building-wilmar",
    24: "wsr-iron-mountain-railroad-map-loc",
    25: "wsr-saline-river-ouachita-nf",
    26: "wsr-saline-river-ouachita-nf",
    27: "wsr-saline-river-ouachita-nf",
    28: "wsr-red-river-steamboat-blessing",
    29: "wsr-red-river-steamboat-blessing",
    30: "wsr-woods-crew-1929",
    31: "wsr-red-river-steamboat-blessing",
    32: "wsr-mo-ark-map-nara",
    33: "wsr-freshwater-mussel",
    34: "wsr-mo-ark-map-nara",
    35: "wsr-iron-mountain-railroad-map-loc",
    36: "wsr-1859-colton-arkansas-railroads",
    37: "wsr-cotton-pickers-pulaski-met",
    38: "wsr-mo-ark-map-nara",
    39: "wsr-wilmar-high-school",
    40: "wsr-general-order-3-juneteenth",
    41: "wsr-saline-river-ouachita-nf",
    42: "wsr-saline-river-ouachita-nf",
    43: "wsr-wilmar-high-school",
    44: "wsr-cotton-bale-warehouse-haer",
    45: "wsr-arkansas-review-1911",
    46: "wsr-cotton-bale-warehouse-haer",
}

ALT_BY_SERIES: dict[int, str] = {
    1: "1859 Colton pocket map of Arkansas showing railroad lines and county geography",
    2: "Cotton pickers in a Pulaski County, Arkansas field, early twentieth century photograph",
    3: "Missouri Pacific railroad depot building, representative of Warren Branch era depots",
    4: "Logging company survey crew at a camp office, Pacific Northwest, circa 1929",
    5: "WPA-era public building in Wilmar, Drew County, Arkansas",
    6: "Timber woods crew with logging equipment, circa 1929",
    7: "Historic map of the Iron Mountain railroad and its connections",
    8: "Timber woods crew felling and yarding logs, circa 1929",
    9: "Logging survey crew at a lumber company camp office, circa 1929",
    10: "1911 Arkansas commerce and industry review title plate",
    11: "Cotton bale storage warehouse at a southern mill, Historic American Engineering Record",
    12: "1911 Arkansas commerce and industry review title plate",
    13: "Wilmar High School building in Wilmar, Arkansas",
    14: "WPA-era civic building in Wilmar, Arkansas",
    15: "Wilmar High School in Wilmar, Drew County, Arkansas",
    16: "Juneteenth General Order No. 3 text on a public monument",
    17: "Juneteenth General Order No. 3 inscription, emancipation proclamation in Texas",
    18: "Cotton field laborers in Arkansas, period photograph used as ledger still",
    19: "1910 Leland Giants baseball team portrait, era of segregated town ball",
    20: "WPA building in Wilmar, Arkansas, civic architecture after the mill",
    21: "Wilmar High School, Wilmar, Arkansas, census-era town still",
    22: "Missouri Pacific depot, stand-in for rail-and-utility corridor towns",
    23: "WPA-era building in Wilmar, Arkansas, churches-after-mill civic context",
    24: "Iron Mountain railroad connection map, children riding to Monticello by rail",
    25: "Saline River flowing through Ouachita National Forest, Arkansas",
    26: "Saline River in the Ouachita National Forest, free-flowing water",
    27: "Saline River landscape, Arkansas, undammed reach",
    28: "Red River steamboat landing, nineteenth-century river commerce",
    29: "Steamboat at a Red River landing, era of the Gate City trade",
    30: "Logging woods crew, southern timber industry stand-in",
    31: "Red River steamboat landing photograph, packet-boat era",
    32: "Historic map of southeastern Missouri and northeastern Arkansas",
    33: "Freshwater mussels grouped on a stream bottom",
    34: "Regional map of Missouri and northeastern Arkansas",
    35: "Iron Mountain railroad map, Warren Branch context",
    36: "1859 Arkansas railroad pocket map, Drew County region",
    37: "Cotton pickers in an Arkansas field, farm-before-lumber still",
    38: "Historic map of Missouri and northeastern Arkansas bottomlands",
    39: "Wilmar High School after the mill whistle",
    40: "General Order No. 3 Juneteenth monument text",
    41: "Saline River in the Ouachita National Forest, river that names the workshop",
    42: "Saline River landscape, lignite and river energy context",
    43: "Wilmar High School, suburb-of-Monticello era building",
    44: "Cotton bale warehouse, Farmers Union storage analog",
    45: "1911 Arkansas historical review plate, music-and-civic culture context",
    46: "Cotton bale warehouse interior, commissary-and-staple still",
}

CAPTION_TAIL: dict[int, str] = {
    2: "Pulaski County, not Drew — used here as a period still for field labor the encyclopedia names but does not photograph.",
    3: "Charleston, Mississippi County — not Wilmar’s four-function house; a depot type the Warren Branch made ordinary.",
    4: "Pacific Northwest camp — not Gates’s woods; a logging-office still the prose can borrow without pretending it is Drew County.",
    8: "Pacific Northwest, circa 1929 — extraction method, not Wilmar’s acreage.",
    9: "Same seam as essay 08: method plate, not a Gates portrait.",
    18: "Not a lynching image. A field still for a county whose violence the record names without photographs.",
    19: "Chicago Leland Giants, 1910 — not Hudspeth Park’s roster; an era plate for segregated town ball.",
    22: "Depot stand-in for rail-and-pipeline towns; not the Wilmar Transmission Station.",
    28: "Red River landing — river trade neighbor to the Saline-Ouachita system, not the *Gate City* wreck site.",
    29: "Blessing’s Red River landing — commerce plate, not the October 1913 wreck photograph.",
    31: "Packet-boat era plate; Bridges Bluff is upstream geography, not this landing.",
    33: "European mussel group — species plate, not a Saline pearl harvest.",
}


def series_no_from_path(path: Path) -> int:
    return int(path.name.split("-", 1)[0])


def upgrade_figure_one(text: str) -> str:
    def repl(match: re.Match[str]) -> str:
        block = match.group(0)
        if 'class="wilmar-figure"' in block:
            return block
        block = block.replace("<figure>", '<figure class="wilmar-figure">', 1)
        block = re.sub(
            r"<img\s+",
            '<img loading="lazy" decoding="async" ',
            block,
            count=1,
        )
        if "loading=" in block and block.count("loading=") > 1:
            block = re.sub(r'loading="lazy"\s+decoding="async"\s+loading="lazy"\s+decoding="async"\s+', 'loading="lazy" decoding="async" ', block)
        return block

    return re.sub(r"<figure[^>]*>.*?</figure>", repl, text, flags=re.DOTALL)


def figure_two_block(series: int) -> str:
    aid = PHOTO_BY_SERIES[series]
    meta = BY_ID[aid]
    alt = ALT_BY_SERIES[series]
    tail = CAPTION_TAIL.get(series, "")
    cap = f"Figure 2. {alt}."
    if tail:
        cap += f" {tail}"
    cap += f" Credit: {meta['credit']}. License: {meta['license']}."
    w, h = meta["width"], meta["height"]
    return (
        f'<figure class="wilmar-figure wilmar-figure--period">\n'
        f'<img src="../assets/photos/{meta["filename"]}" alt="{alt}" '
        f'width="{w}" height="{h}" loading="lazy" decoding="async" />\n'
        f"<figcaption>{cap}</figcaption>\n"
        f"</figure>\n"
    )


def inject_figure_two(text: str, series: int) -> str:
    if "../assets/photos/" in text:
        return text
    marker = "## Sources for this piece"
    block = figure_two_block(series) + "\n"
    if marker in text:
        return text.replace(marker, block + marker, 1)
    return text.rstrip() + "\n\n" + block


def patch_article(path: Path) -> None:
    series = series_no_from_path(path)
    text = path.read_text(encoding="utf-8")
    text = text.replace("voice_check: human", "voice_check: edited")
    text = upgrade_figure_one(text)
    text = inject_figure_two(text, series)
    path.write_text(text, encoding="utf-8")


def main() -> None:
    for path in sorted(ARTICLES.glob("*.md")):
        patch_article(path)
        print("patched", path.name)


if __name__ == "__main__":
    main()
