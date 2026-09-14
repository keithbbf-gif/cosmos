---
title: Editor report — American Dining Room Furniture, 1700–Now
status: draft
voice_check: edited
series: american-dining-room-history
editor_pass: 2026-09-14
pr: 324
---

# Editor report

Editor pass on `content/american-dining-room-history/` for PR #324. Criteria: **object-first** lede, **no sell** (magazine voice per `STYLE_GUIDE.md`), `voice_check: edited` on all series markdown.

## Scope

| Item | Count |
|------|------:|
| Draft articles (`drafts/*.md`) | 44 |
| Series files (INDEX, MANIFEST, STYLE_GUIDE, BIBLIOGRAPHY, PHOTO_CAPTIONS, STAGING_README) | 6 |
| `[CITE NEEDED]` markers (unchanged; intentional gaps) | 13 |

Word band 1,400–2,200: unchanged from writer manifest (44 drafts; total body words ~70,157 before this pass; lede edits are net-neutral).

## Principles applied

1. **Object-first** — Ledes that opened on etymology, trend lines, or store openings were rewritten to start on a piece, joint, or accession the reader can picture.
2. **No sell** — Removed SEO/pillar meta, Bradley Brand / BBF mentions outside the single allowed slug (`arkansas-southern-hardwood-dining`). No CTAs, no “our craftsmen,” no pillar-map process talk in body copy.
3. **Voice** — Kept magazine density; trimmed duplicate price-book paragraphs where the lede already named the object; left `[CITE NEEDED]` and museum pins as written.
4. **Banned phrasing** — Full-series scan: no new violations of the STYLE_GUIDE banned list (incidental “landscape” in Baltimore painted furniture = pictorial, not metaphor).

## Substantive lede / body edits (drafts)

| Slug | Change |
|------|--------|
| `hunt-board-southern-vernacular` | Open on James Park inscribed drawer; defer “hunt board” name; remove BBF/pillar copy; dedupe Park paragraph |
| `arkansas-southern-hardwood-dining` | Open on quartersawn oak behavior; drop pillar meta; Bradley Brand retained only in closing shop sentence |
| `hepplewhite-sideboard-arrives` | Open on Shearer 1788 priced form + Hepplewhite plates; trim repeated price-book paragraph |
| `empire-pillar-and-claw` | Open on glue blocks under pedestal; dedupe in “pillar as knee” section |
| `boston-salem-colonial-dining` | Open on maple gateleg before regional thesis |
| `ikea-flatpack-table` | Open on flat box, cam locks, hex key; Plymouth Meeting in section two |
| `grand-rapids-factory-dining` | Remove BBF / pillar-map closing |
| `butler-pantry-breakfast-room` | Remove BBF shop paragraph |
| `shaker-trestle-dining` | Remove Bradley Brand comparison |
| `charleston-southern-colonial-dining` | Replace brand sentence with woodshed contrast |
| `colonial-revival-dining` | Replace BBF vernacular line with furniture comparison |

## Brand compliance (after pass)

| Location | Bradley Brand / BBF |
|----------|---------------------|
| `drafts/arkansas-southern-hardwood-dining.md` | Yes — one closing sentence (allowed) |
| All other drafts | None |
| `INDEX.md`, `STYLE_GUIDE.md`, `STAGING_README.md` | Series context only (not article body) |

## `voice_check`

All series `.md` files: `voice_check: human` → `voice_check: edited`.

## Not in this pass

- Photograph plan / `PHOTO_CAPTIONS.md` execution (still staged plates only).
- WordPress publish dates (remain unset).
- New accession numbers or invented prices.
- Resolving `[CITE NEEDED]` items (13 remain; see drafts grep).

## QA checklist

- [x] 44 slugs present; `writer-slugs.json` unchanged
- [x] Unique `primary_keyword` per slug (writer QA retained)
- [x] No invented accession numbers in pinned examples (writer QA retained)
- [x] `status: draft` on all articles
- [x] Object-first pass on weakest ledes (see table)
- [x] Sell/pillar language stripped from article bodies

## See also

- `STYLE_GUIDE.md` — voice and banned phrasing
- `STAGING_README.md` — SEO staging rules
- `MANIFEST.md` — word counts
