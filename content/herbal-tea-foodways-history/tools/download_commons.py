#!/usr/bin/env python3
"""Stage cleared Commons rasters for herbal-tea-foodways-history."""
from __future__ import annotations

import hashlib
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMG = ROOT / "assets" / "images"
META = IMG / "_download_meta.json"
UA = "COSMOS-herbal-tea-foodways/1.0 (educational; contact via repo)"

# Wikimedia File: page title (with spaces) -> local path under assets/images/
FILES: dict[str, str] = {
    "Hibiscus sabdariffa fruits.jpg": "food/hibiscus-sabdariffa-calyces.jpg",
    "Dried hibiscus flowers.jpg": "food/dried-hibiscus-calyces.jpg",
    "Rooibos (Aspalathus linearis).jpg": "botanical/rooibos-plant.jpg",
    "Camellia sinensis - Köhler–s Medizinal-Pflanzen-025.jpg": "botanical/camellia-sinensis-kohler.jpg",
    "Mate gourd (calabash) and bombilla held against a European Holly (Ilex aquifolium) bush.jpg": "vessels/mate-gourd-bombilla.jpg",
    "Chamomile@original size.jpg": "botanical/chamomile-flowers.jpg",
    "Barley.jpg": "food/barley-grains.jpg",
    "Chrysanthemum tea (20240131).jpg": "food/chrysanthemum-tea-glass.jpg",
    "Mentha viridis - Köhler–s Medizinal-Pflanzen-096.jpg": "botanical/mint-spearmint-kohler.jpg",
    "Ocimum tenuiflorum 2.jpg": "botanical/tulsi-ocimum.jpg",
    "Sassafras Leaf.jpg": "botanical/sassafras-leaves.jpg",
    "Ilex paraguariensis - Köhler–s Medizinal-Pflanzen-074.jpg": "botanical/yerba-mate-kohler.jpg",
    "Sambucus nigra0.jpg": "botanical/elderflower-sambucus.jpg",
    "Tilia cordata (New Belgrade, Serbia) 01.jpg": "botanical/linden-tilia-inflorescence.jpg",
    "Tea bags.jpg": "aisle/tea-bags-envelope.jpg",
    "Dried barley tea (1).jpg": "food/dried-barley-tea.jpg",
    "Clitoria ternatea.jpg": "botanical/butterfly-pea-flower.jpg",
    "2020 year. Herbarium. Chamerion angustifolium. img-006.jpg": "botanical/fireweed-herbarium.jpg",
    "Sideritis scardica - Botanischer Garten München-Nymphenburg - DSC07698.JPG": "botanical/greek-mountain-tea-sideritis.jpg",
    "Cyclopia genistoides Taub104c.png": "botanical/honeybush-cyclopia-plate.png",
    "Rhododendron groenlandicum.jpg": "botanical/labrador-tea-rhododendron.jpg",
    "Monarda didyma flower.jpg": "botanical/oswego-bee-balm-monarda.jpg",
    "Hojas de Guayusa (Ilex guayusa).jpg": "botanical/guayusa-leaves.jpg",
    "Liotard, Jean-Étienne - Still Life- Tea Set - Google Art Project.jpg": "historic/liotard-tea-set-still-life.jpg",
    "Boricha (barley tea).jpg": "food/boricha-barley-tea.jpg",
    "Camomille sauvage (Matricaria chamomilla), coquelicots (Papaver rhoeas) au bord d'un champ d'orge (Hordeum vulgare).jpg": "garden/chamomile-field.jpg",
    "Pieter Gerritsz. van Roestraten (1629-1630-1700) - Still Life with Tea Cups - VIS.305 - Sheffield Galleries and Museums Trust.jpg": "historic/household-tea-still-life-roestraten.jpg",
    "Ilex vomitoria, by Mary Vaux Walcott.jpg": "botanical/yaupon-holly-walcott.jpg",
    "A Large Pack of Chrysanthemum tea (MY and SG).jpg": "aisle/herbal-tea-retail-pack.jpg",
}


def api_image_url(file_title: str) -> tuple[str, str, str]:
    """Return download URL, license short name, credit artist."""
    params = {
        "action": "query",
        "titles": file_title,
        "prop": "imageinfo",
        "iiprop": "url|extmetadata",
        "format": "json",
    }
    url = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode())
    pages = data["query"]["pages"]
    page = next(iter(pages.values()))
    if "missing" in page:
        raise FileNotFoundError(file_title)
    ii = page["imageinfo"][0]
    raw_url = ii["url"].split("?")[0]
    ext = ii.get("extmetadata") or {}
    lic = ext.get("LicenseShortName", {}).get("value", "See Commons")
    artist = re.sub(r"<[^>]+>", "", ext.get("Artist", {}).get("value", "See Commons file page"))
    return raw_url, lic, artist.strip()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def download_url(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=120) as resp:
        return resp.read()


def main() -> int:
    IMG.mkdir(parents=True, exist_ok=True)
    meta: dict[str, object] = {"files": {}}
    if META.exists():
        try:
            meta = json.loads(META.read_text(encoding="utf-8"))
            if "files" not in meta:
                meta["files"] = {}
        except json.JSONDecodeError:
            meta = {"files": {}}
    errors: list[str] = []
    for title, rel in FILES.items():
        file_title = f"File:{title}"
        dest = IMG / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists() and dest.stat().st_size > 0 and META.exists():
            try:
                existing = json.loads(META.read_text(encoding="utf-8"))
                if rel in existing.get("files", {}):
                    print(f"SKIP {rel}")
                    continue
            except json.JSONDecodeError:
                pass
        try:
            time.sleep(1.2)
            url, lic, artist = api_image_url(file_title)
            time.sleep(0.5)
            data = download_url(url)
            dest.write_bytes(data)
            commons_page = "https://commons.wikimedia.org/wiki/" + urllib.parse.quote(
                file_title.replace(" ", "_"), safe=":/"
            )
            meta["files"][rel] = {
                "commons_title": title,
                "commons_page": commons_page,
                "license": lic,
                "credit": artist[:200] if artist else "See Commons file page",
                "sha256": sha256(data),
                "bytes": len(data),
            }
            print(f"OK {rel}")
        except OSError as exc:
            errors.append(f"{title}: {exc}")
            print(f"FAIL {title}: {exc}")

    META.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    if errors:
        print(f"{len(errors)} failures")
        return 1
    print(f"staged {len(meta['files'])} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
