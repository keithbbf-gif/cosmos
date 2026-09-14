#!/usr/bin/env python3
"""Download staged Commons / museum images for desk-entryway drafts."""

from __future__ import annotations

import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = (
    ROOT
    / "content"
    / "desks-hallway-entryway-furniture"
    / "assets"
    / "images"
    / "manifest.json"
)
OUT_DIR = MANIFEST.parent
UA = "COSMOSContentBot/1.0 (https://github.com/keithbbf-gif/cosmos; cloud-agent)"


def commons_url(title: str) -> str:
    api = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(
        {
            "action": "query",
            "titles": f"File:{title}",
            "prop": "imageinfo",
            "iiprop": "url",
            "format": "json",
        }
    )
    req = urllib.request.Request(api, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.load(resp)
    for page in data["query"]["pages"].values():
        if "missing" in page:
            raise FileNotFoundError(f"Commons file missing: {title}")
        return page["imageinfo"][0]["url"]
    raise RuntimeError(f"no imageinfo for {title}")


def safe_name(name: str) -> str:
    return re.sub(r"[^\w.\-]+", "_", name)


def main() -> int:
    rows = json.loads(MANIFEST.read_text(encoding="utf-8"))
    errors: list[str] = []
    for row in rows:
        dest = OUT_DIR / row["file"]
        if dest.is_file() and dest.stat().st_size > 0:
            continue
        try:
            url = commons_url(row["commons_title"])
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = resp.read()
            dest.write_bytes(data)
            print(f"OK  {row['file']} ({len(data)} bytes)")
        except Exception as exc:  # noqa: BLE001 — batch downloader reports all failures
            errors.append(f"{row['slug']}: {exc}")
            print(f"FAIL {row['file']}: {exc}", file=sys.stderr)
    if errors:
        print(f"{len(errors)} download errors", file=sys.stderr)
        return 1
    print(f"done ({len(rows)} manifest rows)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
