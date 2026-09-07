# P03 — Family-axis occupancy; Porosity; superlinear cover

**Kind:** method / occupancy rule. **Status:** FILE. **Fee:** US provisional micro $65.

**Named quantity (Keith 2026-09-07):** **Porosity** (written Pourosity in the order — use **Porosity** in the spec). The quality of a coder is quantified as porosity: the hole-set / mistake surface of that model (error classes, unseen tools, fabrication modes).

## What it is (in-tree)

Same-vendor-family models are **one vote**, not two. Residual exposure is the **intersection** of hole-sets. Swiss-cheese image: Reason 1990 as *analogy*, not his accident-causation theory claimed as ours. Encoded `docs/MOTIF.md` 2026-09-07.

**Keith 2026-09-07 (this pass):** low-quality models with **DIFFERENT mistakes**, when **overlaid**, cover surface area **quickly**, at a **greater-than-linear** rate versus stacking copies. Copies of the same family leave holes aligned (coverage ≈ flat). Complementary porosity overlays punch residual holes.

Hypothesis to **measure** (do not invent an exponent in the provisional): coverage vs N for different-family overlays vs same-family copies. Same-family incremental coverage ≈ 0. Different-mistake overlay: residual ≈ p1·p2·… if holes are unaligned; cover of the remaining surface is large on the first different overlay. That is the “> linear vs copies / quickly cover” statement. Convert with a packet; do not put a fake number in the spec.

## Problem / scar

N copies of one API (self-consistency; “More Agents Is All You Need”) bill N times and keep the same holes. Hidden Clones (2026) and LLMs-as-Jury (2026) already *measure* family-correlated errors. Knight & Leveson 1986: independently written versions do not fail independently.

## Written description

1. Assign each model a **family** (training house + tool surface + observed failure mode). Occupancy rule, not a clustering theorem.
2. Quantify each coder’s **Porosity** p(m) as a hole-set measure (error classes / residual miss surface). Exact metric is an embodiment (pass/fail per task class, β co-failure, etc.).
3. When seating votes (ARCH, BUILD, CRITICS): same family does not count twice.
4. Overlay: residual holes of the ensemble ≈ intersection of porosities when mistakes **differ**; ≈ the first porosity when they **align**.
5. Prefer adding a *different-porosity* (different-mistake) model, including a **low-quality** one, over adding a high-quality copy of the same family. Predicted: surface cover grows faster than the same-family baseline (flat / linear-in-invoice only).
6. Dual-lane + different-family critics exist to punch **different** holes (P02, P05).

## Already public

Swiss-cheese occupancy in MOTIF.md on public `cosmos` (method text 2026-08-25; swiss cheese 2026-09-07 still in-tree). Family-axis papers 2026 are **their** measurements, not ours.

## Prior art to name (R1)

**Must cite:** Reason 1990 / BMJ 2000 (metaphor); Knight & Leveson 1986; Hidden Clones arXiv:2603.17111 (family bias; 17 models → ~3 independent voters); LLMs-as-Jury arXiv:2607.10139; co-failure ceiling arXiv:2606.27288; Wisdom and Delusion of LLM Ensembles arXiv:2510.21513 (coding, 5 families); More Agents Is All You Need arXiv:2402.05120 (**anti-shape**: same-model copies); Self-consistency arXiv:2203.11171; Mixture-of-Agents arXiv:2406.04692; Self-MoA arXiv:2502.00674 (**adverse** to naïve mixing); Estornell & Liu NeurIPS 2024; DZone/Cognaptus “swiss cheese AI” as **safety-stack** metaphor (not occupancy).

**Patents:** thin. No US patent found that claims “same family is one vote” / porosity overlay. UNKNOWN unpublished.

## What this is not

Not Reason’s aviation model. Not “ensembles exist.” Not a measured superlinear exponent. Not a clustering theorem.

## Suggested independent idea

Quantified **Porosity** of each coder; seating and overlay rules so that **different-mistake** (including low-quality) models cover residual surface faster than same-family copies.
