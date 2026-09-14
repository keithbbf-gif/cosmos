# Editor report — family systems therapy history pack

**Role:** EDITOR (magazine-floor pass, sibling catch-up to dysphagia heritage lane)  
**Writer branch:** `cursor/family-systems-therapy-history-02ad`  
**Editor branch:** `cursor/family-systems-voice-editor-aa98`  
**Scope:** `content/family-systems-therapy-history/` — 44 articles + pack QA  
**Staging only:** no live WOW Therapies CMS write  
**Date:** 2026-09-14  

## Scope note (requested paths)

| Requested path | Status |
| --- | --- |
| `content/dysphagia-swallowing-heritage/` | **Editor pass on** `cursor/dysphagia-voice-editor-ccc7` (parallel lane; not merged here) |
| `content/group-therapy-history/` | **Not in repository** (no branch or tree on `origin` at pack date) |
| `content/family-systems-therapy-history/` | **Present** on writer branch; editor pass applied here |

## Stamp

- All **44** articles: `voice_check: edited` (read-aloud pass; grammar, spelling, human voice; de-duplication where late-draft sections echoed).
- `check_pack.py`: **PASS** (44 articles, YAML, educational note, banned phrases, word floors, INDEX slugs). Accepts `voice_check: human` or `edited`.
- Portrait / placeholder blocks and `PORTRAIT_SOURCES.md` references **unchanged** in substance; no new images added.

## What the editor did

### Voice and AI habits

- Full-series scan for STYLE_GUIDE hard bans: **no violations** in body copy before or after edit.
- Preserved deliberate guardrails (no session scripts, genogram worksheets, home protocols, etc.).

### Structure and repetition

Writer drafts were strong; the editor merged **near-verbatim repeats** in late figure essays:

| Article | Editor action |
| --- | --- |
| `15-after-the-mirror-race-class-consent` | Merged duplicate Southeast Arkansas / drive-home closing beats |
| `28-john-weakland` | Collapsed stacked 1919–1995 / 1974 / MRI temperament sections |
| `30-steve-de-shazer` | Merged duplicate Milwaukee / Norton 1985 / safety-warning blocks |
| `38-nancy-boyd-franklin` | Merged triple 1989 / Guilford / WOW Therapies / booking-keyword repeats |
| `42-lyman-wynne` | Collapsed four stacked 1958 / Rochester / ethics closing sections |

Other articles were read on spot-check; no banned-phrase hits; no new treatment content added.

### Claims / DIY

- No new protocols, genograms, circular-question lists, or home programs added.
- Existing refusals (booking-keyword misuse, living-writer care, etc.) **kept**.

## Pack tooling

- `check_pack.py`: accepts `voice_check: human` **or** `edited`.
- `STYLE_GUIDE.md`: documents `human` vs `edited` stamps.
- `INDEX.md`, `MANIFEST.md`, `WP_IMPORT.md`: unchanged except this report.

## QA command

```bash
python3 content/family-systems-therapy-history/check_pack.py
```

## Handoff

Merge editor branch onto the family-systems writer branch after review. Import per `WP_IMPORT.md` to **staging** only when approved. For dysphagia heritage, merge `cursor/dysphagia-voice-editor-ccc7` on its own timeline.
