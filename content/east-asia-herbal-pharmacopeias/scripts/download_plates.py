#!/usr/bin/env python3
"""Download cleared bencao plates from Wikimedia Commons (license-checked list in RIGHTS.md)."""

from __future__ import annotations

import hashlib
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets" / "plates"

# Commons file titles → repo-relative paths (no faces; botanical / book plates only).
PLATES: list[dict[str, str]] = [
    {
        "commons": "Bencaotu-jing-Illustrated-Canon-of-Materia.png",
        "path": "china/su-song-tujing-line-plate.png",
        "figure_id": "eahp.plates.tujing-line",
    },
    {
        "commons": "Chinese Materia Medica illustration, Ming; Huangqin Wellcome L0039301.jpg",
        "path": "china/ming-huangqin-scutellaria-wellcome.jpg",
        "figure_id": "eahp.plates.ming-huangqin",
    },
    {
        "commons": "Chinese Materia Medica illustration, Ming; Sichuan honey Wellcome L0039305.jpg",
        "path": "china/ming-sichuan-honey-trace-wellcome.jpg",
        "figure_id": "eahp.plates.ming-honey-trace",
    },
    {
        "commons": "Chinese Materia medica, C17; Plant drugs, Wellcome L0039345.jpg",
        "path": "china/c17-plant-drugs-wellcome.jpg",
        "figure_id": "eahp.plates.c17-plant-grid",
    },
    {
        "commons": "First edition of Bencao Gangmu; Chinese, 1590 Wellcome L0039328.jpg",
        "path": "china/gangmu-jinjing-title-page-wellcome.jpg",
        "figure_id": "eahp.plates.gangmu-jinjing-title",
    },
    {
        "commons": "Bencao Gangmu -- Ming materia medica, Trifoliate orange, etc. Wellcome L0039330.jpg",
        "path": "china/gangmu-woodcut-plants-lijianyuan-wellcome.jpg",
        "figure_id": "eahp.plates.gangmu-woodcut-plants",
    },
    {
        "commons": "Ishinpo Nakarai.jpg",
        "path": "japan/ishinpo-nakarai-heian-copy.jpg",
        "figure_id": "eahp.plates.ishinpo-nakarai",
    },
    {
        "commons": "Yamato Honzo.jpg",
        "path": "japan/yamato-honzo-opening-plate.jpg",
        "figure_id": "eahp.plates.yamato-honzo",
    },
    {
        "commons": "Donguibogam (one page of one book).jpg",
        "path": "korea/donguibogam-printed-page.jpg",
        "figure_id": "eahp.plates.donguibogam-page",
    },
]

API = "https://commons.wikimedia.org/w/api.php"


def commons_url(title: str) -> str:
    params = (
        "action=query&format=json&prop=imageinfo&iiprop=url"
        f"&titles=File:{urllib.parse.quote(title.replace(' ', '_'), safe='')}"
    )
    req = urllib.request.Request(
        f"{API}?{params}",
        headers={"User-Agent": "COSMOS-eahp-plates/1.0 (cloud-agent; commons download)"},
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.load(resp)
    pages = data["query"]["pages"]
    page = next(iter(pages.values()))
    if "missing" in page:
        raise SystemExit(f"Commons file not found: {title}")
    return page["imageinfo"][0]["url"].split("?")[0]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    meta: list[dict[str, object]] = []
    for row in PLATES:
        dest = ASSETS / row["path"]
        dest.parent.mkdir(parents=True, exist_ok=True)
        url = commons_url(row["commons"])
        time.sleep(1.5)
        if dest.exists() and dest.stat().st_size > 10_000:
            print(f"SKIP (exists) {dest.relative_to(ROOT)}")
            meta.append(
                {
                    "path": f"assets/plates/{row['path']}",
                    "figure_id": row["figure_id"],
                    "commons": row["commons"],
                    "sha256": sha256_file(dest),
                    "bytes": dest.stat().st_size,
                    "source_url": url,
                }
            )
            continue
        print(f"GET {row['commons']} -> {dest.relative_to(ROOT)}")
        dl_req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "COSMOS-eahp-plates/1.0 (cloud-agent; commons download)",
                "Referer": "https://commons.wikimedia.org/",
            },
        )
        with urllib.request.urlopen(dl_req, timeout=180) as resp:
            dest.write_bytes(resp.read())
        time.sleep(2.0)
        meta.append(
            {
                "path": f"assets/plates/{row['path']}",
                "figure_id": row["figure_id"],
                "commons": row["commons"],
                "sha256": sha256_file(dest),
                "bytes": dest.stat().st_size,
                "source_url": url,
            }
        )
    out = ROOT / "assets" / "plates" / "_download_meta.json"
    out.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {out.relative_to(ROOT)} ({len(meta)} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
