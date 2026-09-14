# GRAPHICS agent — SLPWOW SLP News (practice wave)

## Deliverables per slug

1. SVG(s) under `assets/<slug>/` — news cards, timelines, infographics (typographic/schematic; **no faces**).
2. `embeds/<slug>.md` with `<figure>`, `itemscope` / `ImageObject`, SEO `alt`, dimensions, lazy load, claims-safe `<figcaption>`.
3. Row in `GRAPHICS_INDEX.md` (`python scripts/regenerate_graphics_index.py`).
4. Paste embed HTML into matching `articles/*.md` (generator: `python scripts/generate_practice_graphics.py`).
5. `RIGHTS.md` row per asset.

## Visual system

- `assets/_shared/editorial-palette.md`
- `PHOTO_NOTES.md`

## Acceptance

- [ ] Valid XML; `<title>` + `<desc>` (+ `role="img"`).
- [ ] Caption names schematic intent; links primary sources in prose.
- [ ] No synthetic or AI-generated faces.
- [ ] `GRAPHICS_CHECKLIST.md` updated per wave.
