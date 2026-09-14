# Fig history: ancient to today (content pack)

Magazine-grade editorial pack on *Ficus carica* cultivation, trade, and culture from deep antiquity through the present. This tree is **graphics-forward**: every article ships with multiple captioned, publish-ready figures.

## Layout

| Path | Role |
|------|------|
| `ARTICLE_INDEX.md` | Canon slug list (50+), era tags, per-article figure targets |
| `INDEX.md` | Writer reading order, mix codes, first-wave notes |
| `GRAPHICS_INDEX.md` | Master register of every figure ID, file path, reuse scope |
| `IMAGE_SOURCES.md` | License and attribution ledger (required for all raster imports) |
| `GRAPHICS_PIPELINE.md` | How writers, illustrators, and reviewers add figures |
| `GRAPHICS_CHECKLIST.md` | Per-article QA before moving out of `_staging` |
| `STYLE_GUIDE.md` | Visual system (palette, type, caption format) |
| `WRITER_STYLE_GUIDE.md` | Prose voice, citation rules, mix codes |
| `BIBLIOGRAPHY.md` | Sources actually used or checked |
| `PHOTO_NOTES.md` | Image classes, orchard slots, balance test |
| `WP_IMPORT.md` | Draft-only WordPress handoff |
| `assets/shared/svg/` | Reusable diagrams (maps, timelines, plates) |
| `assets/images/<slug>/` | Article-specific rasters (museum/Wikimedia, cleared) |
| `articles/_staging/<slug>/` | Draft articles (not publish-ready until checklist passes) |
| `templates/` | Markdown embed patterns |

## Embed convention

Articles use figure blocks (see `templates/figure-block.md`):

```markdown
![Caption sentence ending with period.](<!-- figure-id: shared.timeline-master -->)
../../assets/shared/svg/timeline-fig-cultivation-master.svg
*Figure 1. Caption with period. Schematic; not to scale.*
```

The HTML comment `figure-id` must match a row in `GRAPHICS_INDEX.md`.

## Agents

- **Writer** — prose in `articles/_staging/<slug>/index.md`
- **Graphics** (this lane) — figures, index updates, `IMAGE_SOURCES` for rasters
- **Editor** — moves folder to `articles/ready/` only when `GRAPHICS_CHECKLIST.md` is satisfied

## Validation

```bash
python3 tools/fig_graphics_validate.py content/fig-history-ancient-to-today
```
