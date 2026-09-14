---
title: Editor report — American Arts and Crafts / Mission Furniture (deep)
status: staged
voice_check: edited
series: American Arts and Crafts / Mission Furniture
editor_pass: 2026-09-14
writer_branch: cursor/arts-crafts-mission-furniture-deep-c03c
---

# Editor report

Editor pass on `content/arts-crafts-mission-furniture-deep/` (fallback lane: `content/healthcare-institutional-furniture/` is not present in this repo). Criteria: magazine voice per `STYLE_GUIDE.md`, banned-phrase scan, light American spelling harmonization, `voice_check: edited` on all series markdown.

## Scope

| Item | Count |
|------|------:|
| Draft articles (`drafts/*.md`) | 44 |
| Series apparatus (`*.md` at series root) | 10 |
| `validate_staging.py` | 1 (accepts `human` or `edited`) |

Word band **1800–2600** unchanged; writer manifest counts stand.

## Summary

| Check | Result |
| --- | --- |
| Drafts reviewed | 44 / 44 |
| `voice_check: edited` in frontmatter | 53 / 53 series `.md` files |
| `validate_staging.py` | PASS (post-edit) |
| STYLE_GUIDE banned phrases | No hits |
| Bradley Brand / sell copy | Ch. 44 only (per brand rule) |
| `[CITE NEEDED]` / `[VERIFY]` | Unchanged (editor does not invent) |

## Editorial method

1. Full-series read against `STYLE_GUIDE.md` (object-first ledes, no sell, no COSMOS/AI talk).
2. Automated banned-phrase scan (`validate_staging.py` regex + manual grep).
3. American spelling harmonization where the writer used British forms in running prose (not in quoted catalog titles).
4. Did **not** rewrite argument, add takeaway lists, renumber figure plans, or fill citation gaps.

## Substantive body edits

| Slug | Change |
|------|--------|
| `factory-mission-grand-rapids` | *catalogue* → *catalog* in running prose; *tap room* → *taproom* |
| `american-morris-chair` | *catalogued* → *cataloged* (auction-house verb) |

All other drafts: prose already clean; **metadata only** (`voice_check: edited`).

## Brand compliance

| Location | Bradley Brand / living maker |
|----------|------------------------------|
| `drafts/44-hardwood-towns-still-speak.md` | Yes — historical mill-town sentence (allowed) |
| Drafts 01–43 | None |

## Validator

`validate_staging.py` now accepts `voice_check: human` (writer) or `voice_check: edited` (post-editor). Essays still require `status: staged`, word band, figure count, and brand rule for chapters 1–43.

## Handoff

Stacked on writer branch `cursor/arts-crafts-mission-furniture-deep-c03c`. Merge writer first or merge this editor branch into the writer branch for a single publication PR.
