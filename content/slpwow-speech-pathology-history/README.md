# SLPWOW — History of Speech-Language Pathology (staged)

Magazine series for a later import to **SLPWOW.com**. This folder is the pack. It is not a live-site edit, not COSMOS core, and not a furniture/figroots merge.

**Start here:** [`INDEX.md`](INDEX.md) (calendar + roster). Voice: [`STYLE_GUIDE.md`](STYLE_GUIDE.md). Portraits: [`PORTRAIT_SOURCES.md`](PORTRAIT_SOURCES.md). WordPress: [`WP_IMPORT.md`](WP_IMPORT.md). Graphics: [`GRAPHICS_CHECKLIST.md`](GRAPHICS_CHECKLIST.md).

Forty Markdown articles live in `articles/`. Editorial SVGs and portrait plates live under `assets/`. Writers paste ready HTML from `embeds/`.

## Layout

| Path | Purpose |
|------|---------|
| `articles/` | 40 era essays and profiles |
| `assets/<slug>/` | Publish-ready SVG figures per graphic slug |
| `assets/portraits/` | Licensed portrait files only |
| `embeds/<slug>.md` | Copy-paste figure blocks |
| `GRAPHICS_INDEX.md` | Catalog (regenerate via script) |
| `scripts/regenerate_graphics_index.py` | Rebuild the graphics index |

## Portrait policy

Never generate or embed synthetic historical faces. Use files in `assets/portraits/` only when listed as cleared in `PORTRAIT_SOURCES.md`. Until then, use a framed **portrait pending** plate (`embeds/portrait-figure-block.md`).

## Graphics agent

See `AGENTS_GRAPHICS.md` for the standing brief.
