#!/usr/bin/env python3
"""Resolve, download, and verify Wikimedia Commons images for HFRH drafts."""

from __future__ import annotations

import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REGISTRY = ROOT / "images" / "registry.json"
OUT = ROOT / "images"
API = "https://commons.wikimedia.org/w/api.php"

# Search queries when the suggested filename is missing or wrong.
FALLBACK_SEARCH: dict[str, str] = {
    "00-01-why-this-history.md": "Grand Rapids furniture factory",
    "00-02-who-is-talking.md": "woodworking shop bench",
    "00-03-four-doors.md": "Marshall Field building Chicago",
    "00-04-stolen-words.md": "handmade sign craft",
    "01-05-america-house.md": "Museum of Arts and Design New York",
    "01-06-acc-fairs.md": "craft fair booth",
    "01-07-gallery-consignment.md": "art gallery interior",
    "01-08-studio-furniture-as-art.md": "Wharton Esherick Studio",
    "01-09-table-as-bad-gallery-object.md": "dining table chairs",
    "01-10-jury-and-booth.md": "craft fair outdoor",
    "01-11-what-galleries-taught.md": "pottery gallery display",
    "01-12-gallery-to-showroom-handoff.md": "furniture showroom",
    "02-13-to-the-trade.md": "interior design showroom",
    "02-14-design-centers.md": "Merchandise Mart Chicago",
    "02-15-getting-the-line-in.md": "wood finish samples",
    "02-16-territory-exclusivity.md": "showroom floor plan",
    "02-17-net-list-multiplier.md": "price tags retail",
    "02-18-sample-floor.md": "dining table showroom",
    "02-19-paper-trail.md": "purchase order form vintage",
    "02-20-cold-calling-designers.md": "rotary telephone",
    "02-21-own-trucks.md": "furniture delivery truck",
    "03-22-high-point.md": "High Point North Carolina",
    "03-23-market-order-vs-cart.md": "order form wholesale",
    "03-24-tear-sheets.md": "furniture catalog vintage",
    "04-25-ebay-yahoo.md": "IBM PC 1980s",
    "04-26-photography-as-showroom.md": "product photography studio lights",
    "04-27-freight-is-not-shipping.md": "semi trailer truck highway",
    "05-28-etsy-2005.md": "Brooklyn flea market",
    "05-29-jewelry-economics.md": "handmade jewelry display",
    "05-30-handmade-wars.md": "craft market handmade",
    "05-31-three-buckets.md": "antique furniture shop",
    "05-32-fees-and-ads.md": "cash register vintage",
    "05-33-etsy-wholesale.md": "wholesale trade showroom",
    "06-34-overstock-partners.md": "warehouse shelving pallets",
    "06-35-csn-wayfair.md": "distribution center loading dock",
    "06-36-dropship-job.md": "warehouse conveyor boxes",
    "06-37-high-point-recruitment.md": "trade show exhibition hall",
    "06-38-sku-flood.md": "barcode scanner warehouse",
    "06-39-map-private-label.md": "price sticker retail",
    "06-40-returns-chargebacks.md": "returned packages warehouse",
    "06-41-walking-away.md": "closed store shutter",
    "07-42-four-prices.md": "furniture store price tags",
    "07-43-american-made.md": "Made in USA label",
    "07-44-series-close.md": "woodworking workbench hand plane",
}


UA = "BBF-HFRH/1.0 (https://github.com/keithbbf-gif/cosmos; keith.bbf@gmail.com) Python-urllib"


def api(params: dict) -> dict:
    q = urllib.parse.urlencode({**params, "format": "json"})
    req = urllib.request.Request(f"{API}?{q}", headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.load(resp)


def file_info(title: str) -> dict | None:
    data = api(
        {
            "action": "query",
            "titles": title,
            "prop": "imageinfo",
            "iiprop": "url|extmetadata|size|mime",
        }
    )
    pages = data.get("query", {}).get("pages", {})
    page = next(iter(pages.values()))
    if "missing" in page:
        return None
    info = page.get("imageinfo", [{}])[0]
    meta = info.get("extmetadata", {})
    license_short = meta.get("LicenseShortName", {}).get("value", "")
    artist = meta.get("Artist", {}).get("value", "")
    credit = meta.get("Credit", {}).get("value", "")
    desc = meta.get("ImageDescription", {}).get("value", "")
    return {
        "title": title,
        "url": info.get("url"),
        "mime": info.get("mime"),
        "width": info.get("width"),
        "height": info.get("height"),
        "license": re.sub(r"<[^>]+>", "", license_short),
        "artist": re.sub(r"<[^>]+>", "", artist),
        "credit": re.sub(r"<[^>]+>", "", credit),
        "description": re.sub(r"<[^>]+>", "", desc),
        "page": f"https://commons.wikimedia.org/wiki/{urllib.parse.quote(title.replace(' ', '_'))}",
    }


def search_file(query: str) -> dict | None:
    data = api(
        {
            "action": "query",
            "generator": "search",
            "gsrsearch": f"filetype:bitmap {query}",
            "gsrnamespace": "6",
            "gsrlimit": "8",
            "prop": "imageinfo",
            "iiprop": "url|extmetadata|mime",
        }
    )
    pages = data.get("query", {}).get("pages", {})
    for page in sorted(pages.values(), key=lambda p: int(p.get("index", 0))):
        info = page.get("imageinfo", [{}])[0]
        meta = info.get("extmetadata", {})
        lic = meta.get("LicenseShortName", {}).get("value", "").lower()
        if not info.get("url"):
            continue
        if not license_ok(lic):
            continue
        title = page.get("title", "")
        if not title.startswith("File:"):
            continue
        return file_info(title)
    return None


def license_ok(license_short: str) -> bool:
    lic = (license_short or "").lower()
    if not lic:
        return False
    if "non-free" in lic or "fair use" in lic:
        return False
    if "by-nc" in lic or "by-nd" in lic:
        return False
    return any(
        token in lic
        for token in (
            "public domain",
            "cc0",
            "cc by",
            "cc-by",
            "no restrictions",
            "pd",
        )
    )


def pick_commons(suggested: str, draft: str) -> dict | None:
    title = f"File:{suggested}" if not suggested.startswith("File:") else suggested
    info = file_info(title)
    if info and info.get("url") and license_ok(info.get("license", "")):
        return info
    query = FALLBACK_SEARCH.get(draft, suggested.replace("_", " "))
    found = search_file(query)
    if found and license_ok(found.get("license", "")):
        return found
    return None


def download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=120) as resp:
        dest.write_bytes(resp.read())


def main() -> int:
    reg = json.loads(REGISTRY.read_text(encoding="utf-8"))
    rights_rows: list[dict] = []
    errors: list[str] = []

    for draft, spec in reg["drafts"].items():
        dest = OUT / spec["file"]
        info = pick_commons(spec.get("commons", ""), draft)
        if not info or not info.get("url"):
            errors.append(f"{draft}: no commons file")
            continue
        if not license_ok(info.get("license", "")):
            errors.append(f"{draft}: license not PD/CC: {info.get('license')}")
            continue
        try:
            download(info["url"], dest)
        except OSError as exc:
            errors.append(f"{draft}: download failed: {exc}")
            continue
        rights_rows.append(
            {
                "draft": draft,
                "local": spec["file"],
                "commons": info["title"],
                "page": info["page"],
                "license": info["license"],
                "artist": info.get("artist", ""),
            }
        )
        print(f"OK {draft} -> {spec['file']} ({info['title']})")

    rights_path = ROOT / "RIGHTS.md"
    lines = [
        "# Image rights — handmade furniture retail history",
        "",
        "Historical and retail photographs sourced from **Wikimedia Commons** for the BBF channel draft pack. "
        "No AI-generated faces. Verify license on the file page before reuse outside this series.",
        "",
        "| Draft | Local file | Commons file | License | Artist / credit |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in rights_rows:
        artist = (row["artist"] or "").replace("|", "/")[:120]
        lines.append(
            f"| `{row['draft']}` | `{row['local']}` | [{row['commons']}]({row['page']}) | {row['license']} | {artist} |"
        )
    lines.extend(
        [
            "",
            "## Reuse",
            "",
            "- Respect the license on each Commons file page (attribution required for CC BY variants).",
            "- Figures in `drafts/` use relative paths `../images/<file>` with SEO `alt` text and editorial `figcaption` copy.",
            "- Do not substitute stock or AI imagery without updating this file.",
            "",
        ]
    )
    rights_path.write_text("\n".join(lines), encoding="utf-8")

    if errors:
        print("ERRORS:")
        for err in errors:
            print(f"- {err}")
        return 1
    print(f"Downloaded {len(rights_rows)} images; wrote {rights_path.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
