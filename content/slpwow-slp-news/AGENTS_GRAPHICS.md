# GRAPHICS agent — SLPWOW SLP News (stage 46)

## Deliverables

1. Original SVG under `assets/<slug>/` — typographic schematics aligned to each article’s beat (ASLP-IC, Medicare, schools, research, practice).
2. `embeds/<slug>.md` with schema.org `<figure>` HTML for WordPress paste.
3. Inline the same `<figure>` in `articles/*.md` after the first `##` heading.
4. `RIGHTS.md` row per asset; optional PD/CC candidates documented but not embedded until licensed.
5. `GRAPHICS_INDEX.md` via `python scripts/regenerate_graphics_index.py`.

## Regenerate wave

```bash
cd content/slpwow-slp-news
python scripts/generate_graphics.py
python scripts/regenerate_graphics_index.py
python check_pack.py
```

## Hard rules

- No AI faces. No identifiable people in any raster. See `PHOTO_NOTES.md`.
- Do not embed CompactConnect, CMS, or state logos as endorsements — label in text only.
