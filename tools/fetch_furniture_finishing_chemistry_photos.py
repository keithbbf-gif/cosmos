#!/usr/bin/env python3
"""Download PD / CC-licensed photos for furniture-finishing-chemistry (see RIGHTS.md)."""

from __future__ import annotations

import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PHOTOS = ROOT / "content" / "furniture-finishing-chemistry" / "photos"

# filename -> direct Wikimedia Commons URL (verified via Commons API 2026-09-14)
DOWNLOADS: dict[str, str] = {
    "oak-end-grain-quartersawn.jpg": (
        "https://upload.wikimedia.org/wikipedia/commons/2/26/End_grain_cutting_board.jpg"
    ),
    "walnut-pore-close.jpg": (
        "https://upload.wikimedia.org/wikipedia/commons/d/d3/End_Grain_-_geograph.org.uk_-_1179147.jpg"
    ),
    "paint-brushes-studio.jpg": (
        "https://upload.wikimedia.org/wikipedia/commons/3/39/Paintbrushes.jpg"
    ),
    "teak-wood-texture.jpg": (
        "https://upload.wikimedia.org/wikipedia/commons/1/11/Teak_wood_inside_Nilambur_teak_museum.jpg"
    ),
    "linseed-oil-bottle.jpg": (
        "https://upload.wikimedia.org/wikipedia/commons/e/ef/F%C3%A4rgriket_raw_linseed_oil%2C_back.jpg"
    ),
    "shellac-flakes.jpg": (
        "https://upload.wikimedia.org/wikipedia/commons/0/07/Shellac_flakes_closeup.JPG"
    ),
    "waterborne-latex-paint.jpg": (
        "https://upload.wikimedia.org/wikipedia/commons/0/06/Applying_Varnish_on_Unfinished_Violin.jpg"
    ),
    "milk-paint-brush.jpg": (
        "https://upload.wikimedia.org/wikipedia/commons/4/40/Encaustic_painting_on_wood_panel.jpg"
    ),
    "orbital-sander-wood.jpg": (
        "https://upload.wikimedia.org/wikipedia/commons/e/e0/Random_orbit_sander.jpg"
    ),
    "dining-table-wood.jpg": (
        "https://upload.wikimedia.org/wikipedia/commons/5/58/Hal_Blakeley%2C_Wooden_Table%2C_c._1953%2C_NGA_20059.jpg"
    ),
}


def main() -> None:
    PHOTOS.mkdir(parents=True, exist_ok=True)
    for name, url in DOWNLOADS.items():
        dest = PHOTOS / name
        print(f"fetch {name}")
        req = urllib.request.Request(url, headers={"User-Agent": "cosmos-content-bot/1.0"})
        for attempt in range(5):
            try:
                with urllib.request.urlopen(req, timeout=60) as resp:
                    data = resp.read()
                break
            except urllib.error.HTTPError as exc:
                if exc.code == 429 and attempt < 4:
                    time.sleep(2 ** attempt)
                    continue
                raise
        time.sleep(1.0)
        if len(data) < 500:
            raise SystemExit(f"Suspiciously small download for {name}")
        dest.write_bytes(data)
    print(f"Wrote {len(DOWNLOADS)} photos to {PHOTOS}")


if __name__ == "__main__":
    main()
