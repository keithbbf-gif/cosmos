# Editorial calendar — architectural millwork and molding history (BBF lane)

Forty-four staged shop essays under `articles/`, each with two captioned SVG figures (88 files in `assets/`). Cadence is for a future Website-GC / WordPress staging site, not live publish.

Prose is filled and editor-passed. `voice_check: edited`. `lane: bbf-millwork`. Status remains `draft` until Keith clears publish. Graphics markers and figure embeds stay aligned with the graphics pack (`graphics_agent: v1`).

All files live under `content/millwork-molding-history/`.

## Pipeline

```bash
cd content/millwork-molding-history/scripts
python3 generate_graphics.py
python3 ../qa/check_pack.py
```

`generate_graphics.py` is safe to rerun; it overwrites SVGs only, not article prose.

## Companion files

- `STYLE_GUIDE.md` — voice, length, embed rules.
- `SHOP_GUARDRAILS.md` — not a spec, not a bid, no fake client names.
- `PHOTO_NOTES.md` — SVG / shop-plate policy.
- `GRAPHICS_INDEX.md` — figure manifest.
- `DRAFT_CHECKLIST.md` — writer status per slug.
- `BIBLIOGRAPHY.md` — sources named in the pack.
- `WP_IMPORT.md` — staging-import notes.
- `EDITOR_REPORT.md` — magazine-floor editor pass (PR #313).
- `qa/check_pack.py` — figure-contract + voice + length checks.

See `DRAFT_CHECKLIST.md` for the numbered file list.
