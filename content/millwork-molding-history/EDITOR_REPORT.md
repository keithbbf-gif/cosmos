# Editor report — millwork and molding history pack

**Role:** EDITOR (magazine-floor pass)  
**Writer branch:** `cursor/millwork-molding-history-9ed7` (PR #313)  
**Editor branch:** `cursor/millwork-molding-history-editor-ea65`  
**Scope:** `content/millwork-molding-history/` — 44 articles, pack QA, companion docs  
**Staging only:** no live publish  
**Date:** 2026-09-14  

## Stamp

- All **44** articles: `voice_check: edited` (read-aloud pass; grammar, spelling, shop voice).
- `qa/check_pack.py`: **PASS** (44 articles; YAML slugs, figures paths, two `graphics-pack:v1` markers, two Figure captions, SVG embeds, disclaimer, word floors, banned phrases).
- Shop plates, historical timelines, and `../assets/...` embed paths **unchanged**; H2 titles and figure order **unchanged**.

## What the editor did

### Voice and AI habits

- Full-series scan for STYLE_GUIDE hard bans (`delve`, `leverage`, `robust`, `seamless`, `tapestry`, `underscore`, `ever-evolving`, “it’s important to note,” “Whether you’re…,” “elevate your space,” etc.): **no violations** in body copy.
- Preserved deliberate shop shorthand (`each-parts`, `a dark` for shadow, punchy closings) and BBF / Warren / mill-town anchors.
- No new client names, bids, or spec language beyond existing guardrails.

### Copy-editing (prose)

| Article | Editor action |
| --- | --- |
| `24-cavetto-cove` | Clarified scotia cross-reference: “(see the scotia essay — there the job is night)” |
| `33-moisture-movement-cup` | “talked as” → “cited as” (interior MC target) |

All other essays were read in full. No duplicate paragraphs at sentence level; no late-section summary blocks that repeated earlier body copy (unlike some longer figure packs). Word counts remain **705–1105** (mean ~812).

### Structure and embeds

- Did **not** reorder the first two H2s, `figures:` YAML, `<!-- graphics-pack:v1 -->` blocks, `![...](../assets/...)` paths, or `*Figure 1/2*` captions.
- Did **not** edit SVG shop plates or timeline graphics (88 files under `assets/`).

### Pack tooling and docs

- `qa/check_pack.py`: accepts `voice_check: human` **or** `edited`.
- `STYLE_GUIDE.md`: documents the `edited` stamp.
- `DRAFT_CHECKLIST.md`, `INDEX.md`: writer column / stamp updated; `EDITOR_REPORT.md` listed in companion files.

## QA command

```bash
python3 content/millwork-molding-history/qa/check_pack.py
```

## Handoff

Merge editor branch onto writer PR **#313** after review. Import per `WP_IMPORT.md` to **staging** only when Keith clears publish. Do not merge to `main` without explicit approval.
