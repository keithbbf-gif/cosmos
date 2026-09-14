#!/usr/bin/env python3
"""Regenerate GRAPHICS_INDEX.md from pack_data."""

from __future__ import annotations

from pathlib import Path

from pack_data import ARTICLES

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "GRAPHICS_INDEX.md"


def main() -> None:
    lines = [
        "# Graphics index — herbal medicine history blog pack",
        "",
        "Staged editorial figures only. **SVG** under `assets/<slug>/`. Each draft embeds captioned figures after the relevant H2 (`<!-- graphics-pack:v1 -->`).",
        "",
        "Regenerate assets: `python3 scripts/generate_graphics.py`  ",
        "Re-embed markdown: `python3 scripts/embed_graphics.py`  ",
        "Refresh this file: `python3 scripts/write_graphics_index.py`",
        "",
        "## Policy (matches `PHOTO_NOTES.md` + `CLAIMS_GUARDRAILS.md`)",
        "",
        "- No disease-cure marketing art, fake lab photos, or efficacy percentage charts.",
        "- Trade routes and materia medica plates are **illustrative** unless prose cites a specific map or plate.",
        "- Plant→principle diagrams are **historical schematics**, not synthesis or manufacturing guides.",
        "",
        "## Coverage",
        "",
        "| # | Slug | Article file | SVG count | Primary figure types |",
        "| --- | --- | --- | ---: | --- |",
    ]
    total_svgs = 0
    for art in ARTICLES:
        n = len(art["figures"])
        total_svgs += n
        kinds = ", ".join(sorted({f["kind"] for f in art["figures"]}))
        lines.append(
            f"| {art['num']:02d} | `{art['slug']}` | `articles/{art['file']}` | {n} | {kinds} |"
        )
    lines.extend(
        [
            "",
            f"**Totals:** {len(ARTICLES)} drafts illustrated · **{total_svgs}** SVG files · extend `pack_data.py` for drafts 41+.",
            "",
            "## File manifest (by slug)",
            "",
        ]
    )
    for art in ARTICLES:
        lines.append(f"### `{art['slug']}`")
        lines.append("")
        for fig in art["figures"]:
            lines.append(f"- `{fig['file']}` — {fig['caption'].split('.')[0]}.")
        lines.append("")
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
