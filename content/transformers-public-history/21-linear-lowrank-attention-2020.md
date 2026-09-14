---
id: "tph-21"
slug: "linear-lowrank-attention-2020"
title: "Linear and low-rank attention (June 2020)"
status: "staged-draft"
series: "transformers-public-history"
era: "2020-long-scale"
first_public: "2020-06-08"
date_kind: "arxiv-v1-family"
arxiv: "2006.04768"
venue_later: "Linformer 2020-06-08; linear attention Katharopoulos et al. 2020-06-29"
novelty_lane: "public-prior-art-only"
private_systems: "excluded"
voice_check: "edited"
voice_check_date: "2026-09-14"
depends_on: ["tph-02", "tph-19"]
leads_to: ["tph-22", "tph-46"]
---

# Linear and low-rank attention (June 2020)

**Status:** staged draft. Not a publication.
**Lane:** public transformer architecture history.
**First public appearance:** 8 June 2020 for Linformer; 29 June 2020 for Katharopoulos et al.
(`arxiv-v1-family`).
**Primary sources:** Wang et al., *Linformer*, arXiv:2006.04768; Katharopoulos, Vyas, Pappas,
Fleuret, *Transformers are RNNs*, arXiv:2006.16236.

## The claim

Two June 2020 papers attack the \(n \times n\) matrix by **changing the algebra**, not the
sparsity mask.

**Linformer** (8 June 2020) projects keys and values from length \(n\) down to a small
constant \(k\) with learned matrices, so attention is low-rank in sequence length: scores
are \(n \times k\), not \(n \times n\). The bet is that the attention matrix is approximately
low-rank.

**Linear attention** (Katharopoulos et al., 29 June 2020) rewrites
\(\mathrm{softmax}(QK^\top)V\) as a kernel feature map \(\phi(Q)\phi(K)^\top V\) that
associates to \(\phi(Q)(\phi(K)^\top V)\). The inner sum is a **running state** of size
independent of \(n\). The paper's title is the implication: that state makes the layer an
RNN at decode time.

These are different bets (learned projection vs kernel feature map) that popular lists file
as one "linear attention" bucket. This card keeps both dates.

## What the artifacts specified

Linformer: encoder-side experiments (often BERT-like), projection along *length*, shared or
per-layer projections in ablations. Quality is reported as close to BERT on standard
fine-tunes at the lengths they tested. The projection is **not** free at decode for causal
LMs in the way a recurrent state is; Linformer is a length-projection story.

Katharopoulos et al.: causal and non-causal variants, a specific feature map, and an
explicit recurrent formulation for auto-regressive generation. That recurrent view is the
bridge to later linearized / gated-delta / Mamba comparisons: everyone is arguing about
**what lives in the fixed-size state**.

Neither paper is Performer (30 September 2020), which gives a different feature map
(FAVOR+) with a closer relationship to softmax. Performer sits on the next card.

## What it displaced

The binary "dense quadratic or hand-sparse." After June 2020 there is a third public option:
**compress the sequence axis into a state or a short projected length**. Adoption in
production decoder-only LLMs stays rare through 2023. The 2024–2026 hybrid linear papers
(Gated DeltaNet, Qwen3-Next, Kimi Linear) are this line returning with better states, not
a new invention of the idea that attention can be associative.

## Immediate lineage

Performer (FAVOR+), linear Transformer follow-ups, the 2021 fast-weight / delta-rule paper
(Schlag, Irie, Schmidhuber, 22 February 2021, arXiv:2102.11174), RetNet (17 July 2023),
Mamba (1 December 2023). Keep softmax-exact FlashAttention out of this family. FlashAttention
does not change the algebra.

## What this draft does not claim

It does not claim linear attention matches softmax quality at 2024 LLM scale. Several later
labs publicly disagree with themselves on this (MiniMax 2025–2026 is the type case). It does
not treat any closed model as secretly linear.

Linformer's June 8 stamp is the family start used in the filename; Katharopoulos is 21 days
later and must not be back-dated.

## Sources

- Wang, Li, Khabsa, Fang, Ma, arXiv:2006.04768, published 2020-06-08 (`arxiv-v1`).
- Katharopoulos, Vyas, Pappas, Fleuret, arXiv:2006.16236, published 2020-06-29 (`arxiv-v1`).
- Schlag, Irie, Schmidhuber, arXiv:2102.11174, published 2021-02-22 (`arxiv-v1`).

## Draft debt

- Quote the exact feature map in Katharopoulos §3.
- Add Choromanski dates on the next card rather than here.
