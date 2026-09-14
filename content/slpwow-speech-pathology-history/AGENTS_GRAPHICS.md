# GRAPHICS agent — SLPWOW Speech Pathology History

## Deliverables per article slug

1. One or more SVGs under `assets/<slug>/` (clinical-editorial, not clip-art).
2. Matching `embeds/<slug>.md` with relative paths, `<figure>` / caption, alt text.
3. Row in `GRAPHICS_INDEX.md` (run `scripts/regenerate_graphics_index.py`).
4. Portrait articles: framed plate via `embeds/portrait-figure-block.md` until `assets/portraits/<id>.<ext>` is cleared in `PORTRAIT_SOURCES.md`.

## Visual system

- Palette and type notes: `assets/_shared/editorial-palette.md`
- Reuse stroke weights, label caps, and margin grid across slugs.

## Acceptance

- [ ] SVG validates as XML; includes `<title>` and `<desc>`.
- [ ] Caption in embed matches figure purpose; credit line if portrait.
- [ ] No uncredited portrait imagery.
- [ ] Checklist updated for slugs still in draft.
