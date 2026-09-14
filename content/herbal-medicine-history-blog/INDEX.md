# Editorial calendar — history of herbal medicine, drugs, and supplements

Forty dated magazine essays under `articles/`, each with two captioned SVG figures (80 files in `assets/`). Cadence is for a future WordPress staging site, not live publish.

Prose is filled. `voice_check: human`. Status remains `draft` until Keith clears publish. Graphics markers and figure embeds stay aligned with the graphics pack (`graphics_agent: v1`).

All files live under `content/herbal-medicine-history-blog/`.

## Pipeline (do not rerun blindly)

```bash
cd content/herbal-medicine-history-blog/scripts
# bootstrap_articles.py  — regenerates SHELLS and will wipe filled prose
# generate_graphics.py   — SVG assets (already landed)
# embed_graphics.py      — captioned embeds + figures: front matter
python3 ../qa/check_pack.py
```

`bootstrap_articles.py` is a shell factory. Do not run it on this filled tree unless you intend to replace every lede.

## Companion files

- `STYLE_GUIDE.md` — voice, length, embed rules.
- `CLAIMS_GUARDRAILS.md` — no cure marketing or fake efficacy art.
- `PHOTO_NOTES.md` — SVG / line-plate policy.
- `GRAPHICS_INDEX.md` — figure manifest.
- `DRAFT_CHECKLIST.md` — writer status per slug.
- `BIBLIOGRAPHY.md` — sources named in the pack.
- `WP_IMPORT.md` — staging-import notes.
- `qa/check_pack.py` — figure-contract + voice + length checks.

See `DRAFT_CHECKLIST.md` for the numbered file list.
