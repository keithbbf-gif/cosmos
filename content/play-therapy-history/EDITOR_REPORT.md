# Editor report — play therapy history pack

**Role:** EDITOR (magazine-floor pass)  
**Writer branch:** `cursor/play-therapy-history-4eed` (PR #494)  
**Editor branch:** `cursor/play-therapy-history-editor-1589`  
**Scope:** `content/play-therapy-history/` — 45 articles + pack QA  
**Staging only:** no live wowtherapies.com changes  
**Date:** 2026-09-14  

## Stamp

- All **45** articles: `voice_check: edited` (read-aloud pass; grammar, voice, guardrails).
- `check_pack.py`: **PASS** (45 articles, YAML, educational note, claims box, banned phrases, word floors, INDEX slugs).
- Portrait / figure embed instructions and `PORTRAIT_SOURCES.md` references **unchanged** in substance; no new images added.

## What the editor did

### Voice and AI habits

- Full-series scan for `STYLE_GUIDE.md` hard bans (`check_pack.py` regex list): **no violations** introduced; deliberate quotes of "father of play therapy" and "eight principles" remain as myth/history refusals, not endorsements.
- Replaced in-body **"this pack"** framing with **"this series," "this essay,"** or explicit ops paths where prose would read like repo metadata (notably across profession and critique-stage drafts).

### Structure and repetition

Writer drafts carried **late-section recap blocks** at word floors. Editor removed or merged duplicates and replaced cut material with **non-repetitive** bridging sentences.

| Article | Editor action |
| --- | --- |
| `21-garry-landreth-unt` | Removed duplicated UNT timeline block; added filmed-demo / board-service beats without eulogy-as-protocol |
| `32-bapt-and-uk-registration` | Collapsed repeated NHS/cabinet recaps; deepened Tavistock / export-flattening fences |
| `34-bratton-2005-meta` | Merged duplicate 376–390 / weather paragraphs; added wait-list and APA-placement context |
| `41-living-people-public-documents` | Removed duplicated public/not-public list; added workshop-audio and featured-image rules |
| `42-what-a-small-city-clinic-inherited` | Removed duplicated homepage/inheritance block; added telehealth and IEP boundary |
| `45-map-to-sister-packs` | Removed duplicated sister-pack walk section; added trauma/group lane pointers and anti-merge note |
| `13-margaret-lowenfeld` | Meta frame: "this pack" → "this series" in body |

Automated paragraph similarity **≥0.72** within edited articles after pass: **none** on the worst prior offenders (spot re-scan).

### Claims / DIY

- No new treatment protocols, room lists, filial homework, sand-tray interpretation, or "try at home" counsel added.
- Existing refusals (Axline principles as laminate, toy catalogs, RPT-as-license, crisis one-liners) **kept**.

### Copy-editing

- Light grammar and cohesion in merged paragraphs only.
- `[VERIFY]` markers **unchanged** in intent (Guerney death year, Jernberg 1993 cluster, Landreth birth year, BAPT/PTUK society pages, Axline 1950 cite in bibliography).

## Pack tooling

- `check_pack.py`: accepts `voice_check: human` **or** `edited`.
- `MANIFEST.md`: updated for editor pass stamp.

## QA command

```bash
python3 content/play-therapy-history/check_pack.py
```

## Handoff

Merge editor branch **onto** writer branch #494 after review. Import per `WP_IMPORT.md` to **staging** only when Keith approves. **Draft PR; do not merge** without human sign-off.
