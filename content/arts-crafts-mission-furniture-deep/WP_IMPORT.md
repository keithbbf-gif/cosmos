---
title: WordPress import notes
series: American Arts and Crafts / Mission Furniture
status: staged
voice_check: edited
lane: bbf-furniture
---

# WordPress import — staged only

Nothing in this folder is cleared to `publish`. The series is staged Website-GC copy for an editor pass (grammar, spelling, style) and a photo-rights pass.

## Suggested WP settings

| Field | Value |
| --- | --- |
| Post status | `draft` (YAML `status: staged`) |
| Visibility | private or password until legal/photo review |
| Category | Furniture history / Arts and Crafts (create; do not file under product) |
| Tags | YAML `tags`; no living-brand tags on ch. 1–43 |
| Author | to be assigned |
| Featured image | none until a CC0 or licensed hero is chosen from `PHOTO_CAPTIONS.md` |
| Excerpt | YAML `meta_description` |
| Custom fields | `series`, `chapter`, `lane=bbf-furniture`, `voice_check=edited`, `status=staged` |

## Import order

1. Parent landing from `INDEX.md` (converted), still draft.
2. Import essays **01 → 44** as drafts, slugs exactly as YAML `slug:`.
3. Do not auto-schedule.
4. Convert `## Figure plan` blocks into WP captions only after rights are confirmed. Until then, store as custom field `figure_plan`.
5. `PHOTO_CAPTIONS.md` is the rights register. If a row says “rights reserved” or “confirm,” do not upload it as free.

## What not to do

- Do not run a plugin that “improves SEO” by adding banned phrases from `STYLE_GUIDE.md`.
- Do not append shop links, affiliate blocks, or “related products” to chapters 1–43.
- Chapter 44 may mention American hardwood towns and shops that still speak this language as history. It may not grow a buy-button in the CMS.
- Do not strip `[CITE NEEDED]` or `[VERIFY]`.
- Do not invent accession numbers at import.

## Staging checklist (per post)

- [ ] Status is `draft` in WP / `staged` in YAML
- [ ] `voice_check: edited` preserved (post editor pass)
- [ ] Body word count 1800–2600 before notes
- [ ] Figure plan 4–7, each with alt text
- [ ] No product CTAs
- [ ] Internal links only to other drafts in this series

## Files that are not posts

`STYLE_GUIDE.md`, `OUTLINES.md`, `INDEX.md`, `BIBLIOGRAPHY.md`, `PHOTO_CAPTIONS.md`, `TIMELINE.md`, `MANIFEST.md`, `DRAFT_CHECKLIST.md`, `validate_staging.py`, this file.
