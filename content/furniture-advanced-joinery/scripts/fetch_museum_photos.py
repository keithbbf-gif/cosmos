#!/usr/bin/env python3
"""Download museum/Commons rasters listed in assets/museum/museum_sources.yaml."""

from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
YAML = ROOT / "assets" / "museum" / "museum_sources.yaml"
OUT = ROOT / "assets" / "museum"
UA = "COSMOS-faj-fetch/1.0 (keithbbf-gif/cosmos; cloud-agent)"
MAX_WIDTH = 1280


def thumb_url(original: str, width: int) -> str:
    if width <= MAX_WIDTH:
        return original
    # Commons thumb: .../thumb/<path>/<Wx>px-<filename>
    parsed = urllib.parse.urlparse(original)
    if "/wikipedia/" not in parsed.path:
        return original
    parts = parsed.path.split("/")
    # /wikipedia/commons/x/xx/File.jpg
    try:
        idx = parts.index("commons")
        subpath = "/".join(parts[idx + 1 :])
        filename = parts[-1]
        return f"https://upload.wikimedia.org/wikipedia/commons/thumb/{subpath}/{MAX_WIDTH}px-{filename}"
    except ValueError:
        return original


def fetch(url: str, dest: Path) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = resp.read()
    dest.write_bytes(data)
    print(f"  wrote {dest.name} ({len(data)} bytes)")


def main() -> None:
    data = yaml.safe_load(YAML.read_text(encoding="utf-8"))
    OUT.mkdir(parents=True, exist_ok=True)
    for key, meta in data["files"].items():
        dest = OUT / meta["save_as"]
        url = meta["url"]
        w = int(meta.get("width", MAX_WIDTH))
        dl = thumb_url(url, w)
        for attempt in range(4):
            try:
                time.sleep(1.5)
                fetch(dl, dest)
                break
            except Exception as exc:
                if attempt == 3:
                    print(f"FAIL {key}: {exc}")
                    raise
                print(f"  retry {key} ({exc})")
                time.sleep(4 * (attempt + 1))
    manifest = {
        "files": {
            k: {**v, "local_path": f"assets/museum/{v['save_as']}"}
            for k, v in data["files"].items()
        },
        "assignments": data.get("assignments", {}),
    }
    (OUT / "museum_manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    print(f"Wrote {OUT / 'museum_manifest.json'}")


if __name__ == "__main__":
    main()
