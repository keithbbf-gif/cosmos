# Editor report — AI evals & benchmarks explainers

**Scope:** `content/ai-evals-benchmarks-explainers/` (46 articles + pack meta).  
**Related PR:** #310 (`cursor/ai-evals-benchmarks-explainers-c5d5`).  
**Editor branch:** `cursor/ai-evals-editor-pass-6c39`.  
**Date:** 2026-09-14.

## Production flags

- Set `voice_check: edited` on all 46 articles (essays + explainers).
- Updated `tools/validate_pack.py` to accept `voice_check: human` or `edited`.
- Updated `STYLE_GUIDE.md` and `NOVELTY_GUARDRAILS.md` checklist for the edited flag.
- Updated `README.md` to note editor pass complete.

## Novelty / scope

- Re-scanned article bodies for out-of-scope house names (`COSMOS`, `KMesh`, `ModelRater`, etc.): **no hits** in essays or explainers.
- Did not add COSMOS, private systems, unpublished dockets, or live leaderboard numbers.
- Left `FACT_CHECK.md` and bibliography claims unchanged except where copy edits touched surrounding prose.

## Voice and grammar changes (by file)

| File | Changes |
|------|---------|
| `essays/00-series-overview.md` | Reader-facing wording: “pack index” instead of `` `INDEX.md` ``; cross-links “relative within this pack”; guardrails note marked editor-only. |
| `essays/contamination-and-leakage.md` | Subhead: “Leakage without a villain”. |
| `essays/pass-at-k-and-the-coder-receipt.md` | “Stack Overflow snippet”; split comma splice in `pass@k` naive description. |
| `explainers/arc-agi.md` | “This explainer” instead of “this draft”. |
| `explainers/big-bench.md` | Title: “two hundred-plus tasks” (aligns with paper’s 204). |
| `explainers/decodingtrust.md` | “Trustworthiness slices” (clearer than bare “perspectives”); minor closing clarity. |
| `explainers/frontier-math.md` | Title: **Fields Medalist** spelling. |
| `explainers/glue.md` | Smoother climb/superGLUE transition (nested-quote fix). |
| `explainers/gpqa.md` | Removed duplicate Bowman paragraph; one-line Michael note in “An item in the hand”. |
| `explainers/hellaswag.md` | Syntax fix (“worked hard on”); tire-change clarity; trimmed repeated adversarial-filter block; **AI2 ARC-Challenge** disambiguation; subhead “How to read a HellaSwag line”. |
| `explainers/helm.md` | Plain language for contamination (“does not undo leakage…”). |
| `explainers/humaneval.md` | “Harness runs your function body”; Stack Overflow in DS-1000 line. |
| `explainers/ifeval.md` | “question marks” typo; subhead “Constraints a script can count”. |
| `explainers/imagenet-as-eval.md` | “Fei-Fei Li’s bet” (double possessive). |
| `explainers/legalbench.md` | IRAC expanded once. |
| `explainers/lmsys-chatbot-arena.md` | Removed “this draft” meta voice. |
| `explainers/mmlu.md` | “fifty-seven tasks” in body (matches title). |
| `explainers/winograd-schema.md` | Dropped duplicate WinoGrande pointer in closing mis-citation block. |
| `explainers/winogrande.md` | **WinoGrad** → Winograd; specific subheads. |

## Files read with no copy edits

Remaining essays and explainers were read against `STYLE_GUIDE.md` and `NOVELTY_GUARDRAILS.md`. No narrator banned diction, grammar errors, or scope leaks required changes beyond the table above.

## Validation

```text
python3 tools/validate_pack.py
→ articles=46 essays=6 explainers=40 unique_slugs=46 OK
```

## Not done (intentional)

- No WordPress import (`WP_IMPORT.md` unchanged).
- No portrait generation (`portrait: null` throughout).
- No merge of PR #310 (draft only).
- Did not rewrite essay openings wholesale (e.g. `what-a-benchmark-is.md` definitional lead kept as strong spine).

## Reviewer checklist

1. Spot-read edited files in the table above.
2. Confirm `voice_check: edited` on a sample of articles.
3. Run `python3 content/ai-evals-benchmarks-explainers/tools/validate_pack.py`.
4. Optional: diff against #310 head for scope-only changes outside this folder.
