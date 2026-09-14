---
id: "tph-37"
slug: "flashattention-2022"
title: "FlashAttention: exact attention, IO-aware (27 May 2022)"
status: "staged-draft"
series: "transformers-public-history"
era: "2022-align-kernel"
first_public: "2022-05-27"
date_kind: "arxiv-v1"
arxiv: "2205.14135"
venue_later: "NeurIPS 2022"
novelty_lane: "public-prior-art-only"
private_systems: "excluded"
depends_on: ["tph-02", "tph-22"]
leads_to: ["tph-45", "tph-48"]
---

# FlashAttention: exact attention, IO-aware (27 May 2022)

**Status:** staged draft. Not a publication.
**Lane:** public transformer architecture history.
**First public appearance:** 27 May 2022 (`arxiv-v1`).
**Primary source:** Dao, Fu, Ermon, Rudra, Ré, *FlashAttention: Fast and Memory-Efficient
Exact Attention with IO-Awareness*, arXiv:2205.14135.

<figure class="tph-figure tph-figure--spread">
  <img src="content/transformers-public-history/staged/graphics/fig-05-context-mechanisms-timeline.svg"
       alt="Timeline of public sparse attention KV-cache and IO-aware attention mechanisms from 2019 to 2023"
       width="1200" height="500" loading="lazy" decoding="async"/>
  <figcaption><strong>Fig. 1.</strong> Public mechanisms on the length and memory axis preceding and surrounding FlashAttention (27 May 2022). Not a vendor context-window chart.</figcaption>
</figure>

## The claim

FlashAttention is the paper that told the 2019–2021 efficient-Transformer wave that **the
bill was often HBM traffic, not FLOPs**. By tiling \(Q, K, V\) to on-chip SRAM, streaming
the softmax, and **not writing the \(n \times n\) matrix to HBM**, they implement the 2017
formula *exactly* (up to numerical details) with lower memory and higher speed on then-current
NVIDIA GPUs.

This is not an approximation family. After 27 May 2022, an approximate attention method has
to beat a much faster exact baseline. Several 2020 papers look different in that light.

## What the artifact specified

The IO complexity argument (HBM vs SRAM), the blocking algorithm, the recomputation of
attention weights on the backward pass rather than storing the full matrix, and wall-clock
gains on BERT-class and GPT-class training. Author-reported speedups are hardware-specific
(A100-era in the paper).

FlashAttention-2 (17 July 2023, arXiv:2307.08691) changes work partitioning. FlashAttention-3
(11 July 2024, arXiv:2407.08608) targets Hopper asynchrony and low precision. Those are
later kernels, same algebra.

## What it displaced

The practical urgency of *some* linear/sparse approximations for *training* at 2k–8k
lengths. It did not delete the KV-cache bill at **decode**, which is a different IO story
(MQA/GQA/MLA, PagedAttention, windowing). People who say "FlashAttention solved attention
cost" are talking about training (and some prefills), not about 128k decode.

## Immediate lineage

xFormers, PyTorch SDPA, compiler-generated attention (FlexAttention, later), and the fact
that 2023–2024 open pre-trains treat FlashAttention-class kernels as plumbing. SageAttention
and other numeric variants are later.

## What this draft does not claim

It does not claim the algorithm is hardware-universal (TPU implementations are a different
engineering story). It does not claim exactness in every fused int8/fp8 path of later
kernels — FA3 explicitly discusses low precision. It does not describe any private kernel.

## Sources

- Dao et al., arXiv:2205.14135, published 2022-05-27 (`arxiv-v1`).
- Dao, *FlashAttention-2*, arXiv:2307.08691, published 2023-07-17 (`arxiv-v1`).
- Shah et al. / Dao line, *FlashAttention-3*, arXiv:2407.08608, published 2024-07-11
  (`arxiv-v1`).

## Draft debt

- Quote the paper's IO complexity table.
