# Editor report — Supplement Facts / DSHEA label-literacy pack

**Branch:** `cursor/supplement-facts-label-literacy-editor-2adb` (stacked on writer PR **#427** / `cursor/supplement-facts-label-literacy-bf57`)  
**Editor pass date:** 2026-09-14  
**Base commit:** `e7109cf` — `feat: staged Supplement Facts / DSHEA label-literacy pack`

## Scope

- **44/44** drafts under `articles/`
- **YAML:** `voice_check: edited` on every file (`status: draft` unchanged)
- **DSHEA fence:** disclaimer block present on all 44 (educational; not medical advice; not intended to diagnose/treat/cure/prevent disease; not legal advice; not a labeling-opinion for a specific SKU)
- **Citations:** no new PMIDs, warning-letter IDs, CFR cites, or trial numbers added; existing `[VERIFY]` / `[CITE NEEDED]` flags kept
- **Style guide:** `check_pack.py` grep pass on hard bans — **0 hits** in article bodies
- **Brand grep:** `ElitElixir` / `Unilever` in `articles/` — **0 hits**

## Automated QA (editor run)

| Check | Result |
| --- | --- |
| Article count | 44 (≥ 40) |
| `voice_check: edited` | 44/44 |
| DSHEA "not intended to diagnose" | 44/44 |
| Style bans (`STYLE_GUIDE.md`) | 0 failures |
| Word band (script) | 1,331–1,699 per piece |
| `check_pack.py` exit | 0 |

## Edit themes (pack-wide)

1. **Voice:** operator / careful-buyer tone per `STYLE_GUIDE.md`; kept disease names inside FDA/FTC *forbidden-example* fences; no new efficacy or treatment advice.
2. **DSHEA fence:** opening disclaimer unchanged in substance; piece 21 duty header renamed **Disclaimer box.** so it is not confused with the statutory disclaimer block.
3. **Cross-refs:** `Piece NN` pointers checked for tense (piece 29 → piece 41 present tense); print-lock wording in piece 42 aligned with eight-surface packet list.
4. **Grammar / clarity:** piece 32 antecedent (`This piece will not tell…`); no style-ban cousins introduced.

## Per-article notes (high signal)

| # | Slug file | Notable editor action |
| --- | --- | --- |
| 21 | `21-structure-function-343-r-6.md` | Renamed three-duties **Disclaimer.** H3 to **Disclaimer box.** |
| 29 | `29-testimonials-stars-before-after.md` | `Piece 41 treats` (was future tense) |
| 32 | `32-weight-metabolism-cleanse-detox.md` | Clarified subject on no-treatment-advice sentence |
| 42 | `42-label-vs-formula-vs-website.md` | Print-lock sign-off: `every claim-bearing surface` (was `five`) |

Pieces **01–20, 22–28, 30–31, 33–41, 43–44** received `voice_check: edited` plus a full read-through against `STYLE_GUIDE.md`, `CLAIMS_GUARDRAILS.md`, and `_editorial/ARTICLE_SPECS.md`; no material copy changes beyond the flag where prose already met the gates.

## Ops files updated

- `check_pack.py` — requires `voice_check: edited`
- `MANIFEST.md` — inventory + check script steps
- `STYLE_GUIDE.md` — documents `voice_check: edited`
- `WP_IMPORT.md` — staging field mapping
- `EDITOR_REPORT.md` — this file

## Remaining for human QA / counsel

- Resolve `[VERIFY]` before publish (101.9 RDI tables, FDA/FTC/OEHHA/USP live pages, Amazon category style, Cohen *JAMA* summary figures in piece 40, Prop 65 averaging with counsel in piece 38).
- No publish: `status: draft` retained; import per `WP_IMPORT.md` staging only.
- Science/QA partner review on stacked PR **#427** after this editor branch merges or rebases.

## Sign-off

Editor agent: **pass** for voice, grammar, DSHEA fence on every piece, label/claim literacy, and automated gates. Ready for science/QA review on draft PR (editor branch → #427).
