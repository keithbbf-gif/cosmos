# Editor report — Wilmar and the Saline River

**PR:** [#348](https://github.com/keithbbf-gif/cosmos/pull/348)  
**Scope:** `content/wilmar-saline-river-local-history/` (46 essays + house files)  
**Pass:** quality voice edit (`voice_check: edited`)  
**Date:** 2026-09-14  

## What this pass did

1. **Voice check flag** — Set `voice_check: edited` on all 46 essays. Updated `STYLE_GUIDE.md` and `WP_IMPORT.md` to document the field after an editor pass.
2. **Dedup read** — Essay **29** (*Gate City*): removed a paragraph that repeated Beauvoir’s 1907 close and the 1920 census peak already stated in the same section; kept the stave-factory and commercial-slack thread.
3. **Citation hygiene** — Essay **41** (workshop name): pointed prose and sources to `BIBLIOGRAPHY.md` instead of a repo path that may not be checked out in every clone; kept the Fig Jam interview and soft-link rules intact.
4. **Automated slop scan** — Banned AI-phrase list from `STYLE_GUIDE.md` run across all articles; no hits except essay **33**, which *names* “hidden gem” as forbidden house language.

## What this pass did not do

- Did not change `status: staged`, `wp_status: draft`, or mix codes.
- Did not smooth source seams (Gates 1889/1890, *Gate City* dates, June Dinner oral history) — those stay visible on purpose.
- Did not publish, add SKUs, or add shop CTAs.

## Automated checks (post-pass)

| Check | Result |
|---|---|
| Essay count | 46 |
| `voice_check: edited` on every essay | yes |
| Banned slop phrase scan | clean |
| COSMOS / mesh leakage in articles | none |
| Duplicate sentences within an essay | none found |

## Manual read notes

- Ken Burns register and “film the still” meta are intentional series rhythm, not template filler.
- Essay **41** remains the only shop-centered piece; BBF soft-link rules unchanged elsewhere.

## Residual risks (low)

- Body word counts were not re-run in this pass; PR #348 QA band (~1,275–2,352 words) assumed still valid after small trims in **29**.
- External SEO map file may land in another tree; `BIBLIOGRAPHY.md` remains the stable pointer.

## Files touched

- `articles/29-the-gate-city.md`, `articles/41-a-workshop-named-for-a-river.md`: substantive line edits.
- All `articles/*.md`: `voice_check: edited`.
- `STYLE_GUIDE.md`, `WP_IMPORT.md`, `EDITOR_REPORT.md`: house docs.
