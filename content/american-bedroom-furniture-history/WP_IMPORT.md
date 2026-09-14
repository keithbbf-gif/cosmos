---
title: WordPress import notes
series: American Bedroom Furniture
status: draft
voice_check: human
---

# WordPress import — draft only

Nothing in this folder is cleared to `publish`. The series is a **staged** draft for an editor pass (grammar, spelling, style) and a photo-rights pass.

Import from `staged/`, not from `drafts/`. The two trees should match after the writer self-edit. If they diverge, `staged/` is the file the CMS may touch; `drafts/` remains the writer’s working copy.

## Suggested WP settings

| Field | Value |
| --- | --- |
| Post status | `draft` |
| Visibility | private or password until legal/photo review |
| Category | Bedroom furniture history (create; do not file under product or shop) |
| Tags | per-essay `period` from YAML; no brand tags on ch. 1–35 |
| Author | to be assigned |
| Featured image | none until a CC0 or licensed hero is chosen from `PHOTO_CAPTIONS.md` |
| Excerpt | YAML `dek`, or first 40–50 words after the title |
| Custom fields | `series=American Bedroom Furniture`, `chapter=NN`, `voice_check=human`, `status=draft` |

## Import order

1. Create a parent page or category landing from `INDEX.md` (converted). Still a draft.
2. Import essays **01 → 45** as drafts, slugs exactly as YAML `slug:`.
3. Do not auto-schedule. No `publish_date` as a sneak-publish.
4. Convert `## Figure plan` blocks into WP captions only after rights are confirmed. Until then, leave them in a custom field `figure_plan`.
5. `PHOTO_CAPTIONS.md` is the rights register. If a row says confirm or reserved, do not upload that file as if it were free.

## What not to do

- Do not run an SEO plugin that adds banned phrases from `STYLE_GUIDE.md`.
- Do not append shop links, affiliate blocks, or “related products” to chapters 1–35.
- Chapters 36, 42, 43, and 45 may mention Arkansas hardwood and a living shop as history and practice. They may not grow a buy-button in the CMS.
- Do not strip `[CITE NEEDED]` in the public draft.
- Do not upload copyrighted interiors or unlicensed catalog plates.

## Staging checklist (per post)

Copied into `staged/STAGING.md`. Every staged file must still say `status: draft`.
