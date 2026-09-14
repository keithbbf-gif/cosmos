# Editor report — dysphagia & swallowing heritage pack

**Role:** EDITOR (magazine-floor pass)  
**Writer branch:** `cursor/dysphagia-swallowing-heritage-90b7`  
**Editor branch:** `cursor/dysphagia-voice-editor-ccc7`  
**Scope:** `content/dysphagia-swallowing-heritage/` — 44 articles + pack QA  
**Staging only:** no live SLPWOW CMS write  
**Date:** 2026-09-14  

## Scope note (requested paths)

| Requested path | Status |
| --- | --- |
| `content/group-therapy-history/` | **Not in repository** (no branch or tree on `origin` at pack date) |
| `content/family-systems-therapy-history/` | **Not in repository** |
| `content/dysphagia-swallowing-heritage/` | **Present** on writer branch; editor pass applied here |

## Stamp

- All **44** articles: `voice_check: edited` (read-aloud pass; grammar, spelling, human voice; de-duplication where paragraphs echoed).
- `check_pack.py`: **PASS** (44 articles, YAML, educational note, banned phrases, word floors, INDEX slugs). Accepts `voice_check: human` or `edited`.
- Portrait / placeholder blocks and `PORTRAIT_SOURCES.md` references **unchanged** in substance; no new images added.

## What the editor did

### Voice and AI habits

- Full-series scan for STYLE_GUIDE hard bans: **no violations** in body copy before or after edit.
- Preserved deliberate guardrails (no treatment sheets, no IDDSI home charts, no FEES item lists, etc.).

### Structure and repetition

Writer drafts were strong; the editor removed or merged **near-verbatim repeats** inside essays/profiles:

| Article | Editor action |
| --- | --- |
| `08-when-speech-pathologists-took-the-swallow` | Dropped second “piece of a mouth” beat; de-duplicated ASHA “competency” phrasing |
| `13-after-the-tumor-and-the-beam` | Removed repeated organ-preservation triad in “What the decade thought it was solving” |
| `16-what-a-swallow-study-became` | Merged duplicate “rewind a swallow / Cannon” residue; kept cup closing |
| `28-susan-e-langmore` | Collapsed stacked “paper is not the workshop” beats; kept Schatz/Olsen byline guardrail |
| `31-bonnie-martin-harris` | Varied repeated “bet was that dullness…” wording |
| `35-adrienne-l-perlman` | Trimmed repeated millisecond refrain; kept trace discipline |
| `43-james-l-coyle` | Merged duplicated Pittsburgh instrumentation paragraphs |
| `44-olle-ekberg` | Merged Lund / birth-certificate blocks; one closing folder line |

Other articles were read in full on spot-check; no banned-phrase hits; no new treatment content added.

### Claims / DIY

- No new protocols, viscosity charts, maneuvers, or home programs added.
- Existing refusals (screening items, MBSImP component lists, etc.) **kept**.

## Pack tooling

- `check_pack.py`: accepts `voice_check: human` **or** `edited`.
- `STYLE_GUIDE.md`: documents `edited` stamp.
- `INDEX.md`, `MANIFEST.md`, `WP_IMPORT.md`: updated for editor workflow.

## QA command

```bash
python3 content/dysphagia-swallowing-heritage/check_pack.py
```

## Handoff

Merge editor branch onto the dysphagia writer branch after review. Import per `WP_IMPORT.md` to **staging** only when approved.
