#!/usr/bin/env python3
"""Generate RIGHTS.md, GRAPHICS_INDEX.md, and IMAGE_SOURCES.md from staged assets."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMG = ROOT / "assets" / "images"
SVG = ROOT / "assets" / "svg"
META = IMG / "_download_meta.json"


def main() -> int:
    meta = json.loads(META.read_text(encoding="utf-8")) if META.exists() else {"files": {}}
    rights_lines = [
        "# RIGHTS — herbal-tea-foodways-history",
        "",
        "Cleared plates for desk review. **Recheck Commons pages before live import.**",
        "No AI-generated faces. No medical-claim infographics. Foodways and botanical context only.",
        "",
        "## Original SVG (editorial)",
        "",
        "| Pack path | Kind | License | Credit |",
        "| --- | --- | --- | --- |",
    ]
    index_lines = [
        "# GRAPHICS_INDEX — herbal-tea-foodways-history",
        "",
        "| Figure key | Asset | Kind | Status |",
        "| --- | --- | --- | --- |",
    ]
    image_sources = [
        "# IMAGE_SOURCES — herbal-tea-foodways-history",
        "",
        "Per-draft hero figures. Recheck licenses before production import.",
        "",
    ]

    for svg in sorted(SVG.glob("*.svg")):
        rel = f"assets/svg/{svg.name}"
        key = f"svg.{svg.stem}"
        rights_lines.append(
            f"| `{rel}` | Editorial schematic | CC0-equivalent (pack editorial) | herbal-tea-foodways-history |"
        )
        index_lines.append(f"| `{key}` | `{rel}` | svg | staged |")
        image_sources.append(f"## {key}")
        image_sources.append(f"- **File:** `{rel}`")
        image_sources.append("- **License:** Editorial schematic (pack-owned)")
        image_sources.append("")

    rights_lines.extend(["", "## Commons rasters", "", "| Pack path | Commons page | License | SHA-256 |", "| --- | --- | --- | --- |"])
    for rel, info in sorted(meta.get("files", {}).items()):
        key = "plates." + Path(rel).stem.replace("-", "_")
        page = info.get("commons_page", "See Commons")
        lic = info.get("license", "Recheck Commons")
        sha = info.get("sha256", "")
        rights_lines.append(f"| `assets/images/{rel}` | {page} | {lic} | `{sha}` |")
        index_lines.append(f"| `{key}` | `assets/images/{rel}` | raster | staged |")
        image_sources.append(f"## {key}")
        image_sources.append(f"- **File:** `assets/images/{rel}`")
        image_sources.append(f"- **Source:** {page}")
        image_sources.append(f"- **License:** {lic}")
        image_sources.append("")

    (ROOT / "RIGHTS.md").write_text("\n".join(rights_lines) + "\n", encoding="utf-8")
    (ROOT / "GRAPHICS_INDEX.md").write_text("\n".join(index_lines) + "\n", encoding="utf-8")
    (ROOT / "IMAGE_SOURCES.md").write_text("\n".join(image_sources) + "\n", encoding="utf-8")
    print("wrote RIGHTS.md, GRAPHICS_INDEX.md, IMAGE_SOURCES.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
