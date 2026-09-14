#!/usr/bin/env python3
"""Render RIGHTS.md from assets/figures/REGISTRY.toml."""

from __future__ import annotations

from pathlib import Path

try:
    import tomllib
except ImportError:
    import tomli as tomllib  # type: ignore

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "assets" / "figures" / "REGISTRY.toml"
OUT = ROOT / "RIGHTS.md"


def main() -> None:
    plates = tomllib.loads(REGISTRY.read_text(encoding="utf-8")).get("plates", {})
    lines = [
        "# RIGHTS — Dining chairs, history and sitting",
        "",
        "Hot-linked museum and Wikimedia Commons plates plus pack CC0 schematics for staged `<figure class=\"dchd-figure\">` blocks. **No museum binaries in git.** Re-check Commons license tags before WordPress publish.",
        "",
        "Canonical rows: `assets/figures/REGISTRY.toml`. Regenerate embeds:",
        "",
        "```bash",
        "python3 content/dining-chairs-history-design/scripts/generate_dchd_svgs.py",
        "python3 content/dining-chairs-history-design/scripts/build_registry.py",
        "python3 content/dining-chairs-history-design/_editorial/embed_figures.py",
        "python3 content/dining-chairs-history-design/_editorial/check_figures.py",
        "```",
        "",
        "## Cleared plates (2026-09-14)",
        "",
        "| Plate key | License | Institution | Source |",
        "| --- | --- | --- | --- |",
    ]
    for key in sorted(plates):
        p = plates[key]
        src = p["source_page"]
        if src.startswith("http"):
            link = f"[Commons / source]({src})"
        else:
            link = f"`{src}`"
        lines.append(
            f"| `{key}` | {p['license']} | {p['institution']} | {link} |"
        )
    lines.extend(
        [
            "",
            "## Pack schematics (CC0)",
            "",
            "Twelve ergonomic diagrams under `assets/diagrams/*.svg` — original line art, **no AI faces**, no stock people. Used as Figure 1 where shop measurement photos are still outstanding.",
            "",
            "## BBF shop stills (not cleared)",
            "",
            "Rows in `PHOTO_CAPTIONS.md` with `status: needed` stay open. Lead `<figure>` may use a museum fill or schematic; `figures[]` frontmatter **remains `status: needed`** until `D:\\BBF\\BBF Photos` files are pulled and credited.",
            "",
            "## Reserved (do not scrape)",
            "",
            "- IKEA Ingolf catalog heroes (`[VERIFY rights]` in captions)",
            "- Curt Teich and other commercial postcards",
            "- Identifiable children in public photography",
            "- AI-generated people or faces",
        ]
    )
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
