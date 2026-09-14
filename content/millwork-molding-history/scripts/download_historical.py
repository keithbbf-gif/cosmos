#!/usr/bin/env python3
"""Fetch PD/CC historical millwork plates from Wikimedia Commons."""

from __future__ import annotations

import json
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"

# slug -> Commons file title (without File: prefix)
PLATES: dict[str, dict[str, str]] = {
    "asher-benjamin-companion": {
        "file": "The American builder's companion - or, A system of architecture, particularly adapted to the present style of building; illustrated with seventy copperplate engravings (1827) (14780944062).jpg",
        "alt": "Copperplate of moulding profiles from Asher Benjamin's American Builder's Companion (1827 edition).",
        "caption": (
            "Scan from Asher Benjamin, *The American Builder's Companion* (Boston, 6th ed., 1827). "
            "Public domain. Wikimedia Commons / Internet Archive."
        ),
    },
    "gibbs-swan-anglo-palladian": {
        "file": "The British architect; or, the builder's treasury of staircases... MET DP105201.jpg",
        "alt": "Engraved plate from Abraham Swan's British Architect pattern book, Anglo-Palladian moulding and stair details.",
        "caption": (
            "Abraham Swan, *The British Architect* (London, 1745), plate scan via The Metropolitan Museum of Art "
            "(Open Access). CC0 1.0 where marked on Commons."
        ),
    },
    "stuart-revett-greek-turn": {
        "file": "Outlines of the preceding plate with the dimensions - Stuart James & Revett Nicholas - 1816.jpg",
        "alt": "Measured outline plate from Stuart and Revett's Antiquities of Athens, Greek moulding dimensions.",
        "caption": (
            "James Stuart and Nicholas Revett, *The Antiquities of Athens* (London, 1762–1816 series). "
            "Public domain. Wikimedia Commons."
        ),
    },
    "vignola-palladio-rulebooks": {
        "file": "The Architecture of A. Palladio in Four Books containing a Short Treatise on the Five Orders (L'Architecture de A. Palladio en quatre livres... - Il quattro libri dell'architettura) MET DP109544.jpg",
        "alt": "Palladio Four Books woodcut of classical orders and moulding rules, pattern-book plate.",
        "caption": (
            "Andrea Palladio, *I quattro libri dell'architettura* (Venice, 1570), plate via The Metropolitan "
            "Museum of Art (Open Access). CC0 1.0 where marked on Commons."
        ),
    },
    "eight-regular-moldings": {
        "file": "The American builder's companion - or, A system of architecture, particularly adapted to the present style of building; illustrated with seventy copperplate engravings (1827) (14781023322).jpg",
        "alt": "Benjamin Companion copperplate of classical moulding sections—the eight regular profiles in American shops.",
        "caption": (
            "Asher Benjamin, *The American Builder's Companion* (1827), profile plate. Public domain. "
            "Wikimedia Commons / Internet Archive."
        ),
    },
    "gothic-medieval-moldings": {
        "file": "Examples of Gothic architecture - selected from various antient edifices in England, consisting of plans, elevations, sections, and parts at large accompanied by historical and descriptive accounts (14596653208).jpg",
        "alt": "Gothic moulding and tracery plate from Pugin's Examples of Gothic Architecture.",
        "caption": (
            "A. W. N. Pugin, *Examples of Gothic Architecture* (London, 1836). Public domain. "
            "Wikimedia Commons / Internet Archive."
        ),
    },
}


def commons_url(file_title: str) -> str:
    api = (
        "https://commons.wikimedia.org/w/api.php?"
        + urllib.parse.urlencode(
            {
                "action": "query",
                "titles": f"File:{file_title}",
                "prop": "imageinfo",
                "iiprop": "url",
                "iiurlwidth": "1200",
                "format": "json",
            }
        )
    )
    req = urllib.request.Request(
        api,
        headers={"User-Agent": "cosmos-millwork-pack/1.0 (educational; github.com/keithbbf-gif/cosmos)"},
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode())
    pages = data["query"]["pages"]
    page = next(iter(pages.values()))
    if "missing" in page:
        raise FileNotFoundError(file_title)
    info = page["imageinfo"][0]
    return info.get("thumburl") or info["url"]


def main() -> None:
    for slug, meta in PLATES.items():
        dest_dir = ASSETS / slug
        dest_dir.mkdir(parents=True, exist_ok=True)
        url = commons_url(meta["file"])
        img_path = dest_dir / "historical-plate.jpg"
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "cosmos-millwork-pack/1.0 (educational; github.com/keithbbf-gif/cosmos)"},
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            img_path.write_bytes(resp.read())
        meta_path = dest_dir / "historical-plate.json"
        meta_path.write_text(
            json.dumps(
                {
                    "source": f"https://commons.wikimedia.org/wiki/File:{meta['file']}",
                    "license": "Public domain (published work; verify on Commons before print)",
                    "alt": meta["alt"],
                    "caption": meta["caption"],
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        print(f"ok {slug} -> {img_path} ({len(img_path.read_bytes())} bytes)")


if __name__ == "__main__":
    main()
