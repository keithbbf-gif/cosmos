#!/usr/bin/env python3
"""Fetch license-cleared Wikimedia Commons rasters for the adaptogens graphics pack."""
from __future__ import annotations

import hashlib
import json
import re
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
META = ROOT / "assets" / "images" / "_download_meta.json"

# Commons file title (File:...) -> relative path under assets/images/
DOWNLOADS: dict[str, tuple[str, str, str]] = {
    "PSM V39 D563 Ginseng.jpg": (
        "panax-in-the-bencao/psm-ginseng-1891.jpg",
        "Public domain",
        "Popular Science Monthly (1891), via Wikimedia Commons",
    ),
    "Plante de Gin-seng Pierre Jartoux 1713.jpg": (
        "panax-in-the-bencao/jartoux-ginseng-1713.jpg",
        "Public domain",
        "Pierre Jartoux (1713), via Wikimedia Commons",
    ),
    "Flore des serres v15 173a.jpg": (
        "schisandra-and-five-tastes/flore-des-serres-schisandra-1850s.jpg",
        "Public domain",
        "Louis van Houtte, Flore des serres, via Wikimedia Commons",
    ),
    "Eleutherococcus senticosus.jpg": (
        "eleuthero-as-type-specimen/doronenko-eleuthero-2006.jpg",
        "CC BY 2.5",
        "Stanislav Doronenko, via Wikimedia Commons (CC BY 2.5)",
    ),
    "Withania somnifera MHNT.BOT.2012.10.13.jpg": (
        "ashwagandha-smell-of-a-horse/mhnt-withania-2012.jpg",
        "CC BY-SA 3.0",
        "Ercé / Muséum de Toulouse, via Wikimedia Commons (CC BY-SA 3.0)",
    ),
}


def commons_direct_url(filename: str) -> str:
    encoded = urllib.parse.quote(filename.replace(" ", "_"))
    return f"https://commons.wikimedia.org/wiki/Special:FilePath/{encoded}"


def main() -> None:
    entries: list[dict] = []
    if META.exists():
        entries = json.loads(META.read_text(encoding="utf-8"))
    by_path = {e["path"]: e for e in entries}

    for commons_name, (rel, license_name, credit) in DOWNLOADS.items():
        dest = ROOT / "assets" / "images" / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        url = commons_direct_url(commons_name)
        print(f"GET {commons_name} -> {rel}")
        req = urllib.request.Request(url, headers={"User-Agent": "COSMOS-content-pack/1.0"})
        data = urllib.request.urlopen(req, timeout=120).read()
        dest.write_bytes(data)
        sha = hashlib.sha256(data).hexdigest()
        by_path[rel] = {
            "path": rel,
            "bytes": len(data),
            "sha256": sha,
            "commons": commons_name,
            "license": license_name,
            "credit": credit,
        }

    META.write_text(json.dumps(list(by_path.values()), indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {META}")


if __name__ == "__main__":
    main()
