#!/usr/bin/env python3
"""Verify every commons title in figures_registry.json resolves to a URL."""
from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

REG = Path(__file__).resolve().parent / "figures_registry.json"
UA = "COSMOS-verify/1.0"


def has_url(title: str) -> bool:
    params = urllib.parse.urlencode(
        {
            "action": "query",
            "titles": title,
            "prop": "imageinfo",
            "iiprop": "url",
            "format": "json",
        }
    )
    req = urllib.request.Request(
        f"https://commons.wikimedia.org/w/api.php?{params}",
        headers={"User-Agent": UA},
    )
    with urllib.request.urlopen(req, timeout=45) as resp:
        data = json.loads(resp.read().decode())
    for page in data.get("query", {}).get("pages", {}).values():
        if page.get("missing"):
            return False
        ii = page.get("imageinfo", [{}])[0]
        return bool(ii.get("url"))
    return False


def main() -> int:
    reg = json.loads(REG.read_text(encoding="utf-8"))
    bad = []
    for fid, row in reg["figures"].items():
        for key in ("commons", "commons_secondary"):
            title = row.get(key)
            if not title:
                continue
            if not has_url(title):
                bad.append((fid, title))
                print(f"BAD {fid} {title}")
            else:
                print(f"OK {fid} {title[:50]}")
            time.sleep(1.1)
    print(f"bad={len(bad)}")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
