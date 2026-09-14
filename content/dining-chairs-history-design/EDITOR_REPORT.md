---
title: Editor report — Dining Chairs, History and Sitting
status: draft
voice_check: edited
series: dining-chairs-history-design
editor_pass: 2026-09-14
---

# Editor report

Editor pass on `content/dining-chairs-history-design/` for **PR #456** (writer branch `cursor/dining-chairs-history-design-581b`). Criteria: **magazine teach-don't-sell** voice per `STYLE_GUIDE.md`, read-aloud copy-edit, duplicate-block cleanup, `voice_check: edited` on all series markdown. **Draft PR — do not merge to `main` without review.**

## Stamp

- All **46** essays: `voice_check: edited`.
- Pack meta (`INDEX.md`, `MANIFEST.md`, `STAGING_README.md`, `BIBLIOGRAPHY.md`, `PHOTO_CAPTIONS.md`, `WP_IMPORT.md`): editor stamp recorded.
- `[VERIFY]` / `[CITE NEEDED]` pins: **retained** in body and front-matter `verify` lists.
- `STYLE_GUIDE.md`: unchanged except this report cross-reference; self-edit section still names the writer → human → editor workflow.

## What the editor did

### Voice

- Incoming stack already matched the brief: object-first ledes, table–chair pair as the argument, anti-catalog Bradley Brand lines where the writer placed them (`01-the-chair-at-dinner`, `33-arms-that-clear`, `34-host-and-hostess`, `42-arkansas-oak-side-chair`).
- No new product names, CTAs, or “our craftsmen” language added.
- BIFMA / ISO office-chair cousins left as written (named as wrong house for dinner, not dining law).

### Copy-editing and structure

| Slug / file | Change |
| --- | --- |
| Pack-wide | Removed **10** exact duplicate paragraphs (≥80 chars, normalized) left from writer expansion passes — see automated list below. |
| `breuer-cesca-and-the-tube` | Dropped redundant early **Pairing** section and repeated “two-hour fatigue” / copies lines; kept expanded sled, cane, and pairing-without-museum sections. |
| `queen-anne-compass-seat` | Removed repeated Pheasant-percentile and labor blocks; one labor paragraph remains under cabriole/apron. |
| `host-and-hostess` | Removed one exact duplicate humor line; retained expanded clearance and shop sections (some thematic echo between sections is intentional rank/clearance rhythm). |

### Claims and brand

- Bradley Brand / heritage URLs remain **footnote-only** in front matter where the writer placed them.
- `arkansas-oak-side-chair` remains the only draft allowed a local shop sentence in the body; no SKU names in body copy.

## QA notes

- **46** drafts, **76,510** body words after dedup (range per `MANIFEST.md`; all within **1,400–2,200** band).
- All `status: draft`; figure slots still `needed` until museum or `D:\BBF` pulls.
- WordPress: draft-only per `WP_IMPORT.md`.

## Automated checks run

- `STYLE_GUIDE` hard-ban grep on all draft bodies: **clean** (no delve/landscape-as-metaphor/tic list hits in body copy).
- Exact duplicate paragraph scan after edit: **clean**.
- `word_count` front matter vs body recount (Sources excluded): **46/46 match**.

### Duplicate blocks removed (by file)

| File | Blocks removed |
| --- | ---: |
| `22-wegner-y-and-the-wishbone.md` | 1 |
| `26-ikea-ingolf-and-the-flat-chair.md` | 3 |
| `30-rake-is-not-a-lounge.md` | 2 |
| `33-arms-that-clear.md` | 2 |
| `34-host-and-hostess.md` | 1 |
| `42-arkansas-oak-side-chair.md` | 1 |

## Handoff

Merge editor branch **`cursor/dining-chairs-history-design-editor-f759`** onto writer branch **#456** after review. Import per `WP_IMPORT.md` when Keith approves photographs and rights. **Draft PR — do not merge to `main` without review.**
