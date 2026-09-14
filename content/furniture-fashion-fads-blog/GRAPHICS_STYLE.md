# Graphics style — furniture & fashion fads pack

Editorial schematics for a shelter-and-style blog. These are **not** data visualizations from proprietary datasets; they are labeled, opinionated frames that support the prose.

## Tokens

| Role | Hex | Use |
|------|-----|-----|
| Background | `#F7F5F0` | Field |
| Ink | `#1C1C1C` | Headlines, axes |
| Muted | `#5C5A55` | Notes, axis labels |
| Furniture accent | `#7A6B56` | Bars, nodes (home) |
| Fashion accent | `#8B4A5E` | Bars, nodes (apparel) |
| Ages well | `#3D5C4A` | Comparison column |
| Dates fast | `#9A6B4A` | Comparison column |

Typography in SVG: **Georgia** for titles, **Helvetica Neue** stack for notes.

## Figure types

1. **`decade-timeline.svg`** — dated inflection points on a horizontal axis.
2. **`style-cycle.svg`** — recurring phases on a ring (pendulum / revival logic).
3. **`ages-well-vs-dates.svg`** — two-column editorial comparison (not a score).
4. **`retail-era-chart.svg`** — relative visibility bars (indexed schematic).

Every figure carries a footnote that it is schematic, not audited sales data.

## Embedding

From `articles/<slug>.md`:

```html
<figure class="fffb-figure">
  <img src="../assets/<slug>/decade-timeline.svg" alt="…" width="720" loading="lazy" />
  <figcaption>Caption matches GRAPHICS_INDEX.</figcaption>
</figure>
```

Copy-ready blocks live in `embeds/<slug>.md`. Regenerate with:

`python3 tools/fffb_graphics_build.py`

## Do not

- Meme fonts, stickers, or ironic clip art.
- Unlabeled axes pretending to be Nielsen/NPD data.
- Raster screenshots inside SVG.
