# Editor report — ACT / mindfulness therapy history pack

**Role:** EDITOR (magazine-floor pass)  
**Writer branch:** `cursor/act-mindfulness-therapy-history-2d6b` (PR #412)  
**Editor branch:** `cursor/act-mindfulness-editor-9d16`  
**Scope:** `content/act-mindfulness-therapy-history/` — 45 articles + pack QA  
**Staging only:** no live wowtherapies.com changes  
**Date:** 2026-09-14  

## Stamp

- All **45** articles: `voice_check: edited` (read-aloud pass; grammar, voice, guardrails).
- `tools/lint_claims.py`: **PASS** (45 articles, YAML including `voice_check`, educational note, banned phrases, word floors, README slugs, claims box).
- Portrait / figure embed instructions and `PORTRAIT_SOURCES.md` references **unchanged** in substance; no new images added.

## What the editor did

### Voice and AI habits

- Full-series scan for STYLE_GUIDE hard bans (delve, landscape-as-field, Moreover stacks, gold-standard treatment, etc.): **no violations** in body copy before edit; none introduced.
- Preserved deliberate anti-protocol lines (worksheet refusals, “try at home” bans, crisis one-liners) as historical guardrails, not instructions.
- Essay 40 (*How to Read a “Mindfulness Works” Headline*) keeps headline-literacy kits; still not session scripts.

### Structure and repetition

- Automated paragraph similarity **≥0.72** across adjacent blocks: **none** before or after edit.
- Writer drafts had **internal production cross-links** (“draft 23,” “Stage 6 will…”) that would read like git metadata on import. Editor replaced them with **essay numbers and titles** (or stage names with essay ranges) in **17** files.

| Article | Editor action |
| --- | --- |
| `07-american-zendo-after-1950` | Stage 6 forward-reference → essays 33–39 |
| `14-rule-governed-behavior-1980s` | *dryer* → *drier*; Stage 6 → essay 38 title |
| `19-the-1999-guilford-volume` | Draft 23 → essay 23 title |
| `21-kelly-wilson-and-the-values-sentence` | Stage 6 → essay 38 title |
| `25-kabat-zinn-1979` | draft 05 → essay 05 title |
| `26-full-catastrophe-living-1990` | draft 06 → essay 06 title |
| `30-marlatt-and-mbrp` | drafts 25–29 → essays 25–29 |
| `33-hayes-2004-wave-essay` | Draft 03 → essay 03 title |
| `35-hofmann-and-the-family-quarrel` | Draft 12 → essay 12 (body + Sources) |
| `36-guidelines-as-historical-objects` | “This draft’s last verification” → essay wording; sister `CLAIMS_GUARDRAILS.md` path |
| `38-when-acceptance-sounds-like-a-muzzle` | Draft 21 → essay 21 (body + Sources) |
| `39-apps-yogurt-corporate-retreats` | draft 37 → essay 37 title |
| `40-how-to-read-a-mindfulness-works-headline` | Draft 02 / Drafts 05–06 → essay refs; Sources normalized |
| `41-living-people-public-documents` | “every draft’s mouth” → pack essays; sister path |
| `42-what-a-small-city-clinic-inherited` | Removed COSMOS / 15-second clock repo jargon; “these drafts” → essays; Sources |
| `43-what-we-opened` | Editor-branch / repository canon → public honesty wording; thin-trail header; `voice_check` stamp note |
| `45-portraits-we-will-not-fake` | draft / last draft / forty-five drafts → essay language; Sources |
| `03-third-wave-is-a-nickname` | “later drafts” → “later essays” |

Other articles were read on the read-aloud pass; no substantive rewrites required.

### Claims / DIY

- No new treatment protocols, worksheets, or self-administer content added.
- Existing refusals (body scans, values sorts, hexaflex as graphic, guideline-as-enrollment, etc.) **kept**.
- Educational note + Claims box + “not medical advice” / “not a treatment plan” **unchanged in requirement**; linter still enforces.

### Copy-editing

- Light grammar and cohesion in merged or retargeted cross-links only.
- `[VERIFY]` / `[CITE NEEDED]` markers **not added or removed**; writer hedges on NICE dates, Öst coding, hexaflex first print, etc. **unchanged**.

## Pack tooling

- `tools/lint_claims.py`: requires `voice_check: edited` or `human`; `MANIFEST.toml` regenerated via `--write-manifest`.
- `README.md`: documents editor stamp on all forty-five essays.

## QA command

```bash
python3 content/act-mindfulness-therapy-history/tools/lint_claims.py --write-manifest
```

## Handoff

Merge editor branch **onto** writer branch **#412** after review. Import per `WP_IMPORT.md` to **staging** only when Keith approves. **Draft PR; do not merge** without human sign-off.
