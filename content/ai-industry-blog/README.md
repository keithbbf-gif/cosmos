# AI industry blog (content)

Editorial drafts and shared assets for a long-form AI industry publication (target ≥40 drafts). **Graphics** live under `assets/<slug>/`; catalog in [`GRAPHICS_INDEX.md`](GRAPHICS_INDEX.md).

- **Staged embeds:** [`staged/FIGURE_EMBEDS.md`](staged/FIGURE_EMBEDS.md)
- **Regenerate:** `python3 content/ai-industry-blog/scripts/render_graphics.py`
- **Style tokens:** [`GRAPHICS_STYLE.md`](GRAPHICS_STYLE.md)
- **Embed drafts:** `python3 content/ai-industry-blog/scripts/embed_wave2_figures.py`
- **Wave 2 checklist:** [`staged/WAVE2_CHECKLIST.md`](staged/WAVE2_CHECKLIST.md)

Drafts live in `drafts/` (42 pieces, 2020–2026). Figure HTML is already embedded via the wave-2 script; re-run that script after changing `staged/wave2_draft_figure_plan.json`. This folder is draft-only — no WordPress deploy.
