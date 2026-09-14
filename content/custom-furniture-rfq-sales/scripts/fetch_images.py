#!/usr/bin/env python3
"""Download raster assets listed in image_assets.json (skip SVG)."""

from __future__ import annotations

import json
import ssl
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
MANIFEST = ROOT / "image_assets.json"

CTX = ssl.create_default_context()
USER_AGENT = "COSMOS-content-fetch/1.0 (custom-furniture-rfq-sales; educational)"


def fetch(url: str, dest: Path) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, context=CTX, timeout=120) as resp:
        data = resp.read()
    if len(data) < 500 and dest.suffix.lower() in {".jpg", ".jpeg", ".png"}:
        raise RuntimeError(f"tiny download {len(data)} bytes for {url}")
    if len(data) > 15_000_000:
        raise RuntimeError(f"download too large ({len(data)} bytes) — use a Commons thumb URL")
    dest.write_bytes(data)


def main() -> int:
    if not MANIFEST.is_file():
        print("FAIL missing image_assets.json")
        return 1
    assets = json.loads(MANIFEST.read_text(encoding="utf-8"))
    ASSETS.mkdir(parents=True, exist_ok=True)
    seen_urls: dict[str, str] = {}
    errors: list[str] = []
    for a in assets:
        fname = a["file"]
        dest = ASSETS / fname
        if fname.lower().endswith(".svg"):
            continue
        url = a.get("download_url") or ""
        if not url:
            if dest.is_file() and dest.stat().st_size > 500:
                print("skip local", fname)
                continue
            errors.append(f"{fname}: no download_url and no local file")
            continue
        if url in seen_urls and dest.is_file():
            continue
        seen_urls[url] = fname
        try:
            if dest.is_file() and dest.stat().st_size > 500:
                print("skip", fname)
                continue
            print("fetch", fname)
            fetch(url, dest)
            time.sleep(1.5)
        except Exception as exc:  # noqa: BLE001 — fetch script reports all failures
            errors.append(f"{fname}: {exc}")
    if errors:
        print("FAIL")
        for e in errors:
            print("-", e)
        return 1
    print(f"PASS assets dir={ASSETS}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
