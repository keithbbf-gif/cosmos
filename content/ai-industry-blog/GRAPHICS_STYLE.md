# Graphics style — AI industry blog

Design tokens shared by `scripts/render_graphics.py` and hand-tuned wave-2 SVGs.

| Token | Hex | Use |
|-------|-----|-----|
| Paper background | `#FAF8F5` | Artboard fill |
| Ink | `#141414` | Titles, primary labels |
| Ink muted | `#5C574F` | Body copy in figures |
| Ink light | `#8A847A` | Footnotes |
| Rule line | `#E3DDD4` | Dividers, card borders |
| Accent cool | `#1E4D6B` | Years, arrows, lane emphasis |
| Accent warm | `#B85C38` | Markers, callout rails |
| Accent soft | `#D4E4ED` | Card header strips |
| Card fill | `#FFFFFF` | Boxes on paper |

## Typography

- **Titles:** Georgia / Times, 26px, semibold
- **Subtitles & labels:** system-ui, 12–14px
- **Footnotes:** 10px, muted

## Layout

- Timelines: 1200×640
- Architecture / flow boxes: 1100×620 (or noted variants)
- Wave 2 infographics: `infographic-*.svg`, `fig-02-*.svg`, `decision-tree-*.svg`, `callout-*.svg` under `assets/<slug>/`
- Keep in-image text to short labels; long prose stays in article body

## Accessibility

- Minimum contrast: ink on paper and ink on white cards (WCAG AA for labels)
- Every SVG includes `<title>` and `<desc>` via renderer
- Articles supply `alt` on `<img>` in embed blocks

## Regeneration

```bash
python3 content/ai-industry-blog/scripts/render_graphics.py
python3 content/ai-industry-blog/scripts/embed_wave2_figures.py
```

Wave 1 assets use `timeline.svg`, `diagram.svg`, or `explainer.svg`. Wave 2 uses distinct filenames to avoid overwriting PR #234 art.
