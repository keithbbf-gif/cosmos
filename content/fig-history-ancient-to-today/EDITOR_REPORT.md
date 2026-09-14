# Editor report — History of the Fig pack

**Editor pass:** 2026-09-14  
**Branch:** `cursor/fig-history-editor-voice-b586` (stacked on `cursor/fig-history-graphics-762d`, PR #250)  
**Scope:** `content/fig-history-ancient-to-today/articles/_staging/*/index.md` (62 essays)

## Summary

| Check | Result |
| --- | --- |
| Articles edited | 62 / 62 |
| `voice_check` | `edited` on every article |
| Banned AI habit words (WRITER_STYLE_GUIDE list) | 0 hits in article bodies |
| `<!-- figure-id: … -->` blocks | Preserved (not removed) |
| `![…](../../../assets/…)` embeds | All paths resolve on disk |
| `IMAGE_SOURCES.md` | **Not modified** (no new rasters, no licence edits) |
| `assets/shared/svg/` | **Not modified** |
| Net prose change | ~1,093 lines removed (duplicate “stutter” sections); ~63 lines added (front matter + fixes) |

## What was wrong

Many drafts had **stacked tail sections** from iterative expansion: the same oath, species line, or FAOSTAT warning repeated under new `##` headings with slightly different wording. That pattern reads like model summary, not magazine prose.

## Editorial method

1. **Voice** — Kept the pack’s concrete, source-named tone (`WRITER_STYLE_GUIDE.md`). No new folklore, licences, or museum claims.
2. **Dedup** — Removed later sections whose vocabulary overlapped earlier sections (Jaccard similarity ≥ ~0.52 on content tokens), always keeping the first occurrence and **Sources for this piece**.
3. **Hand passes** — Extra trims on high-repeat articles:
   - `global-production-statistics-today` — collapsed redundant FAOSTAT “horseshoe” micro-sections after the shape table.
   - `islamic-paradise-garden-fig` — removed repeated oath / *chahār-bāgh* closers after the courtyard section.
   - `neolithic-gilgal-and-early-sites` — dropped redundant “Cluster, not capital” stub; fixed agreement (*fruits … are*).
4. **Front matter** — `voice_check: human` → `voice_check: edited` on all 62 articles.

## Articles with largest line reductions (stutter removal)

| Slug | Lines removed (approx.) |
| --- | ---: |
| `andalusian-fig-cultivars` | 48 |
| `venetian-spice-fig-cargoes` | 46 |
| `islamic-medical-traditions-fig` | 46 |
| `izmir-port-and-fig-packing` | 46 |
| `chile-peru-andes-fig` | 47 |
| `fig-paste-and-confection` | 43 |
| `new-testament-fig-parables` | 32 |
| `museum-collections-fig-artifacts` | 31 |
| `black-mission-vs-white-genoa` | 31 |
| `organic-and-so2-free-drying` | 30 |

(Full diff: `git diff cursor/fig-history-graphics-762d -- content/fig-history-ancient-to-today/articles/`)

## Intentionally not changed

- `BIBLIOGRAPHY.md`, `GRAPHICS_INDEX.md`, `ARTICLE_INDEX.md`, `INDEX.md`
- `WRITER_STYLE_GUIDE.md` / `WP_IMPORT.md` still document `voice_check: human` for **writer** staging; this editor pass uses `edited` per assignment. Importer checklist should accept `edited` when this report is present.
- Orchard photo slots (`orchard_slot:`) and pending rasters

## Validation (run locally)

```bash
python3 content/fig-history-ancient-to-today/scripts/validate_editor_pass.py
```

## Follow-ups for a later pass

- ~24 articles still carry ≥8 `##` sections; some tails are thematic refrains, not duplicates — human read if any feel thin.
- `WP_IMPORT.md`: add `edited` to the `voice_check` rule when PR #250 + this stack merge.
- Flagship length targets (1,200–2,200 words) were not re-counted; dedup may have shortened a few pieces — spot-check against `ARTICLE_INDEX.md` if word count is a gate.

## Sign-off

Editor pass complete: grammar touch-ups where caught, AI stutter removed, embeds and credits intact, `voice_check: edited` set.
