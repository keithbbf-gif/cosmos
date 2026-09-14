# Editor report — Fig pruning calendars (zones 7–9)

**Editor + image SEO pass:** 2026-09-14  
**Writer PR:** https://github.com/keithbbf-gif/cosmos/pull/338 (`cursor/fig-pruning-calendars-2779`)  
**Editor branch:** `cursor/fig-pruning-calendars-editor-d261` (stacked on writer branch)  
**Scope:** `content/fig-pruning-calendars/[0-9][0-9]-*.md` (46 essays)

## Summary

| Check | Result |
| --- | --- |
| Drafts touched | **46 / 46** |
| `voice_check` | **`edited`** on every draft |
| `zone_center: 8a` | Present on all drafts (writer set) |
| `<figure>` + `figures:` YAML | **46 / 46** (PD/CC/USDA stand-ins) |
| `RIGHTS.md` | **Added** — 12 cleared rasters |
| Ban-list slop (bodies) | **0 hits** |
| Body word count | **~22.5k** total; each draft **≥ 280** words (short-card pack) |

## Editorial method

1. **Voice** — Kept writer's 8a-centered yard tone. No new extension claims; UGA/UF citations unchanged.
2. **Grammar** — Light fixes only where a line read ambiguous (see table). No pillar rewrites.
3. **Front matter** — `voice_check: edited` on all drafts; `figures:` block added per draft for import.
4. **Image SEO** — One `<figure>` per essay: descriptive `alt`, width/height, `loading="lazy"`, `decoding="async"`, caption credits PD/CC/USDA and points to `D:\FIGS` hero.

## Hand fixes (prose)

| File | Change |
| --- | --- |
| `01-zone-8a-year-calendar.md` | "heading-cut" → "heading cut" (verb phrase) |
| `19-mistake-cut-before-live-wood.md` | "scratch the bark" → "scratch the cambium" (clearer live-wood test) |
| `32-after-an-ice-storm.md` | Split run-on on split-leader repair |

## Intentionally not changed

- `README.md` draft index and source list (writer canon)
- Word-count targets — this pack is **short calendar cards**, not 1.1k-word essays
- No new drafts added or removed

## Validation

```bash
python3 content/fig-pruning-calendars/scripts/editor_voice_check.py
python3 content/fig-pruning-calendars/apply_graphics_pass.py
python3 content/fig-pruning-calendars/scripts/validate_pack.py
```

## Sign-off

Editor pass complete: `voice_check: edited`, image SEO figures with honest captions, `RIGHTS.md` ledger for staged rasters. Draft PR — do not merge until Keith reviews.
