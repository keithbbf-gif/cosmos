---
title: WordPress import notes
series: Healthcare / Institutional Furniture
status: staged
voice_check: human
lane: bbf-furniture
---

# WordPress import — staged only

Nothing in this folder is cleared to `publish`. The series is staged Website-GC copy for an editor pass (grammar, spelling, style), a photo-rights pass, and Keith’s publish click.

## Suggested WP settings

| Field | Value |
| --- | --- |
| Post status | `draft` (YAML `status: staged`) |
| Visibility | private or password until legal/photo review |
| Category | Furniture history / Healthcare interiors (create; do not file under product) |
| Tags | YAML `tags`; living-manufacturer names are historical nouns, not shop tags |
| Author | to be assigned |
| Featured image | none until a CC0 or licensed hero is chosen from `PHOTO_CAPTIONS.md` |
| Excerpt | YAML `meta_description` |
| Custom fields | `series`, `chapter`, `lane=bbf-furniture`, `voice_check`, `status=staged` |

## Import order

1. Parent landing from `INDEX.md` (converted), still draft.
2. Import essays **01 → 44** as drafts, slugs exactly as YAML `slug:`.
3. Do not auto-schedule.
4. Convert `## Figure plan` blocks into WP captions only after rights are confirmed.
5. Keep the educational italic under the title.

## What not to do

- Do not run a plugin that “improves SEO” by adding banned phrases from `STYLE_GUIDE.md`.
- Do not append shop links, affiliate blocks, or “related products.”
- Do not strip `[CITE NEEDED]` or `[VERIFY]`.
- Do not turn F-tag essays into a survey-consulting lead magnet.
- Do not invent accession numbers at import.

## Files that are not posts

`STYLE_GUIDE.md`, `OUTLINES.md`, `INDEX.md`, `BIBLIOGRAPHY.md`, `PHOTO_CAPTIONS.md`, `TIMELINE.md`, `MANIFEST.md`, `DRAFT_CHECKLIST.md`, `CLAIMS_GUARDRAILS.md`, `validate_staging.py`, this file.
