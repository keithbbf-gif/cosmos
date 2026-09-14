---
id: "tph-47"
slug: "deepseek-mla-2024"
title: "DeepSeek-V2 MLA: low-rank latent KV (7 May 2024)"
status: "staged-draft"
series: "transformers-public-history"
era: "2024-2026-select"
first_public: "2024-05-07"
date_kind: "arxiv-v1"
arxiv: "2405.04434"
venue_later: "DeepSeek-V3 report 2024-12-27 continues the block"
novelty_lane: "public-prior-art-only"
private_systems: "excluded"
voice_check: "edited"
voice_check_date: "2026-09-14"
depends_on: ["tph-42", "tph-30"]
leads_to: ["tph-48"]
---

# DeepSeek-V2 MLA: low-rank latent KV (7 May 2024)

**Status:** staged draft. Not a publication.
**Lane:** public transformer architecture history.
**First public appearance:** 7 May 2024 (`arxiv-v1`).
**Primary source:** DeepSeek-AI, *DeepSeek-V2: A Strong, Economical, and Efficient
Mixture-of-Experts Language Model*, arXiv:2405.04434.

## The claim

Multi-head Latent Attention (MLA) compresses keys and values into a **low-rank latent**
that is what you cache, then up-projects per head. RoPE does not commute happily with that
compression, so V2 keeps a **decoupled RoPE channel** of small dimension. The paper reports
large KV-cache reductions and decode-throughput gains as author-measured figures (the
abstract's 93.3% cache reduction / 5.76× throughput are author-reported; this pack does
not re-benchmark them).

This is not GQA. GQA still stores a vector per KV head per token. MLA stores a latent plus
a small RoPE piece. Different compression, 2024 date.

V2 is also a DeepSeekMoE model (many small experts, shared experts). Do not reduce the
paper to MLA only; do not date MoE at V2 (`tph-27`).

## What the artifact specified

\(d_c\) latent width, \(d_h^R\) RoPE dim, head counts and layer counts in the paper /
later configs, MoE routing layout. DeepSeek-V3 (27 December 2024, arXiv:2412.19437) keeps
MLA and changes training/economy details (including multi-token prediction). DeepSeek-R1
(22 January 2025, arXiv:2501.12948) is a **reasoning / RL** paper on this family, not a
new attention primitive.

## What it displaced

The sense that GQA was the last word on cache math. After MLA, low-rank *joint* KV is a
named option. Cross-Layer Attention (21 May 2024, arXiv:2405.12981) and YOCO (8 May 2024,
arXiv:2405.05254) are the same month's other cache ideas. 2024 May is a cache-invention
cluster, analogous to 2023's retrofit cluster.

## Immediate lineage

V3, R1, and later DeepSeek Sparse Attention (V3.2-Exp line, 2025) which attacks *which
tokens to score*, not only how to store KV. Keep those axes separate.

## What this draft does not claim

It does not independently verify 93.3% or 5.76×. It quotes them as author-reported. It
does not treat unpublished competitors as "MLA-like."

## Sources

- DeepSeek-AI, arXiv:2405.04434, published 2024-05-07 (`arxiv-v1`).
- DeepSeek-AI, arXiv:2412.19437, published 2024-12-27 (`arxiv-v1`).
- DeepSeek-AI, arXiv:2501.12948, published 2025-01-22 (`arxiv-v1`).
- Ainslie et al., arXiv:2305.13245, published 2023-05-22 (`arxiv-v1`).

## Draft debt

- Quote \(d_c\) and head-dim numbers from V2 §2 against the PDF.
