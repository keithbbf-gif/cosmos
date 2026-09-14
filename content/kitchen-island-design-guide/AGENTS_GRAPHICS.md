# GRAPHICS agent — kitchen island design guide

## Deliverables per illustrated draft

1. Raster (only PD/CC/museum/gov) or SVG under `assets/<topic>/`.
2. `embeds/<slug>.md` with HTML `<figure>`, descriptive `alt`, SEO-natural `<figcaption>`.
3. Inline the same HTML block in `drafts/<id>-<slug>.md` after the opening claim paragraph (WXR-safe).
4. Row in `GRAPHICS_INDEX.md`.
5. License row in `RIGHTS.md` before commit.

## Hard rules

- **Never** AI faces, AI room renders, or unidentified stock lifestyle kitchens.
- Alt text: plain language, includes “kitchen island” or the specific dimension/code topic where natural.
- Captions: one sentence of teaching value + optional credit span for photos.
- Diagrams: follow `assets/_shared/editorial-palette.md`.

## Acceptance

- [ ] SVG validates; raster is JPEG/PNG with verified license chain.
- [ ] `tools/check_island_drafts.py` still passes.
- [ ] Figure paths are relative from `drafts/` as `../assets/...`.
