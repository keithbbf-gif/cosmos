---
id: tph-03
slug: multi-head-attention
title: "Multi-head attention (the 2017 split)"
status: staged-draft
series: transformers-public-history
era: 2017-break
first_public: "2017-06-12"
date_kind: arxiv-v1
arxiv: "1706.03762"
venue_later: "NeurIPS 2017"
novelty_lane: public-prior-art-only
private_systems: excluded
voice_check: edited
voice_check_date: 2026-09-14
depends_on: ["tph-02"]
leads_to: ["tph-18", "tph-42"]
---

# Multi-head attention (the 2017 split)

**Status:** staged draft. Not a publication.
**Lane:** public transformer architecture history.
**First public appearance:** 12 June 2017 (`arxiv-v1`), §3.2.2 of arXiv:1706.03762.
**Primary source:** Vaswani et al., *Attention Is All You Need*.

## The claim

A single attention head, given \(d_{\mathrm{model}} = 512\), is a large averaging operator. The
2017 paper's bet is that **several smaller heads in parallel** capture distinct relations (syntax,
anaphora, positional neighborhoods) that one averaged head smears. They project \(Q, K, V\) \(h\)
times, run scaled dot-product attention in each subspace, concatenate, and project back:

\[
\mathrm{MultiHead}(Q,K,V) = \mathrm{Concat}(\mathrm{head}_1,\ldots,\mathrm{head}_h)W^O
\]

\[
\mathrm{head}_i = \mathrm{Attention}(QW_i^Q, KW_i^K, VW_i^V)
\]

For the base model, \(h = 8\) and \(d_k = d_v = d_{\mathrm{model}}/h = 64\). Total compute is
kept comparable to a single full-dimension head because each head is narrower.

## What the artifact specified

Table 3, row (A) is the ablation people remember poorly. They hold compute roughly fixed and
vary \(h \in \{1, 4, 8, 16, 32\}\) with \(d_k = d_v = 512 / h\). One head is worse. Eight is the
default. Thirty-two heads with \(d_k = 16\) also degrades. The paper's reading: **more heads
help, until the per-head dimension is too small**. That is an empirical claim on WMT
English-to-German development BLEU, not a theorem.

The projections \(W_i^Q, W_i^K, W_i^V, W^O\) are learned and independent. Nothing in 2017 says
the key/value projections must be shared across heads. Sharing arrives later as a decode-time
memory move (MQA), and partial sharing as GQA. Those are not "multi-head done right"; they are
different operators with different cache footprints.

Appendix visualizations (the paper's attention figures) are qualitative. They show heads that
appear to specialize — long-distance verb agreement, attending to the end of sentences — and
they are the origin of a decade of "what do heads do" papers. They are not a causal explanation
of why \(h = 8\) won the ablation.

## What it displaced

Single-head attention as the default seq2seq alignment. Also, implicitly, the idea that a wider
single compatibility function is always better than several narrow ones. The 2017 ablation is
the first public evidence in this architecture that **head count is a hyperparameter with a
U-shaped quality curve** at fixed compute.

## Immediate lineage

Multi-head attention becomes so default that later papers stop specifying it unless they change
the sharing pattern:

- **MQA** (Shazeer, 6 November 2019): one key/value head, many query heads. Decode writes one
  set of K/V.
- **GQA** (Ainslie et al., 22 May 2023): \(g\) key/value groups, \(h/g\) query heads each. A
  continuum between MHA and MQA, with an uptraining recipe from existing MHA checkpoints.
- **MLA** (DeepSeek-V2, 7 May 2024): low-rank joint compression of K/V plus a decoupled RoPE
  channel. Still multi-head on the query side; the cache is no longer "one vector per head per
  token" in the 2017 sense.

Vision transformers inherit \(h\) unchanged (ViT-Base uses 12 heads). Mixture-of-experts papers
sometimes mix up "heads" and "experts"; they are not the same split. Experts route tokens to
FFN shards. Heads partition attention subspaces.

## What this draft does not claim

It does not claim every later model with "32 heads" is doing the 2017 thing — grouped and latent
variants keep the name and change the tensors. It does not claim the appendix figures prove
linguistic specialization. It does not treat any closed model's unpublished head layout as known.

The 2017 paper's "multi-head attention allows the model to jointly attend to information from
different representation subspaces" is the authors' motivation, not a measured decomposition.

## Sources

- Vaswani et al., arXiv:1706.03762, §3.2.2 and Table 3 row (A), published 2017-06-12 (`arxiv-v1`).
- Shazeer, arXiv:1911.02150, published 2019-11-06 (`arxiv-v1`).
- Ainslie et al., arXiv:2305.13245, published 2023-05-22 (`arxiv-v1`).
- DeepSeek-AI, arXiv:2405.04434, published 2024-05-07 (`arxiv-v1`).

## Draft debt

- Reproduce Table 3 row (A) BLEU numbers exactly from the PDF on the next pass.
- Separate "head specialization" literature (Clark et al., Michel et al. pruning) into a later
  interpretability card if that pack is opened.
