# Fact-check notes

Dated claims and known soft spots from staging. A later editor should walk this file against `BIBLIOGRAPHY.md` before any production import.

## Intentional refusals

- **No live leaderboard numbers** except historical snapshots printed in the source papers (e.g. SWE-bench’s original Claude 2 figure of 1.96% on 2,294 issues; Arena’s “more than 240K votes” in the ICML 2024 paper; LiveBench’s early “below 70%” abstract claim). Those are labeled as dated.
- **No invented quotations.** Short paraphrase only.
- **ARC collision** is spelled out in both `ai2-arc` and `arc-agi`. Any table that says only “ARC” is a fail.
- **LMSYS / Chatbot Arena / lmarena.ai / LMArena** rename is treated as one social instrument with a new URL (LMSYS blog, 20 September 2024), not as three unrelated products.

## Soft spots an editor should re-open

1. **Humanity’s Last Exam.** arXiv:2501.14249 (January 2025) uses the public name; *Nature* 2026 uses “A benchmark of expert-level academic questions…”. Both are in the bibliography. Item counts and live scores will move; do not freeze a site percentage in an explainer.
2. **FrontierMath.** Author list grew across arXiv versions. Core organizers (Glazer, Erdil, Besiroglu, Epoch) are stable. Tiers in later Epoch pages should be cited to a dated URL if used more finely than this draft.
3. **AlpacaEval.** Version 1 vs length-controlled 2.0 is easy to smear. The explainer refuses a single “Alpaca” noun.
4. **MBPP size.** The 2021 paper describes ~1,000 problems and a sanitized subset; harnesses disagree on the eval N. The explainer avoids a fake precision.
5. **BIG-bench task count.** Commonly 204 in the paper’s accounting; the explainer says “hundreds” plus that common figure and refuses folklore precision.
6. **MT-Bench item count.** Commonly 80 in secondary write-ups; the explainer says “eighty… in the original write-up’s common telling” and points at the paper’s table.
7. **SimpleQA.** 4,326 questions per the 2024 paper. Three-way grading (correct / incorrect / not attempted) must not be collapsed on import.
8. **MMLU-Pro.** ~12,000 questions, 14 domains, 10-way choices, NeurIPS 2024. The 16–33% drop vs MMLU is the authors’ dated band, not a universal tax.
9. **HELM.** 30 models, 42 scenarios, 16 core × 7 metrics as the 2022–2023 paper describes them. Later “living” leaderboards are other versions.
10. **SWE-bench.** 2,294 issues, 12 Python repos, ICLR 2024. Lite / Verified / later forks are other instruments.

## Protocol traps (not errors, but lies if omitted)

- MMLU and MMLU-Pro without shot count or CoT.
- HumanEval / MBPP / LiveCodeBench without `k`, temperature, or file identity (original vs HumanEval+).
- Arena rank without date, category, or statistical pipeline.
- NQ without long vs short and open vs closed book.
- BBQ without ambiguous vs disambiguated.
- XTREME without per-language tables.
- GAIA / WebArena without tool stack or environment version.

## Novelty scan (this pack)

Searched at staging for house names listed in `NOVELTY_GUARDRAILS.md`. Hits must be zero in essays and explainers. Colophon files may mention the guardrail list itself.

## Style scan

Banned house-style words from `STYLE_GUIDE.md` should not appear as the narrator’s diction. Paper titles may contain them (MMLU-Pro’s “Robust”; HELM’s paper uses “robustness” as a metric name). Quoted titles and metric names are allowed; throat-clearing is not.
