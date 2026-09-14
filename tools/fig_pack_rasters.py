#!/usr/bin/env python3
"""Download license-clear rasters for FigRoots content packs (Commons / USDA)."""

from __future__ import annotations

import hashlib
import json
import subprocess
import urllib.parse
from pathlib import Path

UA = "FigRootsPack/1.1 (staging educational download; figroots editorial)"

# (Commons filename, path relative to pack assets/images/)
PESTS_FILES: list[tuple[str, str]] = [
    ("Fig rust caused by Cerotelium fici.jpg", "shared/rust/cerotelium-fici-leaf-cc0.jpg"),
    (
        "Fig rust, caused by Cerotelium fici - 15341424493.jpg",
        "shared/rust/cerotelium-fici-underside-cc0.jpg",
    ),
    ("Virus mosaico Higuera.jpg", "shared/mosaic/fig-mosaic-leaf-cc-by-sa.jpg"),
    (
        "Meloidogyne incognita on Solanum lycopersicum (11).jpg",
        "shared/nematodes/galled-roots-tomato-cc0.jpg",
    ),
    ("Nematode nodules.jpg", "shared/nematodes/root-knot-nodules-pd.jpg"),
    (
        "A juvenile root-knot nematode (Meloidogyne incognita) penetrates a tomato root - USDA-ARS.jpg",
        "shared/nematodes/meloidogyne-usda-ars-cc-by.jpg",
    ),
    ("Green June Beetle (Cotinis nitida).jpg", "shared/beetles/green-june-beetle-cc-by-sa.jpg"),
    ("Japanese beetle Popillia japonica.jpg", "shared/beetles/japanese-beetle-cc-by.jpg"),
    (
        "CSIRO ScienceImage 12 Tetranychus urticae Two Spotted Spider Mite.jpg",
        "shared/diagnosis/two-spotted-spider-mite-csiro.jpg",
    ),
    ("Ants collecting honeydew drops 01.jpg", "shared/diagnosis/ants-honeydew-cc.jpg"),
    (
        "Rhizomorphs (thick fungal threads) of Armillaria mellea - geograph.org.uk - 933530.jpg",
        "shared/diagnosis/armillaria-rhizomorphs-cc-by-sa.jpg",
    ),
    ("Bactrocera dorsalis.jpg", "shared/biosecurity/oriental-fruit-fly-cc.jpg"),
    ("Fig (Ficus carica) fruit halved.jpg", "shared/diagnosis/fig-fruit-halved-reference.jpg"),
    (
        "Mango fruit fly (Bactrocera dorsalis).jpg",
        "shared/biosecurity/fruit-fly-on-fruit-cc.jpg",
    ),
]

VARIETY_FILES: list[tuple[str, str]] = [
    ("Ficus_carica_L,_1771.jpg", "shared/reference/ehret-ficus-carica-1771-pd.jpg"),
    ("Pomological Watercolor POM00007441.jpg", "cultivars/celeste-usda-pom-07441-pd.jpg"),
    ("Pomological Watercolor POM00007440.jpg", "cultivars/calimyrna-usda-pom-07440-pd.jpg"),
    ("Pomological Watercolor POM00001043.jpg", "cultivars/magnolia-usda-pom-01043-pd.jpg"),
    ("Pomological Watercolor POM00001045.jpg", "cultivars/royal-black-usda-pom-01045-pd.jpg"),
    ("Pomological Watercolor POM00007443.jpg", "cultivars/kadota-type-usda-pom-07443-pd.jpg"),
    ("Pomological Watercolor POM00007410.jpg", "cultivars/mission-type-usda-pom-07410-pd.jpg"),
    ("Pomological Watercolor POM00007442.jpg", "cultivars/fig-x1-cross-section-usda-pom-07442-pd.jpg"),
    ("Pomological Watercolor POM00001044.jpg", "cultivars/nameless-usda-pom-01044-pd.jpg"),
    ("Pomological Watercolor POM00001168.jpg", "cultivars/toulousienne-usda-pom-01168-pd.jpg"),
    ("Pomological Watercolor POM00001042.jpg", "cultivars/cutting-winter-twig-usda-pom-01042-pd.jpg"),
    (
        "Johannes_Simon_Holtzbecher_-_Ficus_carica_-_Google_Art_Project.jpg",
        "shared/reference/holtzbecher-ficus-carica-pd.jpg",
    ),
]


def fetch(commons_name: str, dest: Path) -> dict:
    dest.parent.mkdir(parents=True, exist_ok=True)
    encoded = urllib.parse.quote(commons_name.replace(" ", "_"))
    url = f"https://commons.wikimedia.org/wiki/Special:FilePath/{encoded}?width=1800"
    subprocess.run(
        ["curl", "-fsSL", "-A", UA, "-o", str(dest), url],
        check=True,
    )
    data = dest.read_bytes()
    if len(data) < 1500:
        raise RuntimeError(f"too small: {dest} ({len(data)} bytes)")
    sha = hashlib.sha256(data).hexdigest()
    return {
        "commons": commons_name,
        "bytes": len(data),
        "sha256": sha,
    }


def download_pack(pack_rel: str, files: list[tuple[str, str]]) -> None:
    pack = Path(__file__).resolve().parents[1] / pack_rel
    root = pack / "assets" / "images"
    meta: list[dict] = []
    for commons, rel in files:
        dest = root / rel
        print("GET", commons, "->", dest.relative_to(pack))
        try:
            row = fetch(commons, dest)
            row["path"] = str(dest.relative_to(pack))
            meta.append(row)
        except Exception as exc:
            print("FAIL", commons, exc)
    out = root / "_download_meta.json"
    out.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    print("wrote", out, "n=", len(meta))


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "pack",
        choices=("pests", "varieties"),
        help="Which content pack to fetch rasters for",
    )
    args = parser.parse_args()
    if args.pack == "pests":
        download_pack("content/fig-pests-diseases-blog", PESTS_FILES)
    else:
        download_pack("content/fig-varieties-profiles", VARIETY_FILES)


if __name__ == "__main__":
    main()
