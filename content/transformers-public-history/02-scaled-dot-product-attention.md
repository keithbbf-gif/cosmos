---
id: tph-02
slug: scaled-dot-product-attention
title: "Scaled dot-product attention (the 2017 primitive)"
status: staged-draft
series: transformers-public-history
era: 2017-break
first_public: "2017-06-12"
date_kind: arxiv-v1
arxiv: "1706.03762"
venue_later: "NeurIPS 2017"
novelty_lane: public-prior-art-only
private_systems: excluded
depends_on: ["tph-01"]
leads_to: ["tph-03", "tph-18", "tph-21", "tph-37"]
---

# Scaled dot-product attention (the 2017 primitive)

**Status:** staged draft. Not a publication.
**Lane:** public transformer architecture history.
**First public appearance:** 12 June 2017 (`arxiv-v1`), §3.2.1 of arXiv:1706.03762.
**Primary source:** Vaswani et al., *Attention Is All You Need*.

<figure class="tph-figure tph-figure--architecture">
  <img src="content/transformers-public-history/staged/graphics/fig-03-attention-compute-flow.svg"
       alt="Flowchart of scaled dot-product attention from Q K and V through softmax to output"
       width="900" height="420" loading="lazy" decoding="async"/>
  <figcaption><strong>Fig. 1.</strong> Dataflow for scaled dot-product attention (§3.2.1, arXiv:1706.03762). Shows the public equation form used throughout the series.</figcaption>
</figure>

## The claim

The 2017 paper did not merely say "use attention." It specified a particular bilinear form and a
particular scaling, then made that form the default for the next decade:

\[
\mathrm{Attention}(Q, K, V) = \mathrm{softmax}\left(\frac{QK^\top}{\sqrt{d_k}}\right)V
\]

Queries, keys, and values are packed as matrices so the operation is one batched matmul, a scale,
a softmax, and a second matmul. That packing is why the architecture trained on 2017 GPUs without
an explicit time step. It is also why the later cost story is about **materializing \(QK^\top\)**
— an \(n \times n\) matrix per head — rather than about the idea of matching tokens.

## What the artifact specified

Section 3.2.1 contrasts two compatibility functions already in the literature. Additive
attention (Bahdanau et al.) uses a one-hidden-layer feed-forward network. Dot-product attention
(Luong et al.) is \(QK^\top\). The paper chooses the dot-product form **because it is faster and
more space-efficient on then-current kernels**, and then scales by \(1/\sqrt{d_k}\) because, they
argue, for independent random queries and keys of variance 1 the unscaled dot products have
variance \(d_k\) and push softmax into small-gradient regions.

Three uses of the same primitive sit in one figure:

1. **Encoder self-attention.** \(Q, K, V\) all come from the previous encoder layer. Every
   position may attend to every other position.
2. **Decoder masked self-attention.** Same, but positions after the current one are set to
   \(-\infty\) before softmax so auto-regressive generation is legal.
3. **Encoder–decoder cross-attention.** Queries come from the decoder; keys and values come from
   the encoder output. This is the residual of classical seq2seq alignment.

The mask is an implementation detail that later becomes a product surface (causal vs bidirectional
vs prefix vs sliding window vs sparsity patterns). In 2017 it is a triangular causal mask plus
padding.

Complexity, as they tabulated: per-layer \(O(n^2 \cdot d)\), sequential operations \(O(1)\),
maximum path length \(O(1)\). The quadratic term is not an accident they failed to notice. It is
the price of all-pairs comparison, written down in 2017, and the object almost every 2019–2021
"efficient transformer" paper tries to reduce.

## What it displaced

Luong-style dot-product attention already existed. Two things are new enough to date:

- **Scaling** as a named, motivated, default part of the formula, not an optimizer trick.
- **Self-attention as the layer**, including encoder self-attention, rather than attention as a
  bridge between two recurrent towers.

A reader who writes "attention was invented in 2017" is wrong. A reader who writes "the
all-pairs scaled matmul that later kernels spent five years specializing is specified in
§3.2.1" is right.

## Immediate lineage

The primitive is stable. What changes around it:

- **Multi-head** (`tph-03`) splits \(d_{\mathrm{model}}\) into \(h\) learned projections so the
  same formula runs in parallel subspaces.
- **Sharing K/V heads** (MQA 2019, GQA 2023) leaves the formula alone and changes how many
  distinct \(K, V\) tensors exist at decode time.
- **Approximations** (Linformer, linear attention, Performer, LSH, sparse patterns) try to avoid
  materializing \(n \times n\).
- **FlashAttention** (2022) keeps the *math* exact and changes the *IO*: it never writes the full
  \(n \times n\) matrix to HBM. That is a systems rewrite of this section, not a new score
  function.

T5 later drops the \(1/\sqrt{d_k}\) scale and uses a relative-bias additive term instead. That is
a documented deviation, not a rumor; it is why "the 2017 formula" and "what T5 scores with" are
not interchangeable.

## What this draft does not claim

It does not claim the \(1/\sqrt{d_k}\) argument is the only correct normalization (RMSNorm-era
training, extra \(\log n\) scales, and QK-norm are later public variants). It does not claim
softmax is mandatory; sigmoid-attention and softmax-off-by-one are later public experiments and
get their own cards only if they shipped or were specified with a date.

It does not treat any vendor kernel as part of the 2017 specification.

## Sources

- Vaswani et al., arXiv:1706.03762, §3.2.1–3.2.3, published 2017-06-12 (`arxiv-v1`).
- Bahdanau, Cho, Bengio, arXiv:1409.0473, published 2014-09-01 (`arxiv-v1`).
- Luong, Pham, Manning, arXiv:1508.04025 (`arxiv-v1`; submission-history block not re-fetched in
  this pass — day commonly given as 2015-08-17 via Semantic Scholar; marked weaker than the
  2017 stamp).
- Raffel et al., *T5*, arXiv:1910.10683, published 2019-10-23 — relative bias, no \(1/\sqrt{d}\)
  scale.

## Draft debt

- Re-read Luong PDF and quote the exact compatibility function they used.
- Add a short note on attention dropout (the 2017 paper applies dropout to the softmax weights)
  so later "dropout on attention" claims have a home.
