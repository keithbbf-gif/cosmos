# Visual style guide — fig history pack

Magazine archival quality: restrained palette, legible labels, no decorative clutter.

## Palette (SVG and raster framing)

| Token | Hex | Use |
|-------|-----|-----|
| Ink | `#2c2416` | Primary text, outlines |
| Secondary | `#5c4a32` | Subheads, map borders |
| Accent | `#8b5a2b` | Highlights, trade routes |
| Leaf | `#4a6741` | Botanical fills (light) |
| Fig fruit | `#6b3a2a` | Syconium fills |
| Paper | `#f5f0e8` | Background |
| Grid | `#d4c8b8` | Timeline ticks, map graticule |

## Typography

- Diagram labels: **sans-serif**, 11–14 px equivalent at 800 px width (`font-family: "Segoe UI", system-ui, sans-serif` in SVG).
- Plate titles: 16–18 px, semibold (`font-weight: 600`).
- All schematic maps and timelines carry a footer: `Schematic — not to scale` unless a scale bar is drawn.

## Figure types

1. **Timelines** — horizontal era bands; dated milestones; no fake precision (use “c.” for circa).
2. **Maps** — simplified coastlines; labeled regions; trade arrows with dashed vs solid legend.
3. **Botanical plates** — line art; numbered callouts (1–n); Latin binomial in subtitle.
4. **Process diagrams** — left-to-right flow; numbered steps.
5. **Historical photos** — never generated; only cleared rasters in `assets/images/<slug>/`, wrapped with credit line from `IMAGE_SOURCES.md`.

## Caption rules

- Figure number + sentence-case caption ending with a period.
- Second line (italic) may clarify medium: `*Ink schematic after Stover et al.; syconium stages generalized.*`
- Credit for third-party rasters: `*Photo: Name, Institution. License: CC BY-SA 4.0.*`

## File formats

- **Preferred:** SVG for all diagrams (`assets/shared/svg/` or slug folder).
- **Raster:** PNG or WebP, min 1600 px width for full-width embeds; record SHA256 in `IMAGE_SOURCES.md` when imported.
