# Style guide — furniture finishing chemistry

**Series folder:** `content/furniture-finishing-chemistry/`  
**Audience:** furniture shop — finish behavior, not formulation lab.  
**Fence:** shop-safe rules in `README.md` and draft `05-the-shop-safe-fence.md`.

## Figures (required for web import)

Each numbered draft (01–45) carries:

1. **One shop diagram** — cream/ink SVG at `assets/<slug>/shop-diagram.svg`.  
2. **One photograph** — file under `photos/` (PD or Creative Commons only; see `RIGHTS.md`).  
3. **Two `<figure>` blocks** in the body after the opening paragraph(s), before the first `##` section.

### HTML pattern

```html
<figure class="ffc-figure">
  <img src="assets/<slug>/shop-diagram.svg" alt="…SEO alt…" width="640" height="420" loading="lazy" decoding="async" />
  <figcaption><strong>Figure 1.</strong> …caption visible to reader…</figcaption>
</figure>

<figure class="ffc-figure ffc-photo">
  <img src="photos/<file>.jpg" alt="…SEO alt…" width="640" height="480" loading="lazy" decoding="async" />
  <figcaption><strong>Figure 2.</strong> …caption plus license clause…</figcaption>
</figure>
```

**SEO rules**

- `alt` is a plain-language description (what the image shows), not a keyword stack.  
- `meta_description` in YAML is one or two sentences from the lede — no hype.  
- `figcaption` repeats the teaching point; Figure 2 ends with `Photo: …` per `RIGHTS.md`.  
- Diagram `alt` and `graphics[].alt` must match.

### Front matter additions

```yaml
meta_description: "One or two sentences for excerpt / search snippet."
graphics:
  - asset_slug: <slug>
    path: assets/<slug>/shop-diagram.svg
    alt: "…"
    caption: "…"
figures:
  - id: photo-1
    path: photos/<file>.jpg
    alt: "…"
    caption: "…"
```

## Regeneration

| Task | Command |
| --- | --- |
| SVG diagrams + `GRAPHICS_INDEX.md` | `python3 tools/generate_furniture_finishing_chemistry_graphics.py` |
| Download Commons photos | `python3 tools/fetch_furniture_finishing_chemistry_photos.py` |
| Embed figures + YAML | `python3 tools/embed_furniture_finishing_chemistry_figures.py` |

Run **graphics → photos → embed** after changing slugs or photo map.

## Voice

Same banned list as other BBF content packs: no delve, landscape (metaphor), robust, leverage, unlock, cutting-edge, game-changer, “In today’s,” “It’s important to note,” Moreover, “Whether you’re,” “In conclusion,” fake dualities, invented quotes.

Claims tie to shop consequence. Chemistry serves the use board, not the other way around.

## WordPress

Import as **draft** only. Do not schedule publish from this pack.
