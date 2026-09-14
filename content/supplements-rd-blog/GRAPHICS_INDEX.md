# Graphics index — supplements R&D blog pack

Staged editorial figures only. **SVG** under `assets/<slug>/`. Each draft embeds captioned figures after the relevant H2 (marker `<!-- graphics-pack:v1 -->`).

Regenerate assets: `python3 scripts/generate_graphics.py`  
Re-embed markdown: `python3 scripts/embed_graphics.py`

## Policy (matches `PHOTO_NOTES.md` + `CLAIMS_GUARDRAILS.md`)

- No disease-cure marketing art, fake lab photos, or before/after bodies.
- No fabricated clinical effect sizes on charts — cited trial headlines and regulatory dates only, otherwise labeled **illustrative** or **qualitative** in caption and SVG footnote.
- USP / NSF / Informed-Sport references are literacy only; trademark rules apply at publish.

## Coverage

| # | Slug | Article file | SVG count | Primary figure types |
| --- | --- | --- | ---: | --- |
| 01 | `six-years-rewired-supplement-rd` | `articles/01-six-years-that-rewired-supplement-rd.md` | 2 | Regulatory timeline 2020–2026; CBD/NAC/NMN threads |
| 02 | `covid-demand-adulteration-scrutiny` | `articles/02-covid-demand-and-adulteration.md` | 2 | Demand vs oversight; adulteration QA loop |
| 03 | `immune-support-held-vs-hype` | `articles/03-immune-support-what-held.md` | 2 | Qualitative evidence burden; letter roster table |
| 04 | `vitamin-d-zinc-omega-3-2020-2026` | `articles/04-vitamin-d-zinc-omega3.md` | 2 | VITAL factorial schematic; trial headline table |
| 05 | `probiotics-strain-specificity` | `articles/05-probiotics-strain-specificity.md` | 1 | Strain vs species label compare |
| 06 | `protein-creatine-sports-nutrition` | `articles/06-protein-creatine-sports.md` | 2 | Morton anchor table; sports QA stack |
| 07 | `ashwagandha-adaptogen-rcts-quality` | `articles/07-adaptogens-ashwagandha.md` | 2 | RCT checklist; withanolide method note |
| 08 | `nad-nmn-longevity-evidence` | `articles/08-nad-nmn-longevity.md` | 2 | NAD salvage schematic; NMN regulatory dates |
| 09 | `bioavailability-liposomal-chelates-magnesium` | `articles/09-bioavailability-forms.md` | 2 | Magnesium forms table; delivery claim questions |
| 10 | `heavy-metals-usp-nsf-informed-sport` | `articles/10-testing-usp-nsf-informed-sport.md` | 2 | Program compare; finished-product COA rows |
| 11 | `supply-chain-api-shocks-2020-2022` | `articles/11-supply-chain-shocks.md` | 2 | Shock timeline; dual-source schematic |
| 12 | `fda-ftc-structure-function-enforcement` | `articles/12-fda-ftc-claims.md` | 2 | Structure/function vs disease; dual-agency flow |
| 13 | `personalized-nutrition-at-home-tests` | `articles/13-personalized-nutrition.md` | 2 | Quiz-to-claim gap; evidence match table |
| 14 | `cbd-hemp-regulatory-lessons` | `articles/14-cbd-hemp-regulatory.md` | 1 | CBD regulatory timeline |
| 15 | `womens-health-menopause-nutraceuticals` | `articles/15-womens-health-menopause.md` | 1 | NAMS-aligned qualitative map |
| 16 | `white-label-coa-literacy` | `articles/16-white-label-coa-literacy.md` | 2 | Ingredient vs finished COA; COA read stack |

**Totals:** 16 drafts illustrated · **29** SVG files · calendar target remains **≥40 drafts** for the full blog program — add rows here when CONTENT lands drafts 17+.

## File manifest (by slug)

### `six-years-rewired-supplement-rd`

- `timeline.svg` — Public milestones 2020–2026 (dated in art).
- `ingredient-regulatory-threads.svg` — CBD, NAC, NMN operator summary.

### `covid-demand-adulteration-scrutiny`

- `demand-vs-oversight.svg`
- `adulteration-response-loop.svg`

### `immune-support-held-vs-hype`

- `immune-claims-evidence-burden.svg` — Qualitative tiers only.
- `letter-ingredients.svg`

### `vitamin-d-zinc-omega-3-2020-2026`

- `vital-factorial-schematic.svg` — Illustrative 2×2 layout.
- `large-trial-headlines.svg` — Primary endpoint headlines as reported.

### `probiotics-strain-specificity`

- `label-strain-vs-species.svg`

### `protein-creatine-sports-nutrition`

- `protein-dose-literacy.svg` — Morton 2018 ~1.62 g/kg citation.
- `sports-sku-qa-stack.svg`

### `ashwagandha-adaptogen-rcts-quality`

- `adaptogen-rct-checklist.svg`
- `withanolide-method-note.svg`

### `nad-nmn-longevity-evidence`

- `nad-salvage-pathway.svg`
- `nmn-regulatory-dates.svg`

### `bioavailability-liposomal-chelates-magnesium`

- `magnesium-forms.svg` — No ranked absorption percentages.
- `delivery-claim-questions.svg`

### `heavy-metals-usp-nsf-informed-sport`

- `program-compare.svg`
- `coa-rows-finished-product.svg`

### `supply-chain-api-shocks-2020-2022`

- `timeline.svg`
- `dual-source-decision.svg`

### `fda-ftc-structure-function-enforcement`

- `structure-function-vs-disease.svg`
- `dual-agency-review.svg`

### `personalized-nutrition-at-home-tests`

- `quiz-to-claim-gap.svg`
- `evidence-match.svg`

### `cbd-hemp-regulatory-lessons`

- `timeline.svg`

### `womens-health-menopause-nutraceuticals`

- `nams-evidence-map.svg`

### `white-label-coa-literacy`

- `ingredient-vs-finished-coa.svg`
- `coa-read-stack.svg`

## WordPress / import

Figures use relative paths from `articles/` (`../assets/...`). `WP_IMPORT.md` should copy `assets/` beside uploads or rewrite to theme CDN URLs on import.
