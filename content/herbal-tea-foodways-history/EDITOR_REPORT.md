# Herbal Tea Foodways History — EDITOR_REPORT

**Stream:** EDITOR (`content/herbal-tea-foodways-history/`)  
**Writer PR:** #536 (`cursor/herbal-tea-foodways-history-00f4`, 45-draft pack)  
**Date:** 2026-09-14  
**Editor outcome:** `voice_check: edited` on **all 45** staged drafts  

## Gate (45-draft pack)

| Check | Result |
| --- | --- |
| Draft count | **45** markdown essays (`NN-slug.md` under `stage-0N-*`) |
| `tools/lint_claims.py` | **OK** — frontmatter, Claims box, refuse-to-cure, word floor (≥700), uniqueness |
| Claims policy | **educational-foodways** on every draft; **no disease-name payoffs** outside draft `01` (refuse file) |
| Disease / wellness tripwire | **0** linter hits on forbidden phrases after editor pass |
| Thin / outline-only | **No** — writer pack was desk-ready; editor did not pad stubs |
| Decision | Full claims/voice hygiene pass; **light copy edits only** on nine drafts |

`GUARDRAILS.md`, `CITATIONS.md`, and `tools/lint_claims.py` were not rewritten. No new drafts were invented.

## What changed

### Pack-wide

- Set **`voice_check: edited`** in YAML front matter on all **45** draft files.
- **`README.md`:** voice/status note updated for editor pass.
- **`MANIFEST.toml`:** regenerated via `lint_claims.py --write-manifest` (word counts refreshed).

### Targeted copy (grammar / voice / claims hygiene)

| File | Notes |
| --- | --- |
| `12-caribbean-christmas-sorrel.md` | “premise of the garden” (avoids medical-sounding “condition”) |
| `06-thie-and-the-two-bins.md` | “not a clinic” (trade association, not “healer”) |
| `26-wartime-substitutes.md` | “nutrition lecture” (rose-hip food-supply history, not deficiency framing) |
| `36-chrysanthemum-as-summer-glass.md` | Dropped “later editor” meta; hedge stays honest |
| `39-butterfly-pea-and-pandan.md` | Jar vs night-market glass — “mood, not a meal” |
| `41-atay-mint-taught-the-leaf.md` | “city street” (clearer than bare “street”) |
| `23-greek-mountain-tea.md` | “cure story in a paper sleeve” (refusal without “panacea” slippage) |
| `44-label-literacy-grocery-tin.md` | “help you shop” (grammar fix) |

### Intentionally preserved

- Refusal sentences that **name** wellness, sickroom registers, or label moods to reject them (e.g. `40-tulsi`, `31-sassafras` safrole as **food-law** history, `43-how-journalists-flatten`).
- Draft `01` use of “condition” and “tumor” as **fence examples**, not payoffs.
- `status: draft`, `claims_posture: educational-foodways`, stage order and slugs.

## QA checklist (editor)

- [x] 45 files, each `voice_check: edited`
- [x] `python3 tools/lint_claims.py` passes with **0** errors
- [x] `python3 tools/lint_claims.py --write-manifest` run; manifest matches draft set
- [x] No new medical, supplement, or disease-payoff claims introduced
- [x] No live-publish or COSMOS wiring added
- [x] Stacked PR targets writer branch for **#536**, not `main`

## Handoff

- **Graphics / SEO:** unchanged in this pass; follow writer PR assets if any.
- **Fact desk:** bibliography draft (`45-working-bibliography.md`) still names what was opened vs deferred.
- **Publisher:** all files remain **`status: draft`** until Keith schedules.
