---
title: Graphics index — dining chairs history and sitting
status: draft
voice_check: edited
series: dining-chairs-history-design
---

# Graphics index — IMAGE + SEO pass (2026-09-14)

Forty-six draft essays each carry **one lead `<figure class="dchd-figure">`** with lazy-loaded museum/Wikimedia art or pack SVG schematics (no repo JPEGs of collection objects). Rights: `assets/figures/REGISTRY.toml` and `RIGHTS.md`. Slug → plate map: `_editorial/figure_assignments.toml`.

```bash
python3 content/dining-chairs-history-design/scripts/generate_dchd_svgs.py
python3 content/dining-chairs-history-design/scripts/build_registry.py
python3 content/dining-chairs-history-design/_editorial/embed_figures.py
python3 content/dining-chairs-history-design/_editorial/check_figures.py
python3 content/dining-chairs-history-design/scripts/render_rights_md.py
```

## Frontmatter added per draft

- `figure_id` — key into `REGISTRY.toml`
- `image_rights: documented`
- `image_pass: 2026-09-14`
- `voice_check: edited` (image pass; prose unchanged)
- `figures[]` **unchanged** — BBF shop slots stay `status: needed`

## Layer summary

| Layer | Count | Role |
| --- | ---: | --- |
| Museum / Commons lead | 34 | Historical object or published plate with documented license |
| Pack SVG schematic | 12 | Ergonomics and shop measurement essays — no faces |
| BBF publish heroes outstanding | 8 rows | `PHOTO_CAPTIONS.md` shop table |

## Schematic slugs (CC0 SVG)

`the-chair-at-dinner`, `eighteen-inches`, `the-gap-under-the-apron`, `seat-depth-and-the-knee`, `rake-is-not-a-lounge`, `lumbar-is-the-wrong-word`, `the-front-rail-and-the-thigh`, `arms-that-clear`, `rack-is-the-dinner-test`, `children-at-the-table`, `a-chair-a-wheelchair-can-meet`, `how-to-measure-a-dining-chair`.

## SEO figure rules

- One lead figure per URL; `alt` matches the sitting fact, not keyword stuffing.
- `meta_description` unchanged from editor pass.
- Figcaption ends with `<em>Rights:</em>` line tied to `REGISTRY.toml`.
- No AI-generated faces; children essay uses furniture/tape schematic only.
