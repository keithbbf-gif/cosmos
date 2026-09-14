# Editor report — FigRoots pests & diseases pack

**Editor pass:** 2026-09-14  
**Writer PR:** https://github.com/keithbbf-gif/cosmos/pull/302 (`cursor/fig-pests-diseases-blog-b218`)  
**Editor branch:** `cursor/fig-pests-diseases-editor-0659` (stacked on writer branch)  
**Scope:** `content/fig-pests-diseases-blog/drafts/*.md` (45 essays)

## Summary

| Check | Result |
| --- | --- |
| Drafts edited | **45 / 45** |
| `voice_check` | **`edited`** on every draft |
| Zone | **`zone: 8a`** present on all drafts |
| STYLE_GUIDE ban list (bodies) | **0 hits** |
| Internal duplicate sections (Jaccard ≥ 0.52) | **0 pairs** |
| Body word count | **61,499** total; each draft **1,161–1,581** (target 1,100–1,600) |
| `CLAIMS_GUARDRAILS.md` | **Not modified** (guardrails preserved) |
| `BIBLIOGRAPHY.md` | **Not modified** |

## Editorial method

1. **Voice** — Kept PapaFig / South Arkansas 8a yard tone per `STYLE_GUIDE.md`. First-person moves, named extension sources, refusal language for fake cures.
2. **Guardrails** — Read-through for eradicate/cure theater. *Eradicate*, *cure*, and *virus-free* appear only in refusals, clinic contrast, or `CLAIMS_GUARDRAILS`-aligned negation — not as promises.
3. **Grammar** — Light hand fixes where caught (see below). No pillar rewrites, no new claims, no spray recipes.
4. **Front matter** — `voice_check: human` → `voice_check: edited` on all 45 drafts. Titles, slugs, pillars, `images:` / `D:\FIGS` paths unchanged.
5. **Dedup** — Automated section overlap scan; no stacked tail sections like the history pack stutter pattern.

## Hand fixes (prose)

| File | Change |
| --- | --- |
| `38-photograph-for-the-county.md` | Clinic note list: clarified spray-history line (parallel with other “say it on the form” bullets). |
| `25-birds-write-the-harvest-calendar.md` | “legal and a decent-person line” → “crosses a legal line and a decent-person line.” |

## Intentionally not changed

- `CLAIMS_GUARDRAILS.md`, `BIBLIOGRAPHY.md`, `PHOTO_NOTES.md`, `WP_IMPORT.md` (except inventory pointers in `INDEX.md` / `MANIFEST.md`)
- `STYLE_GUIDE.md` still documents `voice_check: human` for **writer** staging; this pass uses `edited` per assignment.
- Repeated “I will not …” closers across the pack are thematic guardrail refrains, not within-file stutter.

## Validation (run locally)

```bash
python3 content/fig-pests-diseases-blog/scripts/validate_editor_pass.py
```

## Follow-ups for a later pass

- `WP_IMPORT.md`: add `edited` to the `voice_check` rule when writer + editor stack merges.
- Human read on longest rust/copper pieces if any feel repetitive across *articles* (not within one file).
- Publisher: `[VERIFY]` tags and photo drops per `PHOTO_NOTES.md` before any live publish.

## Sign-off

Editor pass complete: grammar touch-ups where caught, guardrails intact, zone 8a default held, `voice_check: edited` set on all 45 drafts.
