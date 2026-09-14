#!/usr/bin/env python3
"""Download CC/PD product photos from Wikimedia Commons into assets/<slug>/."""

from __future__ import annotations

import json
import urllib.parse
import urllib.request
from pathlib import Path

from pack_data import ARTICLES, PACK

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
UA = "COSMOSChipMagazineBot/1.0 (staged editorial pack)"

# commons title -> local filename (must match build_pack_data PHOTO values)
COMMONS: dict[str, str] = {
    "File:KL NVIDIA Geforce 256.jpg": "geforce-256.jpg",
    "File:3dfx Voodoo2.jpg": "3dfx-voodoo2.jpg",
    "File:ATI-Radeon-9700-Pro.png": "ati-radeon-9700-pro.png",
    "File:NVIDIA GeForce 8800 GTX Board.jpg": "geforce-8800-gtx-board.jpg",
    "File:Tesla-NVIDIA GPU cluster (3706444821).jpg": "tesla-gpu-cluster.jpg",
    "File:NVIDIA@40nm@Fermi@GF110@GeForce GTX 580@UA10B338 1041A1 N2Y540.000 GF110-375-A1 DSC06727 (28114557571).jpg": "gtx-580-die.jpg",
    "File:Nvidia DGX front view dllu.jpg": "nvidia-dgx-front.jpg",
    "File:TPU v4.png": "tpu-v4.png",
}

# slug -> local filename
SLUG_PHOTO = {a["slug"]: a["photo"] for a in ARTICLES if a.get("photo")}


def commons_url(title: str) -> tuple[str, str]:
    qtitle = urllib.parse.quote(title)
    url = (
        f"https://commons.wikimedia.org/w/api.php?action=query&titles={qtitle}"
        f"&prop=imageinfo&iiprop=url|extmetadata&format=json"
    )
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    data = json.load(urllib.request.urlopen(req, timeout=60))
    for pid, page in data["query"]["pages"].items():
        if pid == "-1":
            raise SystemExit(f"commons file not found: {title}")
        ii = page["imageinfo"][0]
        meta = ii["extmetadata"]
        lic = meta.get("LicenseShortName", {}).get("value", "unknown")
        return ii["url"].split("?")[0], lic
    raise SystemExit(f"no imageinfo for {title}")


def main() -> None:
    local_to_commons = {v: k for k, v in COMMONS.items()}
    for slug, local in SLUG_PHOTO.items():
        commons_title = local_to_commons.get(local)
        if not commons_title:
            raise SystemExit(f"missing commons mapping for {local}")
        url, lic = commons_url(commons_title)
        dest_dir = ASSETS / slug
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / local
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        dest.write_bytes(urllib.request.urlopen(req, timeout=120).read())
        print(f"{slug}: {dest.name} ({lic})")
    print(f"photos for {PACK} — register in RIGHTS.md")


if __name__ == "__main__":
    main()
