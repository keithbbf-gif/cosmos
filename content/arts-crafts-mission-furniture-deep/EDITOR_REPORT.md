---
title: Editor report
series: American Arts and Crafts / Mission Furniture
status: staged
voice_check: edited
lane: bbf-furniture
editor: Cursor Cloud Agent (Composer 2.5)
editor_pass: 2026-09-14
pr: 335
---

# Editor report — Arts & Crafts / Mission deep series

Magazine-voice QA on the staged pack in `content/arts-crafts-mission-furniture-deep/`. **Draft only.** No publish, no merge, no live-tree or CMS import.

## Scope

| Item | Count |
| --- | ---: |
| Staged essays (`drafts/*.md`) | 44 |
| Series apparatus (INDEX, STYLE_GUIDE, PHOTO_CAPTIONS, etc.) | 10 |
| Validator | `validate_staging.py` |

Baseline before this pass: builder quality commit `39d07dc` — validator **PASS**, 44 essays in **1800–2600** body words, 4–7 figures each.

## Method

1. Re-ran `python3 content/arts-crafts-mission-furniture-deep/validate_staging.py` (word counts, YAML, figures, banned phrases, brand rules).
2. Scanned all drafts for style-guide violations (AI filler, stacked transitions, fake omniscience, product language in ch. 1–43).
3. Line edit for grammar and magazine cadence without flattening voice into brochure English.
4. Set `voice_check: edited` on every markdown file in this folder.
5. Left all `[VERIFY]` and `[CITE NEEDED]` flags in place (172 / 4 instances across drafts) — intentional honesty, not errors to strip.

## Voice judgment

The pack already reads as *Antiques* / *American Bungalow* adjacent: artifact-first openings, dated shops and catalog numbers, doubt where the trade myth runs ahead of the paper. This pass **did not** rewrite for SEO, **did not** add living-brand CTAs outside chapter 44’s allowed historical mention, and **did not** remove the grain of long sentences where the argument needs them.

Banned-phrase scan: **clean** (validator regex + manual read for Moreover/Furthermore, “scholars agree,” throat-clearing closings).

## Copy changes (body)

| File | Change |
| --- | --- |
| `05-wilde-on-the-platform.md` | Removed duplicated word: “making making” → “making”. |
| `37-settles-leather-hall.md` | Fixed verb agreement: “also drop-arms” → “drops its arms too”. |
| `44-hardwood-towns-still-speak.md` | Article: “a applied end” → “an applied end”. |

No other body edits were required for grammar or banned phrasing on this pass. Eastlake’s “had had nothing” in ch. 03 is correct past perfect, not a stutter.

## Metadata and tooling

- **`voice_check: edited`** on all series markdown (essays + apparatus).
- **`validate_staging.py`**: accepts `voice_check: human` (pre-editor) or `voice_check: edited` (post-editor).
- **`STYLE_GUIDE.md`**: editor-pass contract documented.
- **`WP_IMPORT.md`**: custom field and checklist updated for `voice_check=edited`.

Post-pass validator: **PASS** (2026-09-14).

## Keith / photo pass — still open

- Confirm CC0 or licensed heroes from `PHOTO_CAPTIONS.md` before WP upload.
- Resolve or accept `[VERIFY]` / `[CITE NEEDED]` where you want hard citations (especially auction hammers, payroll names, and comparative prices).
- Keep `status: staged` until you clear publish.

## Sign-off

| Check | Result |
| --- | --- |
| Magazine voice preserved | Yes |
| `voice_check: edited` | Yes |
| Validator PASS | Yes |
| Product language ch. 1–43 | None found |
| Bradley / living maker | Ch. 44 only, historical frame |
| Ready for Keith read | Yes — draft PR, no merge |
