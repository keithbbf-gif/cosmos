# Editor report — CBT history deepen pack

**Role:** EDITOR (magazine-floor pass)  
**Writer branch:** `cursor/cbt-history-deep-29aa` (PR #343)  
**Editor branch:** `cursor/cbt-history-deep-editor-2b07`  
**Scope:** `content/cbt-history-deep/` — 44 articles + pack QA  
**Staging only:** no live wowtherapies.com changes  
**Date:** 2026-09-14  

## Stamp

- All **44** articles: `voice_check: edited` (read-aloud pass; grammar, spelling, human voice).
- `check_pack.py`: **PASS** (44 drafts, YAML, educational note, banned phrases, DIY leaks, word floors, INDEX slugs).
- Portraits: all drafts remain `portrait: none` or type-only instructions per `PHOTO_NOTES.md` / `PORTRAIT_SOURCES.md` — **no AI faces**, no scraped workshop photos.

## What the editor did

### Voice and AI habits

- Full-series scan for `STYLE_GUIDE.md` hard bans (delve, landscape-as-field, Moreover stacks, gold-standard treatment, telegram padding, etc.): **no violations** in body copy after pass.
- Preserved deliberate anti-protocol lines (worksheet / exposure / breathing refusals) as historical guardrails, not instructions.

### Structure and repetition

Writer drafts carried **late-section padding** that repeated earlier paragraphs (word-floor closings after the telegram-closing fix). Editor removed duplicate blocks and replaced cut material with **non-repetitive** dated bridges so figure floors still hold.

| Article | Editor action |
| --- | --- |
| `25-joseph-wolpe` | Collapsed repeated Stanford / WOW / staffing paragraphs; kept Temple 1965 + Jones neighbor |
| `27-arnold-a-lazarus` | Dropped repeated sharpness / rural-hour blocks; added 1981 practice-book bridge |
| `30-david-h-barlow` | Merged CARD / UP section without second critics / 2002 repeat |
| `34-jon-kabat-zinn` | Kept 1982 paper as new object; cut duplicated Buddhist / hospital beats |
| `36-neil-s-jacobson` | Trimmed repeated 1996 / WOW blocks; added 1979 couples + BA-manual interval note |
| `37-christine-a-padesky` | Merged 1993 London section without re-pasting workbook body |
| `38-david-d-burns-feeling-good` | Tightened 1989 handbook section; removed triple Ellis / household repeat |
| `39-dianne-l-chambless` | Collapsed leaked-table reprise; kept 1995 newsletter + Hollon 1998 thread |
| `43-stefan-g-hofmann` | Kept 2012 meta-review; removed duplicated 2008 / 2018 / transatlantic blocks |
| `44-adrian-wells` | Kept 1994 Matthews volume; removed repeated Beck / Hayes / Manchester paste |

Twenty era essays and remaining figure essays were read in full on spot-check; no additional paraphrase-duplicate pairs above editorial threshold required surgery.

### Claims / DIY

- No new treatment protocols, worksheets, hierarchies, or self-administer content added.
- Existing refusals (thought records, SUDS, body scans, MCT tasks, list-as-menu, etc.) **kept**.

### Pack ops

- `MANIFEST.md`: lists `EDITOR_REPORT.md`.
- `README.md`: points editors to this report.

## QA command

```bash
python3 content/cbt-history-deep/check_pack.py
```

## Handoff

Merge editor branch **onto** writer branch #343 after review. Import per `WP_IMPORT.md` to **staging** only when Keith approves. **Do not merge to `main` without claims + portrait review.**
