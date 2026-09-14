---
title: Editor report — American Bedroom Furniture History
status: draft
voice_check: edited
series: american-bedroom-furniture-history
editor_pass: 2026-09-14
---

# Editor report

Editor pass on `content/american-bedroom-furniture-history/` — **45 staged drafts**, unified `voice_check: edited` across the pack. Stack for this PR: **`cursor/american-bedroom-furniture-fill-01-06-8166` (PR #516, chapters 01–06 fill)** on **`cursor/american-bedroom-furniture-editor-2bbe` (PR #450, editor pass 07–45)**. Do not merge this PR ahead of #450 or #516.

Criteria: **object-first** magazine voice (`STYLE_GUIDE.md`), trim **pack-meta** (“this chapter,” “next essay,” “this series needs”), **Bradley Brand** only on allowed slugs, `voice_check: edited` on every series `.md`.

## Scope

| Item | Count |
|------|------:|
| Draft articles (`drafts/*.md`) | **45** (chapters **01–45**) |
| Series files (INDEX, MANIFEST, STYLE_GUIDE, EDITOR_REPORT, WRITER_NOTE) | 5 |
| `[CITE NEEDED]` markers | retained (intentional gaps) |

**Total body words (01–45):** 108,180 (per `MANIFEST.md`; 01–06: 17,335; 07–45: 90,845).

## Principles applied

1. **Object-first** — Locked Met / Yale accessions on 01–06 ledes; 07–45 ledes unchanged where already strong.
2. **No pack-meta** — Removed cross-essay throat-clear in 01–06 (“gets its own essays,” “next essay,” “this series needs,” “southern testers essay,” “later joinery essay,” “later vanity essay”).
3. **Bradley Brand** — Unchanged from #450: only `36-arkansas-hardwood-bedrooms` and `43-a-shop-looking-at-a-highboy`.
4. **`voice_check`** — All pack `.md`: **`edited`** (01–06 promoted from `human`; 07–45 already `edited`).

## Substantive edits — chapters 01–06 (this pass)

| Slug | Change |
|------|--------|
| `01-the-chamber-before-the-suite` | Cut forward-reference lines to “essays”; close on high chests without pack pointer |
| `02-testers-and-hangings` | Southern climate without “testers essay”; bed-rail joint without “joinery essay” |
| `04-philadelphia-high-chest` | Newport shells without “next essay”; hallway connoisseurship without “this series” |
| `05-newport-block-and-shell` | Labels, knockdown / bureau-table / Grand Rapids lines without essay/series meta |
| `06-the-lowboy-partner` | Factory vanity type; Notes line without “vanity essay” |

Chapters **03** — front matter only (`voice_check`). Bodies already matched house style.

## Substantive edits — chapters 07–45 (PR #450, unchanged here)

| Slug | Change |
|------|--------|
| `13-grand-rapids-bedroom-factory` | Cut “brief for this chapter” from 1885 sales and Simmons/Berkey chronology |
| `35-solid-wood-revival-now` | Open on trade return; cut catalog/chapter meta |
| `36-arkansas-hardwood-bedrooms` | Bradley Brand as bench; heritage sentence close |
| `38-who-slept-where` | Drop “chapter 1 promised”; “bedroom record” not “this chapter” |
| `42-what-a-bedroom-is-now` | “Thin room is the honest subject” |
| `43-a-shop-looking-at-a-highboy` | Bradley Brand bench sentence without “may be named” |
| `44-childrens-beds-and-cradles` | Dek trim; honest inventory; federal register close |

## Not in this pass

- `living-room-chests-storage-history` (slug absent from repo).
- Figure pulls, WordPress import, or resolving `[CITE NEEDED]` claims.
- Word-band tightening for drafts above 2,800 words (flagged in MANIFEST; no cuts).

## QA checklist

- [x] 45 slugs present; INDEX/MANIFEST aligned
- [x] `status: draft` on articles
- [x] No `voice_check: human` under pack
- [x] `EDITOR_REPORT.md` + `STYLE_GUIDE.md` current
- [x] Pack-meta trimmed on 01–06; #450 edits preserved on 07–45

## Stack / merge order

1. **#450** — `cursor/american-bedroom-furniture-editor-2bbe` (07–45 editor)
2. **#516** — `cursor/american-bedroom-furniture-fill-01-06-8166` (01–06 fill on #450)
3. **This PR** — `cursor/american-bedroom-editor-unify-75a9` (editor unify 01–45, atop #516)

## See also

- `STYLE_GUIDE.md` — voice, BBF rule, front matter
- `MANIFEST.md` — per-slug word counts
- `INDEX.md` — draft list
- `WRITER_NOTE.md` — fill 01–06, locked objects, writer QA
