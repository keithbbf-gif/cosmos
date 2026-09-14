# Editor report — Arkansas / Southern furniture woods

**Editor pass:** 2026-09-14  
**Writer PR:** https://github.com/keithbbf-gif/cosmos/pull/364 (`cursor/arkansas-southern-woods-species-a01a`)  
**Editor branch:** `cursor/arkansas-southern-woods-editor-50c1` (stacked on writer PR #364)  
**Scope:** `content/arkansas-southern-woods-species/[01-46]-*.md` (46 essays + `README.md` inventory)

## Summary

| Check | Result |
| --- | --- |
| Drafts edited | **46 / 46** |
| `voice_check` | **`edited`** on every numbered draft |
| Verse-wrap reflow | **46 / 46** — late-pack narrow line breaks joined to paragraph prose |
| STYLE_GUIDE ban list (bodies) | **0 hits** after pass (`leverage`, metaphorical `landscape` rephrased) |
| Internal duplicate sections (Jaccard ≥ 0.52) | **0 pairs** |
| Body word count | **24,876** total; each draft **450–963** (median **518**) |
| `README.md` | Inventory note updated for `voice_check`; species table unchanged |

## Editorial method

1. **Voice** — Kept shop-and-place tone per series `README.md` (properties, towns, mills, refusal of catalog vagueness). First-person shop observations preserved; no takeaway stacks or moral closes added.
2. **Reflow** — Drafts **26–46** (and uneven wraps in **10–25**) arrived as hard line-broken prose; paragraphs were joined with hyphen-aware glue so compounds (`high-angle`, `early-twentieth-century`) stay intact.
3. **Grammar** — Light hand: list repair in `45-moisture-and-why-southern-furniture-fails.md`, italic species spacing in `14-loblolly-versus-shortleaf-on-the-bench.md`, `What we mill now` in `12-reading-growth-rings-on-arkansas-oak.md`, town name `Warren-Crossett-Fordyce` in `43-fort-smith-was-a-furniture-town.md`.
4. **Front matter** — Added `voice_check: edited` on all 46 drafts. Titles, slugs, species/latin/region fields unchanged.
5. **Ban list** — `landscape property` → `place property` (`01`); `landscape of unnamed` → `among unnamed` (`20`); `full of leverage` → `full of racking stress` (`26`). Grain-figure “landscape” in `34-figured-walnut-crotch-burl-stump.md` kept (literal, not filler).

## Hand fixes (prose)

| File | Change |
| --- | --- |
| `12-reading-growth-rings-on-arkansas-oak.md` | `nineteenthcentury` → `nineteenth-century`; `What we saw now` → `What we mill now`. |
| `23-bald-cypress-delta-and-cache.md` | `decayresistant` → `decay-resistant`. |
| `25-old-growth-versus-second-growth-cypress.md` | `secondgrowth` → `second-growth`. |
| `30-the-1912-cypress-exhaustion-warning.md` | `threequarters` → `three-quarters`. |
| `41-wild-cherry-log-size-and-furniture-grade.md` | `Furnituregrade` → `Furniture-grade`. |
| `44-nineteen-twelve-red-gum-and-white-oak.md` | `ninetyfive` → `ninety-five`. |
| `45-moisture-and-why-southern-furniture-fails.md` | Restored bullet and numbered lists collapsed by reflow; `ovendry` → `oven-dry`. |
| `46-what-arkansas-oak-meant-in-the-catalog.md` | `earlytwentieth` → `early-twentieth`. |

## Intentionally not changed

- Species facts, Janka/shrinkage table in `README.md`, and source list (no new citations invented).
- Sweetgum sidebar essay `44` remains outside the “five woods” title list by writer design.
- Word-count band is **shorter** than the fig-pests pack; editor did not pad essays to an arbitrary ceiling.

## Validation (run locally)

```bash
python3 content/arkansas-southern-woods-species/scripts/validate_editor_pass.py
```

## Follow-ups for a later pass

- Human read on longest oak pieces (`01`, `28`, `30`) for any cross-essay repetition at publish time.
- Publisher: confirm frontmatter schema for WordPress import if `voice_check` becomes a gate field.
- Optional: add `STYLE_GUIDE.md` beside `README.md` if this series gets a second writer wave.

## Sign-off

Editor pass complete: paragraph reflow, grammar touch-ups where caught, ban-list clean, `voice_check: edited` set on all 46 drafts.
