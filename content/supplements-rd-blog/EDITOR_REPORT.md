# Editor report — supplements R&D blog pack

**Branch:** `cursor/supplements-rd-blog-ee57` (PR #230)  
**Editor pass date:** 2026-09-14  
**Base:** post–≥1,000-word expansion (`35b8b1b`). **Not** PR #245.  
**Graphics:** PR #240 SVG embeds preserved (`<!-- graphics-pack:v1 -->` + `../assets/...` paths unchanged).

## Scope

- **40/40** drafts under `articles/`
- **YAML:** `voice_check: edited` on every file (`status: draft` unchanged)
- **DSHEA:** disclaimer block present on all 40 (educational; not medical advice; not intended to diagnose/treat/cure/prevent disease)
- **Citations:** no new PMIDs, DOIs, trial n, or effect sizes added; existing `[CITE NEEDED]` / `[VERIFY]` flags kept
- **Style guide:** grep pass on `STYLE_GUIDE.md` hard bans — **0 hits** in article bodies (ISAPP “selectively utilized” paraphrased in piece 29)

## Automated QA (editor run)

| Check | Result |
| --- | --- |
| Article count | 40 |
| Word count ≥ 1,000 | 40/40 (min **1,001** — `31-ftc-endorsements-2023.md`) |
| Duplicate `![...]` embeds | **0** (fixed on 03, 07, 13) |
| Missing asset SVG vs embed | **0** |
| `ElitElixir` / `Unilever` in articles | **0** |

## Figure hygiene (graphics #240)

Three drafts had **four duplicate copies** of Figure 2 (bad merge artifact). Removed extras; Figure 1 + Figure 2 retained:

| # | File | Fix |
| --- | --- | --- |
| 03 | `03-immune-support-what-held.md` | Deduped `letter-ingredients.svg` |
| 07 | `07-adaptogens-ashwagandha.md` | Deduped `withanolide-method-note.svg` |
| 13 | `13-personalized-nutrition.md` | Deduped `evidence-match.svg` |

Wave-1 slugs (01–16) keep **two** figures where the asset pack ships two SVGs; wave-2 slugs (17–40) keep **one** figure where only one SVG exists for that slug.

## Edit themes (all 40)

1. **Voice:** operator/clinician-curious tone per `STYLE_GUIDE.md`; trimmed recap paragraphs that repeated H2s; removed symmetrical filler.
2. **Grammar/spelling:** e.g. “underrepresented,” “strain specificity,” punctuation in lists and em-dash clauses.
3. **De-duplication:** merged near-duplicate sections in 15, 20–40 (especially regulatory runbooks, GOED/Prop 65/NDI teaching blocks) without cutting sourced facts.
4. **Cross-refs:** piece numbers (e.g. folate quiz → piece 25 + 13) left consistent; no new invented cross-links.

## Per-article notes (high signal)

| # | Slug file | Notable editor action |
| --- | --- | --- |
| 01 | `01-six-years-that-rewired-supplement-rd.md` | Intended-use examples tightened (Reels, Amazon bullets) |
| 02 | `02-covid-demand-and-adulteration.md` | Demand vs inspection wording |
| 03 | `03-immune-support-what-held.md` | Figure dedupe |
| 15 | `15-womens-health-menopause.md` | Trimmed repeated black cohosh / HPTLC block |
| 20 | `20-sleep-stacks-beyond-melatonin.md` | COA / child-resistant copy de-duped |
| 21 | `21-berberine-ozempic-copy.md` | Yin vs STEP contrast; April 2023 FTC notice dating |
| 25 | `25-folate-methylfolate-mthfr.md` | Merged repetitive prenatal / DTC sections |
| 29 | `29-prebiotics-fiber-psyllium.md` | ISAPP definition paraphrase (ban “utilize”) |
| 31 | `31-ftc-endorsements-2023.md` | Merged substantiation / disclosure sections |
| 38 | `38-algae-dha-ocean-oil.md` | Merged GOED oxidation sections |
| 40 | `40-catalog-audit-qa-seat.md` | Merged week-one gate / “park” definition |

Pieces **04–14, 16–19, 22–24, 26–28, 30, 32–37, 39** received the same pass: `voice_check: edited`, light line edits, duplicate-paragraph merges where the ≥1k expansion had stacked the same QA block twice.

## Commits on this branch (editor)

1. `662bbc5` — line-edit articles 01–20  
2. `a4ff78e` — line-edit articles 21–40  
3. *(pending)* — `EDITOR_REPORT.md` + manifest/import flag updates  

## Remaining for human QA / counsel

- Resolve `[VERIFY]` / `[CITE NEEDED]` before publish (ODS ULs, OEHHA MADL, USPSTF final grade, GOED monograph version, etc.).
- `18-multivitamins-cosmos-trial.md`: COSMOS = nutrition RCT (`NCT02422745`), not the repo — unchanged, still flagged in `MANIFEST.md`.
- No publish: `status: draft` retained; import per `WP_IMPORT.md` staging only.

## Sign-off

Editor agent: **pass** for voice, grammar, figure embeds, DSHEA, and word floor. Ready for science/QA partner review on PR #230.
