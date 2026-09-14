---
title: Editor report — American Bedroom Furniture History
status: draft
voice_check: edited
series: american-bedroom-furniture-history
editor_pass: 2026-09-14
---

# Editor report

**Role:** EDITOR (magazine-floor pass)  
**Writer PR:** [#462](https://github.com/keithbbf-gif/cosmos/pull/462) — `cursor/american-bedroom-furniture-history-34e6` (full forty-five staged drafts)  
**Editor branch:** `cursor/american-bedroom-furniture-editor-7352`  
**Scope:** `content/american-bedroom-furniture-history/` — all **45** essays, staged mirrors, pack QA, companion docs  
**Staging only:** no live publish  

## Stamp

- All **45** draft and staged essays: `voice_check: edited` (read-aloud pass; grammar, spelling, object-first voice).
- Series apparatus (`INDEX.md`, `MANIFEST.md`, `STYLE_GUIDE.md`, `BIBLIOGRAPHY.md`, `PHOTO_CAPTIONS.md`, `TIMELINE.md`, `WP_IMPORT.md`, `EDITOR_REPORT.md`): `voice_check: edited`.
- `tools/qa_drafts.py`: accepts `voice_check: human` **or** `edited`; **PASS** on editor branch (45 drafts, 0 problems).
- Figure plans, `[CITE NEEDED]` markers, BBF brand placement (ch. 36, 42, 43, 45), and slugs **unchanged** unless noted below.

## What the editor did

### Voice and AI habits

- Full-series scan for `STYLE_GUIDE` hard bans (`delve`, `leverage`, `robust`, `seamless`, `unpack`, throat-clearing closers, etc.): **no violations** in body copy.
- Trimmed **pack-meta** (“brief for this chapter,” “this chapter is not a catalog,” “chapter 1 promised,” “may be named as”) where it stepped out of the room; kept deliberate “this chapter” lines that anchor an object or scope (e.g. southern testers, Eastlake disclaimer, McCobb notes).
- Preserved shop shorthand, inventory voice, and BBF-adjacent sentences without catalog language.

### Copy-editing (prose) — substantive

| Slug | Editor action |
| --- | --- |
| `13-grand-rapids-bedroom-factory` | Removed assignment “brief” language from 1885 sales and Berkey/Simmons chronology |
| `35-solid-wood-revival-now` | Open on trade return; cut catalog/chapter meta; “revival that matters here” |
| `36-arkansas-hardwood-bedrooms` | Inland luxury without “this chapter”; Bradley Brand as bench; “record does not need” close |
| `38-who-slept-where` | Drop “chapter 1 promised”; “bedroom record” not “this chapter” |
| `42-what-a-bedroom-is-now` | “Thin room is the honest subject” |
| `43-a-shop-looking-at-a-highboy` | Bradley Brand bench sentence without “may be named” |
| `44-childrens-beds-and-cradles` | Dek trim; “honest inventory”; federal register close |

Chapters **01–06** and all other slugs were read in full on the PR #462 tree. No banned-phrase hits; no brand leaks outside allowed chapters. No duplicate-paragraph blocks found at sentence level.

### Pack tooling and docs

- `tools/qa_drafts.py`: `edited` stamp allowed post-editor.
- `STYLE_GUIDE.md`: documents `voice_check: edited`.
- `MANIFEST.md`: total body words **90,367**; ch. 13 and 44 counts updated after trim.
- `staged/`: refreshed from `drafts/` (except `STAGING.md`).

## Not in this pass

- Photo rights clearance or figure pulls (see `PHOTO_CAPTIONS.md`).
- Resolving `[CITE NEEDED]` claims (fact-checker).
- WordPress import or `publish` status.
- Deliberate flattening of voice into brochure English.

## QA command

```bash
python3 content/american-bedroom-furniture-history/tools/qa_drafts.py
```

## Handoff

Review this editor branch against writer **PR #462**. Merge editor onto #462 (or stack) after Keith’s read. Import per `WP_IMPORT.md` to **staging** only when cleared. **Do not merge to `main` without explicit approval.**
