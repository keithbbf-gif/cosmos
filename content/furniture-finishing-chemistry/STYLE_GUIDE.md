# Furniture finishing chemistry — STYLE_GUIDE

Shop-safe visuals for the finishing-chemistry series (draft PR #303). No hazmat glamour.

## Tone

Bench and booth seriousness: what the film does on *your* board, not a chemical-industry photoshoot. No smoke, fire, explosion, or drum-farm hero shots. Safety articles use **schematics** (metal waste can, ventilation arrow), not disaster stock.

## Figures

- Primary teaching art: **SVG schematics** in `assets/<slug>/shop-diagram.svg` (pack-authored, CC0).
- Optional **Photo 2** slots: real wood/finish reference images from Wikimedia Commons or other cleared PD/CC sources — ledgered in `RIGHTS.md`.
- Every numbered draft embeds HTML:

```html
<figure class="ffc-figure">
  <img src="assets/<slug>/shop-diagram.svg" alt="…" width="640" height="420" loading="lazy" decoding="async" />
  <figcaption><strong>Figure 1.</strong> …</figcaption>
</figure>
```

- `alt` is SEO-aware: species, finish family, shop action (sand, recoat, dispose rags).
- `figcaption` states shop consequence, not adjectives.

## Frontmatter

Add on each article:

- `meta_description` — ≤155 characters, plain sentence.
- `graphic.primary` / `graphic.alt` — points at the SVG.
- `photo.*` — when a raster slot is filled.

## Ban list (visual)

- Hazmat suits, flaming rags, methylene-chloride glamour, glowing solvent bottles.
- Copyrighted catalog finishes pasted as “examples.”
- Mislabeled stock (bar fire photo on a rag-disposal article).

## Regenerate

```bash
python3 content/furniture-finishing-chemistry/scripts/generate_graphics.py
python3 content/furniture-finishing-chemistry/scripts/fetch_photos.py
python3 content/furniture-finishing-chemistry/scripts/embed_figures.py
python3 content/furniture-finishing-chemistry/scripts/write_graphics_index.py
```
