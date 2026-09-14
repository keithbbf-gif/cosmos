# Editor report — therapy history pack

**Role:** EDITOR (magazine-floor pass)  
**Writer branch:** `cursor/wowtherapies-therapy-history-b51d` (PR #268)  
**Editor branch:** `cursor/wowtherapies-therapy-history-editor-a2ab`  
**Scope:** `content/wowtherapies-therapy-history/` — 42 articles + pack QA  
**Staging only:** no live wowtherapies.com changes  
**Date:** 2026-09-14  

## Stamp

- All **42** articles: `voice_check: edited` (read-aloud pass; grammar, spelling, human voice).
- `check_pack.py`: **PASS** (42 articles, YAML, educational note, banned phrases, word floors, INDEX slugs).
- Portrait / figure embed instructions and `PORTRAIT_SOURCES.md` references **unchanged** in substance; no new images added.

## What the editor did

### Voice and AI habits

- Full-series scan for STYLE_GUIDE hard bans (delve, landscape-as-field, Moreover stacks, gold-standard treatment, etc.): **no violations** in body copy.
- Tightened a few kinship clichés (e.g. “more than one father” → “more than one inventor” in the hypnosis era essay).
- Preserved deliberate anti-protocol lines (worksheet / “try at home” refusals) as historical guardrails, not instructions.

### Structure and repetition

Writer drafts had **late-section summary paragraphs** that repeated earlier body copy (common on figure essays at the 1,000-word floor). Editor removed or merged duplicates and replaced cut material with **non-repetitive** bridging sentences so floors still hold.

| Article | Editor action |
| --- | --- |
| `03-hypnosis-hysteria-talking-cure` | Dropped repeated Bernheim beat; inventor wording |
| `04-psychoanalytic-century` | Merged 1926 pamphlet lead into lay-analysis paragraph |
| `07-systems-and-families` | Removed second Bowen diagram block; kept family-of-origin note |
| `08-cognitive-empirical-turn` | Removed duplicate managed-care / rural paragraph |
| `09-attachment-in-the-room` | Removed duplicate ward/consulting-room beat; kept one scaled argument |
| `10-trauma-lineages` | Trimmed repeated Kardiner/forgetting block; added cross-series bridge; ICD citation hyphenation |
| `11-feminist-relational` | Fixed orphan “Those collected volumes” (Boston Lesbian Psychologies lead-in) |
| `28-albert-ellis` | Removed duplicated early-career / institute paragraph; restored concise early-career beat |
| `32-virginia-satir` | Collapsed duplicate Avanta/MRI closing; kept geography + franchise tension |
| `36-ignacio-martin-baro` | Shortened Portrait section (was re-pasting body); kept bio-page test |
| `41-judith-herman` | Removed near-verbatim repeats of NYT/DSM lag and triad/worksheet blocks; unified Living section |

Other figure essays were read in full; paraphrase-duplicate pairs above **0.72** similarity were reduced where found (Ellis, Satir). Remaining closings are distinct at paragraph level.

### Claims / DIY

- No new treatment protocols, worksheets, or self-administer content added.
- Existing refusals (DBT skills, miracle question scripts, Morita stages at home, Herman stages as plan, etc.) **kept**.

### Copy-editing

- Citation YAML: `complex post-traumatic stress disorder` (Herman, trauma era).
- Light grammar and cohesion fixes in merged paragraphs only.

## Pack tooling

- `check_pack.py`: accepts `voice_check: human` **or** `edited`.
- `STYLE_GUIDE.md`: documents `edited` stamp.
- `MANIFEST.md`: lists `EDITOR_REPORT.md`.

## QA command

```bash
python3 content/wowtherapies-therapy-history/check_pack.py
```

## Handoff

Merge editor branch **onto** writer branch #268 after review. Import per `WP_IMPORT.md` to **staging** only when Keith approves.
