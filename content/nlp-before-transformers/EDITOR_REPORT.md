# Editor report — NLP before transformers

**PR:** [#337](https://github.com/keithbbf-gif/cosmos/pull/337)  
**Scope:** `content/nlp-before-transformers/` (51 essays + house files)  
**Pass:** novelty-safe voice edit (`voice_check: edited`)  
**Date:** 2026-09-14  

## What this pass did

1. **Voice check flag** — Added `voice_check: edited` to all 51 essay frontmatter blocks. Documented the field in `README.md`.
2. **House wrap** — Reflowed 11 essays whose hard wraps were far narrower than the series norm (~67 characters per line, matching essay 01). Fixed a reflow artifact on closing `---` delimiters and on hyphenated terms (`pointer-generator`, `encoder-decoder`) in the closing essay.
3. **Factual tightening** — Essay **01** (Shannon): separated what belongs to the 1948 channel paper from the **1951** human guessing-game note; trimmed duplicate exposition.
4. **Word choice** — Essay **44** (Moses → NMT): replaced nonstandard *intervenability* with plain *a phrase table you could grep* (same point, less jargon).
5. **Opening hook** — Essay **28** (LSA): one lead sentence before the bibliographic opener so the voice matches the stronger essays in stages 01–07.

## What this pass did not do

- Did not change `publish: false`, `status: staged`, or `novelty: public-record`.
- Did not add transformer-era material beyond what essay **51** already names as context.
- Did not merge or split essays; `MANIFEST.md` ids and counts unchanged.

## Automated checks (post-pass)

| Check | Result |
|---|---|
| Essay count | 51 |
| `voice_check: edited` on every essay | yes |
| `publish: false` on every essay | yes |
| Word count per essay | 403–597 (unchanged band) |
| Slop / leakage scan (COSMOS, cDeck, MOTIF, USPTO, template phrases) | clean |
| Novelty fence (`NOVELTY.md`) | no violations found |

## Manual read notes

- Series voice is consistent: first-person craft history, skeptical of demos, respectful of engineering that shipped.
- Recurring closers (*If you only remember one thing…*) remain in several essays; they read as intentional series rhythm, not AI filler.
- Citation-first openings on **45** (BLEU) and **49** (LDA) are appropriate for evaluation/topic-model essays.

## Residual risks (low)

- Dates and attributions were not re-litigated paper-by-paper; only the Shannon 1948/1951 split was corrected on high-confidence grounds.
- These drafts are still **not** a novelty opinion or legal review — see `NOVELTY.md`.

## Files touched

- All `stage-*/*.md` essays (51): `voice_check` + reflow where needed.
- `01-shannon-1948-language-as-a-channel.md`, `28-lsa-when-svd-looked-like-meaning.md`, `44-from-moses-to-neural-mt.md`: substantive line edits above.
- `README.md`: frontmatter docs for `voice_check`.
- `EDITOR_REPORT.md`: this file.
