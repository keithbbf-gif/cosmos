# GRAPHICS agent — SLPWOW pediatric milestones

## Deliverables per flagship slug

1. One or more SVGs under `assets/<slug>/` (parent-facing editorial, not clip-art; **no child likenesses**).
2. Matching `embeds/<slug>.md` with `<figure>`, SEO-friendly `alt`, `width`/`height`, `loading="lazy"`, and a claims-safe `<figcaption>`.
3. Row in `GRAPHICS_INDEX.md` (run `scripts/regenerate_graphics_index.py`).
4. Rights line in `RIGHTS.md` for every asset.

## Visual system

- Palette: `assets/_shared/editorial-palette.md`
- Photo rules: `PHOTO_NOTES.md`

## Acceptance

- [ ] SVG validates as XML; includes `<title>` and `<desc>` (and `role="img"` where appropriate).
- [ ] Caption states schematic intent; no diagnostic or eligibility promises.
- [ ] No uncredited raster portraits; no synthetic faces.
- [ ] Flagship articles link embeds after editor sign-off (wave 1 slugs first).
