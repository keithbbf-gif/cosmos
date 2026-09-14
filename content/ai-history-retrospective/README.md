# Long Term History of AI — Retrospective (content staging)

Magazine-style retrospective series: timelines, lab maps, paradigm charts, and portrait plates.

| Doc | Purpose |
|-----|---------|
| [GRAPHICS_PIPELINE.md](GRAPHICS_PIPELINE.md) | How figures are produced and embedded |
| [GRAPHICS_INDEX.md](GRAPHICS_INDEX.md) | Master list of SVG assets |
| [GRAPHICS_CHECKLIST.md](GRAPHICS_CHECKLIST.md) | Slug coverage and remaining work |
| [PORTRAIT_SOURCES.md](PORTRAIT_SOURCES.md) | Licensed portrait ledger |

**Layout**

- `assets/<slug>/` — SVG figures per article or figure profile
- `assets/shared/` — cross-series diagrams
- `assets/portraits/` — cleared raster files only (empty until rights logged)
- `staged/embeds/` — publish-ready Markdown figure blocks
- `tools/validate_graphics.py` — pre-PR SVG checks

Article prose drafts are not in this tree yet; graphics ship ahead of COPY in **staged** form.
