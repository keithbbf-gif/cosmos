# SLPWOW — History & Major Figures of Speech Pathology (staged graphics)

**Series path:** `content/slpwow-speech-pathology-history/`  
**Site:** SLPWOW.com (do not edit live theme or production deploy from this tree)

This folder holds **staged** article graphics: SVG figures, portrait plates, embed snippets for writers, and the graphics index. Writers paste figures from `embeds/` into article drafts when those drafts land under `articles/` (or the site CMS).

## Layout

| Path | Purpose |
|------|---------|
| `assets/<slug>/` | Publish-ready SVG figures per article slug |
| `assets/portraits/` | Licensed portrait files only (see `PORTRAIT_SOURCES.md`) |
| `embeds/<slug>.md` | Copy-paste figure blocks (path + caption) |
| `GRAPHICS_INDEX.md` | Machine- and human-readable catalog (regenerate via script) |
| `GRAPHICS_CHECKLIST.md` | Remaining slugs and portrait rights work |
| `PORTRAIT_SOURCES.md` | License ledger for every portrait file |
| `scripts/regenerate_graphics_index.py` | Rebuild `GRAPHICS_INDEX.md` from `assets/` |

## Portrait policy

Never generate or embed synthetic historical faces. Use files in `assets/portraits/` only when listed in `PORTRAIT_SOURCES.md`. Until then, use the framed **portrait pending** plate from `embeds/portrait-figure-block.md`.

## Graphics agent

See `AGENTS_GRAPHICS.md` for the standing brief and acceptance checks.
