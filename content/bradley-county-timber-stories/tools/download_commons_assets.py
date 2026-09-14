#!/usr/bin/env python3
"""Fetch license-cleared images for Bradley County timber stories pack."""
from __future__ import annotations

import hashlib
import json
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
META = ROOT / "assets" / "images" / "_download_meta.json"

DOWNLOADS: dict[str, tuple[str, str, str, str]] = {
    "Saw mill, North Bend Mill & Lumber Company, North Bend, ca 1920 (KINSEY 2449).jpeg": (
        "mill-era-reference/kinsey-sawmill-north-bend-1920.jpg",
        "Public domain",
        "Darius Kinsey / University of Washington Libraries, via Wikimedia Commons",
        "Sawmill interior, North Bend, Washington, ca. 1920 — era comparison, not Warren, Arkansas.",
    ),
    "Mill crew, North Bend Mill & Lumber Company, North Bend, ca 1920 (KINSEY 2447).jpeg": (
        "mill-era-reference/kinsey-mill-crew-north-bend-1920.jpg",
        "Public domain",
        "Darius Kinsey / University of Washington Libraries, via Wikimedia Commons",
        "Mill crew portrait, North Bend, Washington, ca. 1920 — illustrative of mill-town labor, not a named Warren mill.",
    ),
    "Bradco courthouse3.jpg": (
        "warren-place/bradley-county-courthouse-warren.jpg",
        "CC BY-SA 3.0",
        "Photo: Bradco, via Wikimedia Commons (CC BY-SA 3.0)",
        "Bradley County Courthouse, Warren, Arkansas.",
    ),
    "Map of Arkansas highlighting Bradley County.svg": (
        "warren-place/bradley-county-map.svg",
        "Public domain",
        "Wikimedia Commons contributors",
        "Bradley County location within Arkansas — schematic map.",
    ),
}


def commons_url(filename: str) -> str:
    return "https://commons.wikimedia.org/wiki/Special:FilePath/" + urllib.parse.quote(
        filename.replace(" ", "_")
    )


def main() -> None:
    by_path: dict[str, dict] = {}
    if META.exists():
        by_path = {e["path"]: e for e in json.loads(META.read_text(encoding="utf-8"))}

    for commons_name, (rel, license_name, credit, caption_note) in DOWNLOADS.items():
        dest = ROOT / "assets" / "images" / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        req = urllib.request.Request(commons_url(commons_name), headers={"User-Agent": "COSMOS/1.0"})
        data = urllib.request.urlopen(req, timeout=120).read()
        dest.write_bytes(data)
        by_path[rel] = {
            "path": rel,
            "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
            "commons": commons_name,
            "license": license_name,
            "credit": credit,
            "caption_note": caption_note,
        }
        print("saved", rel)

    META.write_text(json.dumps(list(by_path.values()), indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
