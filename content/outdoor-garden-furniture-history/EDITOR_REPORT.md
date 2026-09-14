# Editor report — Outdoor and garden furniture history

**Editor pass:** 2026-09-14  
**Writer branch / PR:** `pr-481` (staged BBF outdoor/garden furniture history drafts)  
**Editor branch:** `cursor/editor-outdoor-garden-furniture-3189`  
**Scope:** `content/outdoor-garden-furniture-history/drafts/*.md` (44 spoken narratives) + pack README + `validate_staging.py`

## Summary

| Check | Result |
| --- | --- |
| Drafts edited | 44 / 44 |
| `voice_check` | `edited` on every draft |
| `last_edited` | `2026-09-14` on every draft |
| `validate_staging.py` banned phrases | 0 hits |
| `status: staged` | Preserved on all drafts |
| `voice: shop-floor-first-person` | Unchanged on all drafts |
| Net prose change | Light; one bridge line + grammar fix in `educational_claim` |

## Editorial method

1. **Voice** — Kept shop-floor first person (Ferdinand, indoor custom shop, outdoor as adjacent history). Preserved the series habits: climate before SKU, stolen-word policing, BBF refusal lines, and the maker/buyer/designer triad where the writer already used it. Did not add catalog claims, outdoor SKUs, or warranty language.
2. **Shop-floor beats** — Writer’s post-validator thicken pass (veneer teak, railing-as-chair steel, sling reskin, fastener bruises, wicker repair economics, roof-before-zip-code) was left intact; those lines already read on-camera.
3. **Grammar** — Fixed `not a invented patio SKU` → `not an invented patio SKU` in `08-44-bbf-collections-adjacent.md` frontmatter (`educational_claim`).
4. **Pack gate** — `validate_staging.py` now requires `voice_check: edited` and `last_edited`. README documents the editor metadata beside the existing structural checks.

## Files with body edits (beyond YAML)

| Draft | Change |
| --- | --- |
| `00-02-three-climates.md` | Closing bridge tightened for spoken handoff to `00-03` |
| `08-44-bbf-collections-adjacent.md` | Grammar: `not an invented patio SKU` in `educational_claim` |

All other drafts: `voice_check: edited` + `last_edited` only (prose already met bar after writer pass).

## Intentionally not changed

- Draft order, slugs, titles, `educational_claim` text (except grammar above), `topics`, `sequence_after`
- Series bridge lines (`The next draft…`, material handoffs at episode ends)
- `SOURCES.md` verify notes (off-camera by design)
- No new drafts, no cuts to the 44-piece set

## Validation

```bash
python3 content/outdoor-garden-furniture-history/validate_staging.py
python3 content/outdoor-garden-furniture-history/validate_staging.py --write-manifest
```

## Sign-off

Editor pass complete: shop-floor voice retained, `voice_check: edited` set, structural validator green. Ready for Keith’s on-camera cut; **not for merge** without his review.
