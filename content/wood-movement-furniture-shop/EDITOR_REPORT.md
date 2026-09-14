---
title: Editor report — wood movement furniture shop
slug: editor-report-wood-movement-furniture-shop
status: draft
series: wood-movement-furniture-shop
stage: 0
stage_name: index
order: 0
topic: [editor]
audience: shop
safety: shop-safe
voice: human
voice_check: edited
---

# Editor report — `content/wood-movement-furniture-shop/`

**Lane:** Cursor Cloud Agent (editor pass)  
**Branch:** `cursor/wood-movement-furniture-shop-37d0`  
**PR:** #499 (draft; do not merge from this pass)  
**Date:** 2026-09-14  

## Scope

Full voice edit on all fifty numbered drafts (`01`–`50`). House rules:
[`STYLE_GUIDE.md`](STYLE_GUIDE.md), shop-safe fence in [`README.md`](README.md).
**FPL / Wood Handbook:** uncertain numeric cells stay marked **`[VERIFY]`** in
body copy; nothing in this pass removes or softens those tags.

## Voice and structure

- **Shop-floor voice:** Tightened closings that repeated the dek or doubled an
  earlier section. Deduped overlapping blocks where two headings said the same
  bench lesson.
- **Openings:** No banned thesis openers found; left strong in-room leads
  unchanged.
- **Banned lexicon:** No live use of STYLE_GUIDE hard bans in body copy.

### Files with substantive body edits

| File | Edit |
| --- | --- |
| `01-the-crack-that-wasnt-your-glue.md` | Inline `[VERIFY]` on Handbook tangential coefficient before the worked example. |
| `07-three-directions-one-cut-list.md` | Inline `[VERIFY]` on species coefficient list. |
| `10-moisture-content-is-not-humidity.md` | Cut EMC stanza that restated §Ticket grammar; kept one closing noun line. |
| `11-the-scrap-paper-formula.md` | `[VERIFY]` on 6–14% MC band / FPL-RP-711 linearity note. |
| `13-cups-away-from-the-pith.md` | Replaced redundant closing with one witness-cut line. |
| `14-pin-meters-and-the-holes.md` | Moved glue/knot needle rule out of duplicate tail; added waste-vs-show disagreement habit. |
| `15-pinless-and-the-species-setting.md` | Cut duplicate “species at lunch” tail; kept rule in §Settings. |
| `19-a-number-you-can-defend.md` | Removed duplicate “Write it on the door” block (merged into §Write it where the argument happens). |
| `20-august-shop-january-shop.md` | Removed dek-echo triplet before kitchen-drawer anecdote. |
| `23-stickering-like-you-mean-it.md` | Removed duplicate §Finished doors (already in §Finished parts). |
| `31-doors-in-february.md` | Merged pair-door + bead + case-side notes; merged hinge-mortise story; added slab vs frame closing. |
| `32-cross-grain-a-year-later.md` | Cut calendar-inspector tail; rephrased meta pointer to “another draft in the pack.” |
| `36-oak-will-teach-you.md` | `[VERIFY]` on first oak coefficient block. |
| `37-walnut-and-cherry-still-move.md` | `[VERIFY]` on walnut/cherry coefficients; cut plywood one-liner tail. |
| `38-maple-beech-and-the-pale-shove.md` | `[VERIFY]` on maple and beech coefficient lines. |
| `41-plywood-until-the-veneer-splits.md` | Cut closing that restated title/dek before van anecdote. |
| `50-the-cut-list-checklist.md` | Shortened series-epilogue close; ends on clipboard / travel blank. |

### Light pass (voice_check only unless noted)

Drafts `02`–`06`, `08`–`09`, `12`, `16`–`18`, `21`–`22`, `24`–`30`,
`33`–`35`, `39`–`40`, `42`–`49`: read against STYLE_GUIDE; no body change
except front-matter `voice_check` and recomputed `word_count`. Existing inline
`[VERIFY]` tags (e.g. `02`, `06`, `09`, `12`, `15`, `18`, `19`, `24`, `39`)
left intact.

## `[VERIFY]` / FPL consistency

After edit, inline **`[VERIFY]`** appears in body on Handbook-sensitive
numerics in: `01`, `02`, `06`, `07`, `09`, `11`, `12`, `15`, `18`, `19`,
`24`, `36`, `37`, `38`, `39`, plus EMC/RH targets called out in `SOURCES.md`
and `README.md`. Species drafts that state coefficients only in YAML `verify:`
without inline tags were brought in line where coefficients are quoted in prose
(`01`, `07`, `11`, `36`, `37`, `38`).

**Not verified in this pass:** No shelf edition of the Wood Handbook was
opened; editor did not confirm cells against FPL. Tags remain for Keith /
runtime verify.

## Front matter

- All fifty drafts: **`voice_check: edited`**
- **`word_count`:** recomputed from body only (YAML excluded); table in
  [`MANIFEST.md`](MANIFEST.md) updated to match.
- **`status: draft`** unchanged on all pieces.

## Length bar

STYLE_GUIDE target **650–1,100** words body. After cuts/adds, **`14-pin-meters-and-the-holes.md`**
was brought back above 650 with shop-useful lines (waste vs show, glue-up wait).
All other pieces remain in band per manifest.

## Intentional series repeats

The **12″ × 0.00369 × 4 ≈ 0.177″** spine across multiple drafts is
intentional syllabus echo; editor did not dedupe across files.

## Figures / WordPress

No figure credits invented. No publish scheduling. Import remains **draft**
per pack README.

## Suggested follow-ups (human)

1. Confirm `[VERIFY]` cells against the Handbook edition on the shelf; remove
   tags only with artifact.
2. Fill `figures` / `PHOTO_CAPTIONS.md` from `D:\BBF\BBF Photos` when cleared.
3. Optional: vary the worked 12″ oak example in later stages so the series
   feels less like a chorus (not required for draft stage).

## Editor sign-off

Fifty drafts edited for shop-floor voice, duplicate closings reduced, FPL
uncertainty preserved with **`[VERIFY]`**, manifest counts refreshed,
**`voice_check: edited`** on all numbered files. Ready for human read on PR
#499 as **draft**.
