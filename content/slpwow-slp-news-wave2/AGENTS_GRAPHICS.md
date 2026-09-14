# GRAPHICS agent — SLPWOW SLP News wave 2

## Deliverables

1. Original **SVG infographics** under `assets/<slug>/` — typographic schematics aligned to each brief’s public document (CMS, ASHA, compact, research, literacy desk).
2. `embeds/<slug>.md` with schema.org `<figure>` HTML for WordPress paste.
3. Inline the same `<figure>` in `articles/*.md` after the first `##` heading.
4. `RIGHTS.md` row per asset (generated with the scripts).
5. `GRAPHICS_INDEX.md` via `python scripts/regenerate_graphics_index.py`.

## Regenerate wave

```bash
cd content/slpwow-slp-news-wave2
python3 scripts/generate_graphics.py
python3 scripts/regenerate_graphics_index.py
python3 check_pack.py
```

## Hard rules

- **Educational SVG only.** No photographs, no AI faces, no child likenesses. See `PHOTO_NOTES.md`.
- **No PHI.** No student names, IEP identifiers, or therapy worksheets.
- Do not embed CompactConnect, CMS, or state logos as endorsements — label in text only.
- Figure SEO: every SVG needs `<title>` and `<desc>`; every article needs `ImageObject` figure markup with `alt`, `contentUrl`, and `caption`.
