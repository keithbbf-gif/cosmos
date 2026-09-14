# Editor report — Fig soil, drainage, mulch, irrigation, container media

**Editor pass:** 2026-09-14  
**Branch:** `cursor/fig-soil-irrigation-editor-2f61` (stacked on `cursor/fig-soil-irrigation-drafts-87f0`, writer PR #366)  
**Scope:** `content/fig-soil-irrigation/drafts/*.md` (48 essays)

## Summary

| Check | Result |
| --- | --- |
| Drafts edited | 48 / 48 |
| `voice_check` | `edited` on every draft |
| `validate.py` slop list | 0 hits in bodies |
| Stacked tail / duplicate sentences | Trimmed in 8 drafts (see below) |
| `_manifest.toml` | `voice_check = "edited"` at set level |
| Net prose change | ~150 lines touched; ~242 lines removed of repeat tails; replacements keep word floor |

## What was wrong

Several drafts carried **second closers** from iterative expansion: the same zone beat, habit list, or diagnostic order restated under a new paragraph. That reads like model summary, not PapaFig yard prose. A few pieces also repeated whole sentences (rust ring, FigRoots library count, moisture-control bag rule, perlite rock sermon).

The writer pack was already on-voice (8a, first person, source-named). This pass was **dedup + desk hygiene**, not a rewrite of the soil/water doctrine.

## Editorial method

1. **Voice** — Kept PapaFig: concrete hole/hose/can talk, FigRoots citations where already present, no new trials or recipes.
2. **Dedup** — Removed later paragraphs that repeated an earlier sentence or beat; kept the stronger first pass and any unique `[VERIFY]` hooks.
3. **Front matter** — Added `voice_check: edited` under `voice: human` on all 48 drafts.
4. **Gate** — `validate.py` now requires `voice_check: edited`; `STAGE.md` documents writer vs editor staging.

## Drafts with substantive tail edits

| File | Change |
| --- | --- |
| `d27-rust-leaves-are-not-a-gift.md` | Merged duplicate ring / raking closers; cross-link to overhead draft |
| `d33-split-after-the-drought-then-storm.md` | Dropped repeated “make up a drink” / pick-before-front block |
| `d34-overhead-water-and-rust.md` | Single “honest count / FigRoots library” close |
| `d37-cut-water-to-ripen-the-california-argument.md` | Removed restated California / forum paragraph; added berm vs #3 tank beat |
| `d40-yellow-leaves-wet-dry-or-occupied.md` | One diagnostic order; salt / knuckle lines kept once |
| `d44-moisture-control-mix-is-a-drowning-kit.md` | Removed triple restate of gel / petunia rule; kept rescue paragraph |
| `d46-perlite-you-can-see.md` | One rocks/castings close; media ingredient list once |
| `d48-saucers-collapse-and-pots-that-water-themselves.md` | Single three-habits outro for the pack |

## Intentionally not changed

- `README.md` source list and staging table
- Draft filenames (including `d14-…-tamus-…` slug)
- Required anchors: puddle test (`d06`), bathtub hole (`d13`), Promix / field capacity (`d43`)
- No publish / SEO / WordPress steps

## Validation

```bash
python3 content/fig-soil-irrigation/validate.py
```

## Handoff

- Files remain **`status: staged`** until Keith schedules.
- Art / graphics: no image slots in this pack.
- Publisher: accept `voice_check: edited` when importing this stack after writer PR #366.

## Sign-off

Editor pass complete: PapaFig voice preserved, AI stutter tails removed, `voice_check: edited` set, structural gate passes.
