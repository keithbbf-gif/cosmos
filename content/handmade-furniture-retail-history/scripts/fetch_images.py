#!/usr/bin/env python3
"""Download curated Wikimedia Commons assets for HFRH drafts. Run from repo root."""

from __future__ import annotations

import json
import re
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMAGES = ROOT / "images"
UA = "COSMOS-ContentBot/1.0 (https://github.com/keithbbf-gif/cosmos; educational)"

# draft_id -> Commons filename (no File: prefix)
ASSETS: list[tuple[str, str, str]] = [
    # id, commons_file, local_stem
    ("hfrh-00-01", "Berkey and Gay Furniture Company Factory, aerial view, 1924.jpg", "grand-rapids-furniture-factory-1924"),
    ("hfrh-00-02", "Furniture store interior LCCN2011634378.tif", "historic-furniture-store-interior"),
    ("hfrh-00-03", "A history of oak furniture (1920) (14593664349).jpg", "oak-furniture-catalog-1920"),
    ("hfrh-00-04", "Price list and barbers' purchasing guide of barbers' chairs, furniture, and barbers' supplies (1884) (14597488498).jpg", "vintage-furniture-price-list-1884"),
    ("hfrh-01-05", "Craftsman's World Aileen Webb-42.jpg", "aileen-osborn-webb-craft-league"),
    ("hfrh-01-06", "Craft fair 130504-N-WF272-063.jpg", "acc-craft-fair-booth-market"),
    ("hfrh-01-07", "De Groot showroom, Rushcutters Bay.jpg", "craft-gallery-showroom-interior"),
    ("hfrh-01-08", "Wharton Esherick House & Studio, 1520 Horsehoe Trail, Malvern (Chester County, Pennsylvania).jpg", "wharton-esherick-studio-house"),
    ("hfrh-01-09", "Wendell castle, tavolino da caffè, rochester NY 1967.jpg", "wendell-castle-studio-furniture"),
    ("hfrh-01-10", "06 10 016049Southern Furniture Exposition Building, High Point, N. C. (5811465873).jpg", "jury-booth-market-hall"),
    ("hfrh-01-11", "Museum of Arts and Design Midtown.jpg", "museum-of-arts-and-design-craft"),
    ("hfrh-01-12", "Crop from Berkey & Gay Furniture Co.'s sales rooms, Grand Rapids, Michigan (NYPL NYPG90-F390-G90F390 012B).jpg", "grand-rapids-furniture-sales-room"),
    ("hfrh-02-13", "Night View of the Merchandise Mart, Chicago - Front.png", "merchandise-mart-chicago-trade"),
    ("hfrh-02-14", "Merchandise Mart 080405.jpg", "merchandise-mart-design-center"),
    ("hfrh-02-15", "Furniture store interior LCCN2011634378.tif", "to-the-trade-showroom-floor"),
    ("hfrh-02-16", "Grand Rapids Showcase Company Factory 06.jpg", "furniture-showcase-factory-territory"),
    ("hfrh-02-17", "Price list and barbers' purchasing guide of barbers' chairs, furniture, and barbers' supplies (1884) (14781018521).jpg", "wholesale-net-list-price-sheet"),
    ("hfrh-02-18", "Showplace, High Point Market, North Carolina.jpg", "high-point-market-showplace-sample"),
    ("hfrh-02-19", "Price list and barbers' purchasing guide of barbers' chairs, furniture, and barbers' supplies (1884) (14597488498).jpg", "trade-paper-price-trail-1884"),
    ("hfrh-02-20", "Line Changes Being Made in the Installation of the Dial System. Enrollees Working Under Supervision of Telephone Linemen from Billings District Office. - DPLA - 7617cfdcd7671be40c0ef4c7abf6d4c7.jpg", "telephone-office-outreach-era"),
    ("hfrh-02-21", "Auto Delivery Moving Company (1911) (ADVERT 133).jpeg", "furniture-delivery-truck-1911"),
    ("hfrh-03-22", "06 10 016049Southern Furniture Exposition Building, High Point, N. C. (5811465873).jpg", "southern-furniture-exposition-high-point"),
    ("hfrh-03-23", "Berkey and Gay Furniture Company Factory, aerial view, 1924.jpg", "wholesale-market-order-factory-scale"),
    ("hfrh-03-24", "A history of oak furniture (1920) (14593824658).jpg", "furniture-tear-sheet-catalog-page"),
    ("hfrh-04-25", "EBay former logo.svg", "ebay-early-marketplace-logo"),
    ("hfrh-04-26", "0252 kitchen showroom window (9959104154).jpg", "showroom-window-display-photography"),
    ("hfrh-04-27", "EFTA00002265 - Cluttered warehouse with stacked boxes a fan and shelves filled with supplies under industrial lighting.jpg", "freight-warehouse-crates-boxes"),
    ("hfrh-05-28", "Etsy Brooklyn Headquarters (the clocktower).jpg", "etsy-brooklyn-headquarters-2005-era"),
    ("hfrh-05-29", "Shaker-Furniture.jpg", "handmade-craft-furniture-shaker"),
    ("hfrh-05-30", "Shaker ladder chairs.jpg", "handmade-furniture-authenticity-craft"),
    ("hfrh-05-31", "Craft fair 130504-N-WF272-063.jpg", "craft-fair-handmade-market-booth"),
    ("hfrh-05-32", "A history of oak furniture (1920) (14777817264).jpg", "catalog-listing-fees-ads-era"),
    ("hfrh-05-33", "Crop from Berkey & Gay Furniture Co.'s sales rooms, Grand Rapids, Michigan (NYPL NYPG90-F390-G90F390 012B).jpg", "etsy-wholesale-showroom-catalog"),
    ("hfrh-06-34", "EFTA00002281 - Large white mattress rests on the floor in a dimly lit warehouse with shelves stacked high with boxes and supplies.jpg", "closeout-warehouse-inventory"),
    ("hfrh-06-35", "Merchandise Mart, Chicago, Illinois (9181646666).jpg", "ecommerce-catalog-hub-chicago"),
    ("hfrh-06-36", "Warehouse interior showcasing organized shelving and packages.jpg", "dropship-warehouse-shelving"),
    ("hfrh-06-37", "Showplace, High Point Market, North Carolina.jpg", "high-point-market-recruitment-floor"),
    ("hfrh-06-38", "Shelves stocked with boxes and carts in a spacious warehouse environment during daylight hours.jpg", "sku-flood-warehouse-shelves"),
    ("hfrh-06-39", "Made in USA label 01.jpg", "map-private-label-made-in-usa"),
    ("hfrh-06-40", "EFTA00002265 - Cluttered warehouse with stacked boxes a fan and shelves filled with supplies under industrial lighting.jpg", "returns-warehouse-logistics"),
    ("hfrh-06-41", "De Groot showroom, Rushcutters Bay.jpg", "empty-showroom-walking-away"),
    ("hfrh-07-42", "Price list and barbers' purchasing guide of barbers' chairs, furniture, and barbers' supplies (1884) (14781776084).jpg", "four-prices-furniture-tags"),
    ("hfrh-07-43", "Made in USA label 02.jpg", "american-made-label-retail"),
    ("hfrh-07-44", "Berkey and Gay Furniture Company Factory -1.jpg", "handmade-furniture-shop-tradition"),
]

# SEO alt text and figcaption per draft id
CAPTIONS: dict[str, tuple[str, str]] = {
    "hfrh-00-01": (
        "Aerial view of the Berkey and Gay furniture factory in Grand Rapids, Michigan, circa 1924, representing the industrial scale behind American casegoods and handmade furniture retail history",
        "Grand Rapids became a furniture capital generations before online marketplaces; factory scale and showroom doors learned different languages early.",
    ),
    "hfrh-00-02": (
        "Historic photograph of an American furniture store interior with displayed casegoods and seating",
        "A furniture store interior from the photographic record — not a gallery, not a website — a room where buyers learned to read display as promise.",
    ),
    "hfrh-00-03": (
        "Page from a 1920 illustrated history of oak furniture showing catalog engravings of handmade and manufactured pieces",
        "Oak furniture catalog plates from 1920: four doors — consignment, wholesale, to-the-trade, dropship — all eventually fight over the same stolen words.",
    ),
    "hfrh-00-04": (
        "Victorian-era printed price list for barber chairs and furniture illustrating how retail vocabulary and list prices were published",
        "Printed price lists trained buyers to treat list price as fiction; handmade, custom, wholesale, and artisan drifted when the paper stopped matching the shop.",
    ),
    "hfrh-01-05": (
        "Historical photograph related to Aileen Osborn Webb and the American craft cooperative retail movement that opened America House in 1940",
        "America House and the Handcraft Cooperative League gave rural makers a metropolitan gallery door — the ancestor of serious American craft retail.",
    ),
    "hfrh-01-06": (
        "Cover or title page of an official New York State Fair exhibition catalog listing crafts and goods on display",
        "State fair catalogs turned handmade retail into a portable gallery: jury, booth fee, public buyers, and store buyers with wholesale notebooks.",
    ),
    "hfrh-01-07": (
        "Interior of the De Groot furniture showroom in Rushcutters Bay, a historic gallery-style retail room",
        "Gallery consignment keeps title with the maker; the showroom split pays for editing, rent, and the talk that teaches a buyer to trust the wall.",
    ),
    "hfrh-01-08": (
        "Wharton Esherick House and Studio in Pennsylvania, a landmark of studio furniture treated as art",
        "Studio furniture climbed toward art in rooms like Wharton Esherick's — handmade tables and chairs with a museum shadow still meant for living.",
    ),
    "hfrh-01-09": (
        "Wendell Castle studio furniture coffee table photographed in Rochester, New York, 1967",
        "When a table becomes a gallery object, the buyer must decide whether to eat on it or admire it — studio furniture lives in that tension.",
    ),
    "hfrh-01-10": (
        "Historic Jamestown furniture exposition catalog promising authentic photographs of booths and exhibits",
        "Jury, booth rent, and a hall full of competitors: craft fair economics mirror gallery consignment with worse weather and better foot traffic.",
    ),
    "hfrh-01-11": (
        "Museum of Arts and Design building in Midtown Manhattan, successor institution to the craft teaching impulse behind America House",
        "What galleries taught — editing, patience, price as a taught decision — still lives in institutions that curate handmade furniture as culture.",
    ),
    "hfrh-01-12": (
        "Berkey and Gay Furniture Company sales room in Grand Rapids, Michigan, a wholesale showroom floor",
        "The handoff from gallery wall to trade showroom: casegoods lines on a sample floor, net pricing, and buyers who already speak wholesale.",
    ),
    "hfrh-02-13": (
        "Night view of the Merchandise Mart in Chicago, a landmark to-the-trade design and furniture center",
        "To-the-trade showrooms: browse and buy are different acts. The Merchandise Mart is the scale model of door two for Midwest designers.",
    ),
    "hfrh-02-14": (
        "Exterior of the Merchandise Mart, Chicago, a major design center for furniture and interiors professionals",
        "Design centers from Chicago to New York are not malls and not High Point Market — they are permanent cities for the trade.",
    ),
    "hfrh-02-15": (
        "Historic furniture store interior showing arranged seating and casegoods on a showroom floor",
        "Getting the line in means earning square feet on a sample floor where a designer can touch finishes, not just scroll photographs.",
    ),
    "hfrh-02-16": (
        "Grand Rapids Showcase Company factory exterior, representing regional furniture manufacturing and territory",
        "Territory and exclusivity were map problems before they were portal checkboxes — factories and showrooms shared zip codes and reps.",
    ),
    "hfrh-02-17": (
        "Victorian printed price list page for furniture and barber chairs showing list and net pricing columns",
        "Net, list, and multiplier arithmetic on paper — the hidden math behind handmade furniture quoted to designers at trade price.",
    ),
    "hfrh-02-18": (
        "Showplace building at High Point Market, North Carolina, a trade destination for furniture buyers",
        "Sample floors at market and in design centers let buyers compare handmade lines beside casegoods under one roof.",
    ),
    "hfrh-02-19": (
        "1916 spring trade list catalog cover aimed at florists and dealers, an example of paper wholesale trails",
        "The paper trail — tear sheets, line sheets, signed acknowledgments — once carried more legal weight than a shopping cart.",
    ),
    "hfrh-02-20": (
        "Historic photograph of telephone line installation, evoking the era of cold-calling designers from a shop desk",
        "Cold-calling designers was door-to-door work with a dial tone: persistence, samples, and a finish story that survived hang-ups.",
    ),
    "hfrh-02-21": (
        "1911 advertisement for an auto delivery moving company, illustrating furniture delivery by truck",
        "Own trucks mean the shop keeps the last mile — handmade furniture retail trust is often won or lost on the front step.",
    ),
    "hfrh-03-22": (
        "Southern Furniture Exposition Building in High Point, North Carolina, home of the High Point Market trade fair",
        "High Point Market began as the Southern Furniture Market in 1909 — a twice-a-year wholesale city, not a public furniture mall.",
    ),
    "hfrh-03-23": (
        "Pocket directory of southern furniture manufacturers, a wholesale reference book for market buyers",
        "A market order once moved title and risk with ink; a website cart is a thinner document with fewer witnesses.",
    ),
    "hfrh-03-24": (
        "Illustrated catalog page from a 1920 history of oak furniture used as a tear sheet for buyers",
        "Tear sheets were portable memory — finish codes, dimensions, and the line rep's handwriting between market and showroom.",
    ),
    "hfrh-04-25": (
        "Early eBay logo from the marketplace's first web era, representing auction-era online furniture retail experiments",
        "Before Etsy, auction sites and Yahoo storefronts taught makers that photography and freight were half the product.",
    ),
    "hfrh-04-26": (
        "Kitchen and furniture showroom window display photographed from the street",
        "When the photograph becomes the showroom, handmade furniture competes on light, crop, and honesty about scale.",
    ),
    "hfrh-04-27": (
        "Warehouse interior with stacked boxes and shelving, illustrating freight and fulfillment separate from small-parcel shipping",
        "Freight is not shipping: crates, blankets, and lift gates — the vocabulary platforms blur when they promise free delivery.",
    ),
    "hfrh-05-28": (
        "Etsy Brooklyn headquarters clocktower building, corporate home of the handmade marketplace launched in 2005",
        "Etsy launched in Brooklyn in 2005 with handmade positioning — a new gallery door that scaled faster than any Madison Avenue room.",
    ),
    "hfrh-05-29": (
        "Shaker handmade furniture example showing craft construction and proportion",
        "Jewelry economics on Etsy trained buyers to compare hours and materials; furniture makers imported those expectations at a loss.",
    ),
    "hfrh-05-30": (
        "Shaker ladder-back chairs exemplifying authentic handmade furniture construction",
        "Handmade wars were fights over definitions — who made it, who designed it, and whether the platform would enforce the word.",
    ),
    "hfrh-05-31": (
        "Outdoor craft fair booths displaying handmade goods without a permanent gallery lease",
        "Three buckets on one storefront — handmade, vintage, supplies — one URL hiding different contracts behind a single search bar.",
    ),
    "hfrh-05-32": (
        "1920 oak furniture catalog plate showing how listings and illustrated ads presented casegoods to buyers",
        "Fees and promoted listings turned craft retail into media buying; the split still looked like a gallery cut without the gallerist.",
    ),
    "hfrh-05-33": (
        "Wholesale furniture catalog promising goods for home, office, and hotel trade buyers",
        "Etsy Wholesale tried to connect growing handmade sellers to brick retailers — gallery consignment logic at spreadsheet scale.",
    ),
    "hfrh-06-34": (
        "Cluttered warehouse with stacked boxes under industrial lighting, evoking closeout and overstock inventory partnerships",
        "Overstock-era partners moved closeout and fulfillment inventory — a different risk assignment than consignment on a gallery wall.",
    ),
    "hfrh-06-35": (
        "Merchandise Mart interior corridor in Chicago, a hub where catalog companies met physical trade infrastructure",
        "CSN Stores grew from niche sites into Wayfair — supplier-direct dropship catalogs assembled in the same trade cities as showrooms.",
    ),
    "hfrh-06-36": (
        "Organized warehouse shelving with packages ready for shipment, illustrating dropship fulfillment",
        "Dropship assigns the customer relationship to a platform while the shop keeps production — door four with door two's paperwork.",
    ),
    "hfrh-06-37": (
        "Showplace at High Point Market where platform buyers recruited family shops for online catalogs",
        "Recruiters with badges walked High Point halls asking small shops for SKUs — wholesale geography repurposed for catalog flood.",
    ),
    "hfrh-06-38": (
        "Warehouse shelves stocked with cartons, visual metaphor for SKU flood on marketplace catalogs",
        "Millions of SKUs turned handmade lines into rows in a database; discovery replaced the taught buyer in the gallery.",
    ),
    "hfrh-06-39": (
        "Made in USA retail label sewn into goods, relevant to MAP policies and private-label listings",
        "MAP fights and private-label listings traded on country-of-origin language — American made as marketing before audit.",
    ),
    "hfrh-06-40": (
        "Industrial warehouse with stacked product boxes, suggesting returns processing and reverse logistics load",
        "Returns and chargebacks push risk back to the maker while the platform keeps the customer — consignment without the wall.",
    ),
    "hfrh-06-41": (
        "Historic De Groot furniture showroom interior, a quiet room after the platform contract ends",
        "Walking away from a portal contract often means rebuilding showroom relationships the gallery door once held open.",
    ),
    "hfrh-07-42": (
        "Victorian furniture and barber-chair price list page showing multiple published price columns",
        "Four prices for one handmade piece — gallery, designer net, showroom, and your floor — each honest only if calculated on purpose.",
    ),
    "hfrh-07-43": (
        "Made in USA label on consumer goods, a retail claim tied to sourcing and showroom language",
        "American made meant traceable labor and domestic supply chains before the word became a filter checkbox.",
    ),
    "hfrh-07-44": (
        "Berkey and Gay furniture factory complex, closing image tying factory, showroom, and handmade tradition",
        "The series closes where it opened: shops, markets, and platforms change; handmade furniture still lives between price, proof, and delivery.",
    ),
}


def commons_info(filename: str) -> dict:
    api = "https://commons.wikimedia.org/w/api.php"
    params = urllib.parse.urlencode(
        {
            "action": "query",
            "titles": f"File:{filename}",
            "prop": "imageinfo",
            "iiprop": "url|extmetadata|mime|size",
            "iiurlwidth": 1400,
            "format": "json",
        }
    )
    req = urllib.request.Request(f"{api}?{params}", headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.load(resp)
    pages = data["query"]["pages"]
    page = next(iter(pages.values()))
    if page.get("missing"):
        raise SystemExit(f"Missing on Commons: {filename}")
    return page["imageinfo"][0]


def safe_ext(filename: str, mime: str) -> str:
    lower = filename.lower()
    if lower.endswith(".svg"):
        return ".svg"
    if lower.endswith(".pdf"):
        return ".pdf"
    if lower.endswith(".png"):
        return ".png"
    if lower.endswith(".jpeg") or lower.endswith(".jpg"):
        return ".jpg"
    if lower.endswith(".tif") or lower.endswith(".tiff"):
        return ".jpg"
    if "svg" in mime:
        return ".svg"
    if "pdf" in mime:
        return ".pdf"
    if "png" in mime:
        return ".png"
    return ".jpg"


def download(url: str, dest: Path) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = resp.read()
    dest.write_bytes(data)


def strip_html(s: str) -> str:
    return re.sub(r"<[^>]+>", "", s).strip()


def main() -> None:
    IMAGES.mkdir(parents=True, exist_ok=True)
    meta_out: list[dict] = []
    for draft_id, commons_name, stem in ASSETS:
        info = commons_info(commons_name)
        mime = info.get("mime", "")
        ext = safe_ext(commons_name, mime)
        url = info.get("thumburl") or info.get("url")
        if not url:
            raise SystemExit(f"No URL for {commons_name}")
        local_name = f"{draft_id}-{stem}{ext}"
        dest = IMAGES / local_name
        if not dest.exists() or dest.stat().st_size < 500:
            print("download", local_name)
            download(url, dest)
        em = info.get("extmetadata", {})
        meta_out.append(
            {
                "draft_id": draft_id,
                "file": local_name,
                "commons_file": commons_name,
                "commons_url": f"https://commons.wikimedia.org/wiki/File:{urllib.parse.quote(commons_name.replace(' ', '_'))}",
                "source_url": info.get("descriptionurl") or info.get("url"),
                "download_url": url,
                "license": strip_html(em.get("LicenseShortName", {}).get("value", "See Commons")),
                "license_url": strip_html(em.get("LicenseUrl", {}).get("value", "")),
                "artist": strip_html(em.get("Artist", {}).get("value", "See Commons file page")),
                "credit": strip_html(em.get("Credit", {}).get("value", "")),
                "alt": CAPTIONS[draft_id][0],
                "figcaption": CAPTIONS[draft_id][1],
            }
        )
    (ROOT / "image_assets.json").write_text(
        json.dumps(meta_out, indent=2) + "\n", encoding="utf-8"
    )
    print(f"wrote {len(meta_out)} assets to {IMAGES}")


if __name__ == "__main__":
    main()
