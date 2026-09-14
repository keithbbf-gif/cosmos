---
title: WordPress import notes
series: History of Furniture
status: draft
voice_check: human
---

# WordPress import — draft only

Nothing in this folder is cleared to `publish`. The series is a staged draft for an editor pass (grammar, spelling, style) and a photo-rights pass.

## Suggested WP settings

| Field | Value |
| --- | --- |
| Post status | `draft` |
| Visibility | private or password until legal/photo review |
| Category | Furniture history (create; do not file under product or shop) |
| Tags | per-essay `regions` and `period` from YAML; no brand tags on ch. 1–42 |
| Author | to be assigned |
| Featured image | none until a CC0 or licensed hero is chosen from `PHOTO_CAPTIONS.md` |
| Excerpt | first 40–50 words after the title, not a marketing blurb |
| Custom fields | `series=History of Furniture`, `chapter=NN`, `voice_check=human`, `status=draft` |

## Import order

1. Create a parent page or category landing that points to `INDEX.md` (converted).
2. Import essays **01 → 43** as drafts, slugs exactly as YAML `slug:`.
3. Do not auto-schedule. No `publish_date` in the future as a sneak-publish.
4. Convert `## Figure plan` blocks into WP captions only after rights are confirmed. Until then, leave them in a custom field `figure_plan` or as an HTML comment in the draft.
5. `PHOTO_CAPTIONS.md` is the rights register. If a row says “rights reserved” or “confirm,” do not upload that file to the media library as if it were free.

## What not to do

- Do not run a plugin that “improves SEO” by adding banned phrases from `STYLE_GUIDE.md`.
- Do not append shop links, affiliate blocks, or “related products” to chapters 1–42.
- Chapter 43 may mention American mill towns and Arkansas hardwood as history. It may not grow a buy-button in the CMS.
- Do not strip `[CITE NEEDED]` in the public draft; those marks are for the editor and fact-checker.
- Do not upload Harry Burton / Griffith Institute photographs without a license. Prefer Met CC0, Smithsonian CC0, and Wikimedia PD.

## Staging checklist (per post)

- [ ] Status is `draft`
- [ ] YAML `voice_check: human` preserved in a custom field
- [ ] Body word count 1800–2800 before notes (recount after editor pass)
- [ ] Figure count 3–8, each with alt text
- [ ] No AI-banned phrases introduced by a rewriter
- [ ] Internal links only to other drafts in the series, not to live product URLs

## Files that are not posts

`STYLE_GUIDE.md`, `INDEX.md`, `BIBLIOGRAPHY.md`, `PHOTO_CAPTIONS.md`, `TIMELINE.md`, `MANIFEST.md`, this file. Keep them in the repo. If a public “about this series” page is wanted later, write it from `INDEX.md` after the editor pass — still as draft.
