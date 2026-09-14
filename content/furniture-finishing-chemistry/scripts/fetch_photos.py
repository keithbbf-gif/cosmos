#!/usr/bin/env python3
"""Download PD/CC photos listed in ffc_photo_slots.json from Wikimedia Commons."""

from __future__ import annotations

import json
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SLOTS = json.loads((Path(__file__).resolve().parent / "ffc_photo_slots.json").read_text(encoding="utf-8"))


def commons_url(filename: str) -> str:
    encoded = urllib.parse.quote(filename.replace(" ", "_"))
    return f"https://commons.wikimedia.org/wiki/Special:FilePath/{encoded}"


def main() -> None:
    for slug, slot in SLOTS.items():
        if not slot.get("file"):
            continue
        dest = ROOT / slot["path"]
        dest.parent.mkdir(parents=True, exist_ok=True)
        url = commons_url(slot["file"])
        req = urllib.request.Request(url, headers={"User-Agent": "COSMOS-ffc-graphics/1.0"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = resp.read()
        dest.write_bytes(data)
        try:
            from PIL import Image
            import io

            im = Image.open(io.BytesIO(data)).convert("RGB")
            if im.width > 1280:
                im = im.resize((1280, int(im.height * 1280 / im.width)), Image.Resampling.LANCZOS)
            buf = io.BytesIO()
            im.save(buf, "JPEG", quality=85, optimize=True)
            dest.write_bytes(buf.getvalue())
        except ImportError:
            pass
        print(f"{slug}: {dest.name} ({len(data)} bytes)")


if __name__ == "__main__":
    main()
