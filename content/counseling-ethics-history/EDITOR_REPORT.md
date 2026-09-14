# Editor report — counseling ethics-code history pack

**Role:** EDITOR (magazine-floor pass)  
**Writer branch:** `cursor/counseling-ethics-history-fb43` (PR #517)  
**Editor branch:** `cursor/counseling-ethics-history-editor-3cda`  
**Scope:** `content/counseling-ethics-history/` — 48 articles + pack QA  
**Staging only:** no live wowtherapies.com changes  
**Date:** 2026-09-14  

## Stamp

- All **48** articles: `voice_check: edited` (read-aloud pass; grammar, spelling, human voice).
- `lint_claims.py`: **PASS** (48 drafts, YAML, educational note, banned phrases, DIY leaks, word floors, README slugs).
- **`[VERIFY]`** and **`[CITE NEEDED]`** markers: **kept** (not flattened into false certainty).
- Portraits: drafts remain `portrait: none` or type-only per `PHOTO_NOTES.md` / `PORTRAIT_SOURCES.md` — **no AI faces**.

## Posture

Educational history of APA / ACA / NASW ethics **documents** only. Not legal advice, not clinical advice, not complaint how-tos. Claims boxes and `GUARDRAILS.md` refuse lists unchanged in intent.

## What the editor did

### Voice and STYLE_GUIDE scan

- Full-series grep for hard bans (`delve`, `landscape`, `Moreover` stacks, `gold-standard treatment`, worksheet voice, etc.): **no violations** in body copy before or after pass.
- Preserved deliberate refusals (no decision trees, no complaint walkthroughs, no code paste).

### Line edits (body)

| Article | Editor action |
| --- | --- |
| `01-what-this-folder-refuses` | *an adopted*; tightened *ethics* / *they* coordination |
| `03-three-professions-three-codes` | Explicit subject under historian subhead |
| `04-public-text-is-not-a-trial` | *cite* a code (not *wave*) in deposition |
| `06-oaths-older-than-associations` | Kos / Hippocratic oath gloss (was bare *Cos*) |
| `17-2002-fisher-june-2003` | *the law*; *nickname problem* hyphenation |
| `18-pens-2005-and-2010-amendments` | *the law* in 1.02 paraphrase |
| `27-2014-values-screens-five-years` | Varied year-count opener (de-collide with 37) |
| `37-multiple-relationships-and-year-counts` | New opener; *grocery-aisle encounter* |
| `39-informed-consent-as-a-late-object` | *superbill* grammar |
| `42-who-adjudicates-association-board-court` | *cite* / *citing* (not *wave*) |
| `44-living-people-public-documents` | QA flag notes `edited` stamp |
| `45-what-a-small-city-clinic-inherited` | *grocery-aisle encounter* |

Remaining 36 essays: read in full across stages; no additional surgery above editorial threshold (no duplicate-paragraph padding, no bot-smell hits).

### Pack ops

- `README.md`: editor stamp + pointer to this report.
- `tools/lint_claims.py`: accepts `voice_check: edited` after editor pass.
- `MANIFEST.toml`: regenerated from frontmatter.

## QA command

```bash
python3 content/counseling-ethics-history/tools/lint_claims.py
python3 content/counseling-ethics-history/tools/lint_claims.py --write-manifest
```

## Handoff

Merge editor branch **onto** writer branch #517 after review. Import per `WP_IMPORT.md` to **staging** only when Keith approves. **Do not merge to `main` without claims + portrait review.** Draft PR only — no merge from this lane.
