# Image + SEO — sports-nutrition-rd-2020

Draft pack only. Figures support comprehension; they do not replace citations in the body.

## Asset rules

| Rule | Detail |
| --- | --- |
| No AI faces | No synthetic likenesses, no “athlete stock,” no generated portraits. Population pieces use charts or abstract icons only. |
| Original SVG | Schematics labeled **illustrative** in the caption. Numbers match cited papers or are clearly approximate. |
| PD / CC | Food or historical scientific art only when `RIGHTS.md` records license, source URL, and `ai_generated \| no`. |
| One hero file | Each `figures/<slug>/` folder holds exactly one `figure.svg` or `figure.jpg` plus `RIGHTS.md`. |
| Rasters | JPEG/PNG/WebP live only under `figures/`. |

## HTML pattern

Every draft embeds one hero `<figure>` immediately after the educational disclaimer:

```html
<figure class="sn-rd-figure sn-rd-figure--chart">
  <img src="../../figures/<slug>/figure.svg" alt="…" width="640" height="400" loading="lazy" />
  <figcaption>
    <strong>Schematic only.</strong> …
    <span class="figure-credit">… See figures/<slug>/RIGHTS.md.</span>
  </figcaption>
</figure>
```

Use `sn-rd-figure--photo` when the hero is a cleared photograph.

## YAML (SEO)

Add to front matter:

- `meta_description` — ≤160 characters, claims-safe, no disease language.
- `hero_figure` — `figures/<slug>/figure.svg` (or `.jpg`).
- `figure_status` — `original-svg` or `cleared-pd`.

## Captions (claims-safe)

- Lead with **Schematic only** or **Illustrative** when the graphic is not primary data.
- State what was measured in the source paper when a curve is inspired by a meta-analysis.
- Never imply treatment, disease prevention, or guaranteed body-composition outcomes.
- Credit line points at `RIGHTS.md`.

## QA

Run from this directory:

```bash
python3 check_pack.py
```

Exit 0 means structure, figures, RIGHTS, and banned phrases pass.
