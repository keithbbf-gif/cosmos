# AI industry blog (content)

Editorial drafts and shared assets for a long-form AI industry publication (target ≥40 drafts). **Graphics** live under `assets/<slug>/`; catalog in [`GRAPHICS_INDEX.md`](GRAPHICS_INDEX.md).

- **Staged embeds:** [`staged/FIGURE_EMBEDS.md`](staged/FIGURE_EMBEDS.md)
- **Regenerate:** `python3 content/ai-industry-blog/scripts/render_graphics.py`
- **Style tokens:** [`GRAPHICS_STYLE.md`](GRAPHICS_STYLE.md)
- **Embed drafts:** `python3 content/ai-industry-blog/scripts/embed_wave2_figures.py`
- **Wave 2 checklist:** [`staged/WAVE2_CHECKLIST.md`](staged/WAVE2_CHECKLIST.md)

Draft markdown is expected under `drafts/` as the writing stream lands copy; this PR seeds the graphics layer only.
