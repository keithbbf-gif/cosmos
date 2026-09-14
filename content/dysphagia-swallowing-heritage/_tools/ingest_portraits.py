#!/usr/bin/env python3
"""Download cleared Commons portraits into assets/portraits/ and write .RIGHTS.md sidecars."""
from __future__ import annotations

import json
import subprocess
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "portraits"
UA = "SLPWOW-heritage-pack/1.0 (Cursor cloud agent; contact keith.bbf@gmail.com)"

PORTRAITS = [
    {
        "id": "francois-magendie",
        "commons": "Portrait de François Magendie (1783-1855), physiologiste, S454.jpg",
        "figure": "François Magendie",
        "dates": "1783–1855",
        "alt": "Lithograph portrait of François Magendie, nineteenth-century French physiologist.",
        "caption_tail": "French physiologist who treated deglutition as interruptible physiology in the *Précis* textbooks.",
        "credit": "BIU Santé / Wikimedia Commons. CC0 1.0.",
    },
    {
        "id": "walter-b-cannon",
        "commons": "Walter Bradford Cannon. Photograph. Wellcome M0014715.jpg",
        "figure": "Walter B. Cannon",
        "dates": "1871–1945",
        "alt": "Studio photograph of Walter Bradford Cannon in mid career.",
        "caption_tail": "Harvard physiologist who stained living meals with bismuth for early fluoroscopic swallow studies.",
        "credit": "Wellcome Collection / Wikimedia Commons. CC BY 4.0.",
    },
    {
        "id": "gustav-killian",
        "commons": "Killian.jpg",
        "figure": "Gustav Killian",
        "dates": "1860–1921",
        "alt": "Portrait photograph of Gustav Killian, German laryngologist and endoscopist.",
        "caption_tail": "Freiburg laryngologist associated with rigid endoscopy and Killian’s triangle.",
        "credit": "Wikimedia Commons. Public domain.",
    },
    {
        "id": "chevalier-jackson",
        "commons": "Portrait of Chevalier Jackson, autographed. Wellcome M0017924.jpg",
        "figure": "Chevalier Jackson",
        "dates": "1865–1958",
        "alt": "Autographed studio portrait of Chevalier Jackson in later life.",
        "caption_tail": "Philadelphia bronchoesophagologist whose foreign-body clinic and manuals shaped American endoscopy.",
        "credit": "Wellcome Collection / Wikimedia Commons. CC BY 4.0.",
    },
]


def commons_url(filename: str) -> tuple[str, int, int]:
    title = f"File:{filename}" if not filename.startswith("File:") else filename
    q = urllib.parse.urlencode(
        {
            "action": "query",
            "format": "json",
            "titles": title,
            "prop": "imageinfo",
            "iiprop": "url|size|extmetadata",
        }
    )
    req = urllib.request.Request(
        f"https://commons.wikimedia.org/w/api.php?{q}",
        headers={"User-Agent": UA},
    )
    data = json.loads(urllib.request.urlopen(req, timeout=60).read())
    pages = data["query"]["pages"]
    page = next(iter(pages.values()))
    ii = page["imageinfo"][0]
    meta = ii.get("extmetadata") or {}
    lic = (meta.get("LicenseShortName") or {}).get("value", "?")
    artist = (meta.get("Artist") or {}).get("value", "")
    return ii["url"], ii["width"], ii["height"], lic, artist, title


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for spec in PORTRAITS:
        url, w, h, lic, artist, title = commons_url(spec["commons"])
        dest = OUT / f"{spec['id']}.jpg"
        subprocess.run(
            ["curl", "-fsSL", "-A", UA, "-o", str(dest), url],
            check=True,
        )
        page = "https://commons.wikimedia.org/wiki/" + urllib.parse.quote(title.replace(" ", "_"))
        rights = OUT / f"{spec['id']}.RIGHTS.md"
        rights.write_text(
            f"""---
# Rights — `{spec['id']}.jpg`

| Field | Value |
|-------|-------|
| figure | {spec['figure']} ({spec['dates']}) |
| file | `assets/portraits/{spec['id']}.jpg` |
| commons | {page} |
| license | {lic} |
| creator | {artist or 'See Commons file page'} |
| ingested | 2026-09-14 |

## SEO caption (`<figcaption>`)

**{spec['figure']}** ({spec['dates']}), {spec['caption_tail']}
{spec['credit']}

## Alt text

{spec['alt']}
""",
            encoding="utf-8",
        )
        print(f"OK {spec['id']} {w}x{h} -> {dest.name}")


if __name__ == "__main__":
    main()
