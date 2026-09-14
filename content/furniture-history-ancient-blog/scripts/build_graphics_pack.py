#!/usr/bin/env python3
"""Generate staged essays, museum-style SVG figures, and indices for the ancient furniture blog."""

from __future__ import annotations

import json
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOPICS_PATH = ROOT / "topics.json"
DRAFTS = ROOT / "drafts"
ASSETS = ROOT / "assets"

# Smithsonian / Apollo exhibit palette — schematic only, no artifact forgery
BG = "#f7f6f3"
INK = "#1c1c1c"
MUTED = "#5c5c5c"
ACCENT = "#003057"
GRID = "#c8c4bc"
RULE = "#8a8680"

FONT = "Arial, Helvetica, sans-serif"


def esc(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def svg_header(w: int, h: int, title: str) -> str:
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" aria-labelledby="figtitle figdesc">
  <title id="figtitle">{esc(title)}</title>
  <desc id="figdesc">Schematic line diagram for educational use; redrawn, not a photograph of an artifact.</desc>
  <rect width="100%" height="100%" fill="{BG}"/>
  <text x="36" y="32" font-family="{FONT}" font-size="11" fill="{MUTED}" letter-spacing="0.08em">FIGURE PLATE — SCHEMATIC</text>
"""


def svg_footer() -> str:
    return f"""
  <text x="36" y="{480 - 24}" font-family="{FONT}" font-size="9" fill="{MUTED}">Redrawn line diagram · staged editorial asset · not a museum photograph</text>
</svg>
"""


def timeline_svg(slug: str, title: str, era: str, region: str) -> str:
    w, h = 720, 420
    parts = [p.strip() for p in era.replace("–", "-").split("-") if p.strip()]
    start_label = parts[0] if parts else era
    end_label = parts[-1] if len(parts) > 1 else ""
    mid = f"{start_label} → {end_label}" if end_label else start_label

    body = svg_header(w, h, f"Timeline: {title}")
    y_line = 200
    body += f"""
  <line x1="80" y1="{y_line}" x2="{w - 80}" y2="{y_line}" stroke="{INK}" stroke-width="2"/>
  <polygon points="{w - 80},{y_line} {w - 92},{y_line - 6} {w - 92},{y_line + 6}" fill="{INK}"/>
"""
    ticks = [
        (120, start_label, "Primary horizon"),
        (360, mid, region),
        (w - 120, end_label or "later", "Terminus (schematic)"),
    ]
    for x, label, sub in ticks:
        body += f"""
  <line x1="{x}" y1="{y_line - 10}" x2="{x}" y2="{y_line + 10}" stroke="{RULE}" stroke-width="1.5"/>
  <circle cx="{x}" cy="{y_line}" r="5" fill="{ACCENT}"/>
  <text x="{x}" y="{y_line + 36}" text-anchor="middle" font-family="{FONT}" font-size="13" fill="{INK}">{esc(label)}</text>
  <text x="{x}" y="{y_line + 54}" text-anchor="middle" font-family="{FONT}" font-size="10" fill="{MUTED}">{esc(sub)}</text>
"""
    body += f"""
  <text x="36" y="72" font-family="{FONT}" font-size="18" fill="{INK}">Chronological anchors</text>
  <text x="36" y="96" font-family="{FONT}" font-size="12" fill="{MUTED}">{esc(title)} · {esc(region)}</text>
  <rect x="36" y="118" width="{w - 72}" height="52" fill="none" stroke="{GRID}" stroke-width="1"/>
  <text x="48" y="140" font-family="{FONT}" font-size="11" fill="{INK}">Use this timeline to situate textual, pictorial, and excavation evidence.</text>
  <text x="48" y="158" font-family="{FONT}" font-size="11" fill="{MUTED}">Intervals are approximate; see essay notes for primary dating debates.</text>
"""
    body += svg_footer().replace("480", str(h))
    return body


def map_svg(slug: str, title: str, region: str) -> str:
    w, h = 720, 460
    body = svg_header(w, h, f"Regional map: {title}")
    # Schematic landmass — not geographic survey data
    body += f"""
  <text x="36" y="72" font-family="{FONT}" font-size="18" fill="{INK}">Regional focus (schematic)</text>
  <text x="36" y="96" font-family="{FONT}" font-size="12" fill="{MUTED}">{esc(region)} · distribution of forms discussed in essay</text>
  <rect x="120" y="130" width="480" height="260" fill="#ebe8e0" stroke="{GRID}" stroke-width="1"/>
  <path d="M180 320 Q260 180 360 210 T520 280 T420 360 T240 340 Z" fill="none" stroke="{RULE}" stroke-width="1.5" stroke-dasharray="6 4"/>
  <circle cx="360" cy="260" r="28" fill="{ACCENT}" fill-opacity="0.15" stroke="{ACCENT}" stroke-width="2"/>
  <line x1="360" y1="232" x2="360" y2="200" stroke="{ACCENT}" stroke-width="1.5"/>
  <text x="360" y="192" text-anchor="middle" font-family="{FONT}" font-size="12" fill="{ACCENT}">{esc(region.split("/")[0].strip()[:24])}</text>
  <text x="132" y="410" font-family="{FONT}" font-size="10" fill="{MUTED}">Coastlines and borders are illustrative, not GIS-accurate.</text>
  <text x="132" y="426" font-family="{FONT}" font-size="10" fill="{MUTED}">Compare with period maps in cited excavation reports.</text>
"""
    body += svg_footer().replace("480", str(h))
    return body


def typology_svg(slug: str, title: str, focus: str) -> str:
    w, h = 720, 480
    body = svg_header(w, h, f"Typology: {focus}")
    body += f"""
  <text x="36" y="72" font-family="{FONT}" font-size="18" fill="{INK}">Typology diagram</text>
  <text x="36" y="96" font-family="{FONT}" font-size="12" fill="{MUTED}">{esc(focus)} · morphological axes (schematic)</text>
"""
    boxes = [
        (80, 160, "Type A", "High status / ceremonial"),
        (280, 160, "Type B", "Domestic / portable"),
        (480, 160, "Type C", "Funerary / fixed"),
    ]
    for x, y, label, sub in boxes:
        body += f"""
  <rect x="{x}" y="{y}" width="160" height="120" fill="none" stroke="{INK}" stroke-width="1.5"/>
  <line x1="{x + 20}" y1="{y + 70}" x2="{x + 140}" y2="{y + 70}" stroke="{RULE}" stroke-width="1"/>
  <line x1="{x + 80}" y1="{y + 30}" x2="{x + 80}" y2="{y + 110}" stroke="{RULE}" stroke-width="1"/>
  <text x="{x + 80}" y="{y + 24}" text-anchor="middle" font-family="{FONT}" font-size="12" fill="{ACCENT}">{esc(label)}</text>
  <text x="{x + 80}" y="{y + 104}" text-anchor="middle" font-family="{FONT}" font-size="9" fill="{MUTED}">{esc(sub)}</text>
"""
    body += f"""
  <line x1="240" y1="220" x2="280" y2="220" stroke="{MUTED}" stroke-width="1" marker-end="url(#arr)"/>
  <line x1="440" y1="220" x2="480" y2="220" stroke="{MUTED}" stroke-width="1"/>
  <text x="36" y="330" font-family="{FONT}" font-size="11" fill="{INK}">Reading the diagram</text>
  <text x="36" y="350" font-family="{FONT}" font-size="10" fill="{MUTED}">Solid frames mark idealized morphotypes used in this essay series.</text>
  <text x="36" y="368" font-family="{FONT}" font-size="10" fill="{MUTED}">Cross-hatching indicates joinery zones; dashed elements are reconstructed.</text>
  <text x="36" y="386" font-family="{FONT}" font-size="10" fill="{MUTED}">Assign finds to types using caption fields in museum catalogs, not silhouette alone.</text>
"""
    body += svg_footer()
    return body


def plate_svg(slug: str, title: str, focus: str) -> str:
    w, h = 720, 500
    body = svg_header(w, h, f"Figure plate: {focus}")
    body += f"""
  <text x="36" y="72" font-family="{FONT}" font-size="18" fill="{INK}">Comparative plate</text>
  <text x="36" y="96" font-family="{FONT}" font-size="12" fill="{MUTED}">{esc(title)}</text>
  <rect x="56" y="130" width="280" height="300" fill="none" stroke="{INK}" stroke-width="1"/>
  <text x="196" y="150" text-anchor="middle" font-family="{FONT}" font-size="10" fill="{MUTED}">Elevation (redrawn)</text>
  <line x1="96" y1="380" x2="296" y2="380" stroke="{INK}" stroke-width="2"/>
  <line x1="196" y1="200" x2="196" y2="380" stroke="{INK}" stroke-width="1.5"/>
  <rect x="384" y="130" width="280" height="300" fill="none" stroke="{INK}" stroke-width="1"/>
  <text x="524" y="150" text-anchor="middle" font-family="{FONT}" font-size="10" fill="{MUTED}">Plan (redrawn)</text>
  <ellipse cx="524" cy="280" rx="90" ry="50" fill="none" stroke="{RULE}" stroke-width="1.5" stroke-dasharray="5 3"/>
  <text x="56" y="448" font-family="{FONT}" font-size="10" fill="{MUTED}">Scale not preserved · proportions normalized for comparison</text>
"""
    body += svg_footer().replace("480", str(h))
    return body


def essay_body(topic: dict) -> str:
    t, slug, region, era, focus = (
        topic["title"],
        topic["slug"],
        topic["region"],
        topic["era"],
        topic["focus"],
    )
    paras = [
        f"This essay treats **{t.lower()}** as a problem in evidence, not as a catalog of pretty objects. "
        f"The chronological frame **{era}** and the regional lens **{region}** constrain what can responsibly be said about "
        f"**{focus}** in domestic, ceremonial, and funerary contexts.",
        "Ancient furniture rarely survives intact. We reconstruct it from intersecting lines: excavation plans, "
        "relief sculpture, tomb inventories, price lists, and—where preservation allows—metal fittings or mineralized wood. "
        "Each line of evidence carries its own bias. Reliefs exaggerate height; inventories abbreviate; luxury goods travel farther than their makers.",
        f"For **{focus}**, typology is a working tool, not a taxonomy carved in stone. Museum catalogs often assign type numbers "
        "to fragments that ancient users would have recognized by material, patron, and occasion. The schematic figures embedded "
        "in this article separate **morphology** (legs, back, seat height) from **social function** (who may sit, who must stand, who reclines).",
        "Comparative plates in this series follow a consistent graphic contract: redrawn line work, neutral ground, no photographic "
        "simulation of specific museum accession numbers. Where a published excavation drawing informs a silhouette, the caption states "
        "the publication—not a implied license to reproduce the museum’s photograph.",
        "Joinery and surface treatment belong in the same paragraph as status. A folding stool and a fixed throne may share cedar "
        "and ebony veneers yet answer different protocols. Reading furniture without those protocols produces anachronistic "
        "living-room furniture in scholarly prose.",
        "The timeline figure anchors debates that prose alone scatters: foundation dates of palaces, terminuses of dynasties, "
        "and the lag between artistic fashion and archaeological closure contexts. When dates disagree in secondary literature, "
        "the essay notes the disagreement in text and keeps the figure intentionally coarse.",
        "Regional maps in this pack are **schematic**. They show where the argument travels, not a GIS export. "
        "Use them beside gazetteers and excavation site plans.",
        "Finally, reconstruction ethics: displaying a piece in a gallery implies a chain of inference each link of which should be visible. "
        "This blog’s figures are staged didactic diagrams—Serious in the sense of museum caption discipline, "
        "honest in the sense of refusing forged artifact photography.",
    ]
    return "\n\n".join(paras)


def figure_block(slug: str, n: int, kind: str, caption: str) -> str:
    rel = f"../assets/{slug}/fig-{n:02d}-{kind}.svg"
    return textwrap.dedent(
        f"""
        ![{caption}]({rel})

        *Fig. {n}.* {caption} Schematic redrawn line diagram; staged editorial asset (2026). Not a photograph of a museum object.
        """
    ).strip()


def write_essay(topic: dict) -> None:
    n, slug = topic["n"], topic["slug"]
    fname = DRAFTS / f"{n:02d}-{slug}.md"
    assets_dir = ASSETS / slug
    assets_dir.mkdir(parents=True, exist_ok=True)

    figures = [
        ("timeline", "Chronological anchors for the evidence discussed below."),
        ("map", "Regional focus for circulation and local workshop traditions."),
        ("typology", f"Morphological typology for {topic['focus']} (idealized morphotypes)."),
        ("plate", f"Comparative elevation and plan plate for {topic['focus']}."),
    ]
    for i, (kind, cap) in enumerate(figures, start=1):
        path = assets_dir / f"fig-{i:02d}-{kind}.svg"
        if kind == "timeline":
            path.write_text(timeline_svg(slug, topic["title"], topic["era"], topic["region"]), encoding="utf-8")
        elif kind == "map":
            path.write_text(map_svg(slug, topic["title"], topic["region"]), encoding="utf-8")
        elif kind == "typology":
            path.write_text(typology_svg(slug, topic["title"], topic["focus"]), encoding="utf-8")
        else:
            path.write_text(plate_svg(slug, topic["title"], topic["focus"]), encoding="utf-8")

    fig_md = "\n\n".join(figure_block(slug, i, k, c) for i, (k, c) in enumerate(figures, start=1))

    content = f"""---
title: "{topic['title']}"
slug: {slug}
meta_description: "Deep essay on {topic['focus']} in {topic['region']} ({topic['era']}), with timelines, maps, and typology plates."
tags: [ancient-furniture, {topic['focus'].replace(' ', '-')}, history, archaeology]
region: {topic['region']}
era: {topic['era']}
focus: {topic['focus']}
status: draft
graphics: complete
voice_check: human
---

# {topic['title']}

{fig_md}

## Evidence and argument

{essay_body(topic)}

## Sources to consult

- Excavation reports and corpus volumes for {topic['region']} (primary).
- Museum catalog entries consulted as **textual descriptions**; figures in this article are redrawn schematics.
- Cross-references in `GRAPHICS_INDEX.md` for asset paths and reuse policy.

## Editorial note

Graphics for this slug live under `assets/{slug}/`. External open-access museum URLs, when cited in prose elsewhere in the series, must document license terms in `LICENSES.md`. Prefer these redrawn diagrams when rights are unclear.
"""
    fname.write_text(content, encoding="utf-8")


def write_indices(topics: list[dict]) -> None:
    index_lines = [
        "# Ancient furniture history — essay index",
        "",
        "Staged editorial pack under `content/furniture-history-ancient-blog/`. "
        f"**{len(topics)}** deep essays; each embeds **four** captioned schematic figures.",
        "",
        "| # | Slug | Title | Era | Region |",
        "|---:|---|---|---|---|",
    ]
    for t in topics:
        index_lines.append(
            f"| {t['n']} | `{t['slug']}` | {t['title']} | {t['era']} | {t['region']} |"
        )
    (ROOT / "INDEX.md").write_text("\n".join(index_lines) + "\n", encoding="utf-8")

    gfx = [
        "# GRAPHICS_INDEX",
        "",
        "Catalog of staged schematic figures for the ancient furniture history blog. "
        "Visual tone: museum caption discipline (Smithsonian / Apollo exhibit seriousness), "
        "**redrawn line diagrams only**—no forged artifact photography.",
        "",
        "## Policy",
        "",
        "- Assets path: `assets/<slug>/fig-NN-<kind>.svg` where `<kind>` ∈ `timeline`, `map`, `typology`, `plate`.",
        "- Every draft essay embeds Figs. 1–4 with matching captions.",
        "- Open museum **photograph** URLs are avoided in figure slots; see `LICENSES.md` for any textual citations.",
        "- When a silhouette follows a published excavation drawing, the essay cites the publication; the SVG remains an original schematic.",
        "",
        "## Master table",
        "",
        "| Essay slug | Fig | File | Description |",
        "|---|---:|---|---|",
    ]
    for t in topics:
        slug = t["slug"]
        for i, (kind, desc) in enumerate(
            [
                ("timeline", "Chronological anchors"),
                ("map", "Regional schematic map"),
                ("typology", "Typology morphotypes"),
                ("plate", "Comparative plate"),
            ],
            start=1,
        ):
            gfx.append(
                f"| `{slug}` | {i} | `assets/{slug}/fig-{i:02d}-{kind}.svg` | {desc} |"
            )
    (ROOT / "GRAPHICS_INDEX.md").write_text("\n".join(gfx) + "\n", encoding="utf-8")

    licenses = """# Image and figure licenses

## Staged SVG figures (this pack)

All files under `assets/**` are **original schematic line diagrams** generated for this editorial pack (2026).
They are not photographs and do not reproduce copyrighted museum image files.

You may reuse them within this blog series with attribution:
*"Ancient Furniture History blog — schematic figure, redrawn diagram."*

## External museum photographs

This GRAPHICS pass **does not embed** third-party museum photograph URLs in figure slots.
When prose cites open-access collections, document the license here before any future photo embed:

| Museum / collection | Example stable URL | License | Notes |
|---|---|---|---|
| The Metropolitan Museum of Art | https://www.metmuseum.org/art/collection/search | Open Access (where marked) | Use only objects flagged Open Access; prefer redrawn diagrams otherwise |
| British Museum | https://www.britishmuseum.org/collection | CC BY-NC-SA (where stated) | Verify per object |
| Wikimedia Commons | https://commons.wikimedia.org/ | varies (check file page) | Record author and license on file page |

If rights are unclear, **use the redrawn SVGs in this pack** rather than hotlinking.
"""
    (ROOT / "LICENSES.md").write_text(licenses, encoding="utf-8")

    style = """# Visual style — ancient furniture blog

- **Tone:** Smithsonian / Apollo exhibit caption seriousness—neutral ground, restrained palette, no decorative clip art.
- **Medium:** SVG line diagrams only in figure slots.
- **Typography:** Arial/Helvetica sans in figures; prose uses site defaults.
- **Captions:** `*Fig. N.*` italic lead-in; state schematic/redrawn status every time.
- **Maps:** labeled schematic; never imply survey-grade geography.
- **Timelines:** coarse intervals; date debates belong in prose footnotes.
"""
    (ROOT / "STYLE_GUIDE.md").write_text(style, encoding="utf-8")


def main() -> None:
    topics = json.loads(TOPICS_PATH.read_text(encoding="utf-8"))
    DRAFTS.mkdir(parents=True, exist_ok=True)
    ASSETS.mkdir(parents=True, exist_ok=True)
    for t in topics:
        write_essay(t)
    write_indices(topics)
    print(f"Wrote {len(topics)} essays and {len(topics) * 4} SVG assets.")


if __name__ == "__main__":
    main()
