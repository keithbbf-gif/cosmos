#!/usr/bin/env python3
"""Validate staged therapy-history core SVGs and write MANIFEST.json."""
from __future__ import annotations

import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PIPE = ROOT / "pipeline"
STAGED_GFX = ROOT / "staged" / "graphics"
CORE_LIST = json.loads((PIPE / "core_figures.json").read_text(encoding="utf-8"))[
    "core_figures"
]

SVG_NS = {"svg": "http://www.w3.org/2000/svg"}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def parse_viewbox(root: ET.Element) -> str | None:
    vb = root.get("viewBox")
    if vb:
        return vb
    w, h = root.get("width"), root.get("height")
    if w and h:
        nums = re.findall(r"[\d.]+", f"{w} {h}")
        if len(nums) >= 2:
            return f"0 0 {nums[0]} {nums[1]}"
    return None


def portrait_raster_guard(svg_path: Path, figure_name: str) -> list[str]:
    """Block embedded raster unless portrait_sources marks cleared."""
    text = svg_path.read_text(encoding="utf-8")
    if "<image" not in text and "xlink:href" not in text:
        return []
    try:
        import yaml  # optional
    except ImportError:
        return [
            f"{figure_name}: raster <image> present but PyYAML not installed for license check"
        ]
    sources = yaml.safe_load((PIPE / "portrait_sources.yaml").read_text(encoding="utf-8"))
    fig_key = figure_name.replace(".svg", "")
    entry = (sources.get("figures") or {}).get(fig_key, {})
    if entry.get("status") != "cleared":
        return [
            f"{figure_name}: embedded raster requires portrait_sources status 'cleared' "
            f"(current: {entry.get('status', 'missing')})"
        ]
    return []


def main() -> int:
    errors: list[str] = []
    manifest_entries = []

    for name in CORE_LIST:
        path = STAGED_GFX / name
        if not path.is_file():
            errors.append(f"missing core figure: {path.relative_to(ROOT)}")
            continue
        try:
            tree = ET.parse(path)
            root = tree.getroot()
        except ET.ParseError as exc:
            errors.append(f"{name}: XML parse error: {exc}")
            continue
        vb = parse_viewbox(root)
        if not vb:
            errors.append(f"{name}: no viewBox/width/height")
        errors.extend(portrait_raster_guard(path, name))
        manifest_entries.append(
            {
                "file": f"staged/graphics/{name}",
                "sha256": sha256_file(path),
                "viewBox": vb,
            }
        )

    manifest_path = ROOT / "staged" / "MANIFEST.json"
    manifest_path.write_text(
        json.dumps({"figures": manifest_entries}, indent=2) + "\n",
        encoding="utf-8",
    )

    if errors:
        print("seed_core_figures: FAILED", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    print(f"seed_core_figures: OK ({len(manifest_entries)} figures)")
    print(f"  wrote {manifest_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
