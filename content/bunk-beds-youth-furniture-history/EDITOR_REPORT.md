---
series: bunk-beds-youth-furniture-history
stage: 0-frame
draft: editor-report
voice: BBF
status: draft
audience: educational
not: legal-advice
voice_check: edited
---

# Editor report — Bunk beds and youth furniture history

**Editor pass:** 2026-09-14  
**Branch:** `cursor/bunk-beds-youth-furniture-history-1350` (stacked on `cursor/bunk-beds-youth-furniture-history-2493`, PR #382)  
**Scope:** `content/bunk-beds-youth-furniture-history/` (46 numbered essays + README, SOURCES, MANIFEST)

## Summary

| Check | Result |
| --- | --- |
| Essays edited | 46 / 46 (light pass; no stacked-tail dedup needed) |
| Frame files | README, SOURCES, MANIFEST — `voice_check: edited` |
| `voice_check` | `edited` on every `.md` in the folder |
| Banned AI habit words (fig-pack list) | 0 hits in essay bodies |
| Educational / not legal advice | Present in front matter on all pieces |
| `SOURCES.md` locked facts | **Not modified** (numbers unchanged) |
| Net prose change | Small grammar/clarity fixes; front matter only elsewhere |

## What was wrong

This staging set did **not** show the fig-pack failure mode (repeated tail sections under new `##` headings). The main issues were **metadata** (no `voice_check` yet) and two **grammar** slips in otherwise strong BBF voice.

## Editorial method

1. **Voice** — Kept Keith BBF concrete, citation-named tone. No new death counts, SKUs, or standard clauses behind paywalls.
2. **Legal-education boundary** — Left existing disclaimers (`not: legal-advice`, draft 45, README). Editor did not add prescriptive "you must comply" language beyond what the series already uses as teaching examples.
3. **Prose fixes**
   - `01-why-this-series-exists.md` — "the entrapment dead" → "children who died from entrapment" (clearer, less sensational).
   - `45-what-this-series-is-not.md` — "A honest" → "An honest".
4. **Front matter** — Added `voice_check: edited` after `not: legal-advice` on all 49 markdown files.

## Intentionally not changed

- Federal Register table in draft 19 and locked dates in `SOURCES.md`
- Cross-draft pointers (`draft N` shorthand)
- COSMOS / one-writer references in draft 45 (series voice, not product doctrine)

## Validation (run locally)

```bash
python3 content/bunk-beds-youth-furniture-history/scripts/validate_editor_pass.py
```

## Follow-ups for a later pass

- Spot-read practice drafts (39–44) against a live eCFR snapshot if a standard revision lands after 2026-09-14.
- Word-count gate (if desired): essays are mid-length magazine pieces; no flagship under 400 words after this pass.
- If an importer checklist exists elsewhere in the tree, add `edited` beside `human` for `voice_check` when this report is present.

## Sign-off

Editor pass complete: AI stutter scan clean, educational-not-legal-advice framing preserved, `voice_check: edited` set, validation script added.
