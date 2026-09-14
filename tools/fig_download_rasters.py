#!/usr/bin/env python3
"""Download license-clear Wikimedia rasters into assets/images/<slug>/."""

from __future__ import annotations

import hashlib
import json
import subprocess
import urllib.parse
from pathlib import Path

PACK = Path(__file__).resolve().parents[1] / "content" / "fig-history-ancient-to-today"
UA = "FigRootsHistoryPack/1.0 (staging educational download; contact figroots editorial)"

# filename on Commons, dest relative to assets/images/, home slug
FILES = [
    ("Ficus_carica_L,_1771.jpg", "syconium-botany-and-morphology/ehret-trew-1771.jpg"),
    (
        "Wall_painting_-_still_life_with_bread_and_figs_-_Herculaneum_-_Napoli_MAN_8625.jpg",
        "pompeii-gardens-fig-trees/herculaneum-man-8625.jpg",
    ),
    ("Pompeii_-_Casa_del_Frutteto_-_Fig_tree.jpg", "pompeii-gardens-fig-trees/casa-del-frutteto-fig.jpg"),
    ("Bartolomeo_Bimbi_(figs).jpg", "renaissance-still-life-figs/bimbi-figs-1696.jpg"),
    (
        "Johannes_Simon_Holtzbecher_-_Ficus_carica_-_Google_Art_Project.jpg",
        "renaissance-still-life-figs/holtzbecher-ficus-carica.jpg",
    ),
    ("EB1911_Moraceae_-_Ficus_carica.jpg", "syconium-botany-and-morphology/eb1911-ficus-carica.jpg"),
    (
        "Jacques_Le_Moyne_de_Morgues._Ficus_carica_L.jpg",
        "california-mission-fig-spread/le-moyne-ficus-carica.jpg",
    ),
    (
        "Brooklyn_Museum_-_Nathaniel_Under_the_Fig_Tree_(Nathana%C3%ABl_sous_le_figuier)_-_James_Tissot_-_overall.jpg",
        "figs-in-hebrew-bible/tissot-nathaniel-under-fig.jpg",
    ),
    (
        "Brooklyn_Museum_-_The_Vine_Dresser_and_the_Fig_Tree_(Le_vigneron_et_le_figuier)_-_James_Tissot.jpg",
        "new-testament-fig-parables/tissot-vine-dresser-fig.jpg",
    ),
    (
        "A_fig_plant_(Ficus_carica);_fruiting_stem_and_halved_fruit._Wellcome_V0044761.jpg",
        "figs-in-greek-roman-medicine/wellcome-v0044761.jpg",
    ),
    ("Illustration_Ficus_carica0.jpg", "islamic-medical-traditions-fig/kohler-ficus-carica.jpg"),
]


def fetch(commons_name: str, dest: Path) -> dict:
    dest.parent.mkdir(parents=True, exist_ok=True)
    # Special:FilePath follows to current hash path
    url = "https://commons.wikimedia.org/wiki/Special:FilePath/" + commons_name
    if "?" not in url:
        url = url + "?width=1800"
    else:
        url = url + "&width=1800"
    cmd = [
        "curl",
        "-fsSL",
        "-A",
        UA,
        "-o",
        str(dest),
        url,
    ]
    subprocess.run(cmd, check=True)
    data = dest.read_bytes()
    if len(data) < 2000:
        raise RuntimeError(f"too small: {dest} ({len(data)} bytes)")
    sha = hashlib.sha256(data).hexdigest()
    return {"path": str(dest.relative_to(PACK)), "bytes": len(data), "sha256": sha, "commons": commons_name}


def main() -> None:
    root = PACK / "assets" / "images"
    meta = []
    for commons, rel in FILES:
        dest = root / rel
        print("GET", commons, "->", dest)
        try:
            meta.append(fetch(commons, dest))
        except Exception as e:
            print("FAIL", commons, e)
    out = PACK / "assets" / "images" / "_download_meta.json"
    out.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print("wrote", out, "n=", len(meta))


if __name__ == "__main__":
    main()
