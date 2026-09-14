# Editorial calendar — history of herbal medicine, drugs, and supplements

Forty staged drafts (shell prose + embedded SVG figures). Cadence is for a future WordPress staging site, not live publish.

All files live under `content/herbal-medicine-history-blog/`. Status: `draft`.

## Pipeline

```bash
cd content/herbal-medicine-history-blog/scripts
python3 bootstrap_articles.py   # refresh shells from pack_data (Grok-safe regen)
python3 generate_graphics.py    # SVG assets
python3 embed_graphics.py       # captioned embeds + figures: front matter
```

## Companion files

- `STYLE_GUIDE.md` — voice and embed rules.
- `CLAIMS_GUARDRAILS.md` — no cure marketing or fake efficacy art.
- `PHOTO_NOTES.md` — SVG / line-plate policy.
- `GRAPHICS_INDEX.md` — figure manifest.
- `DRAFT_CHECKLIST.md` — writer status per slug.

See `DRAFT_CHECKLIST.md` for the full numbered file list.
