---
id: tph-05
slug: encoder-decoder-residuals-layernorm
title: "Encoder–decoder stack, residuals, and post-LN (2017)"
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
leads_to: ["tph-09", "tph-32"]
---

# Encoder–decoder stack, residuals, and post-LN (2017)

**Status:** staged draft. Not a publication.
**Lane:** public transformer architecture history.
**First public appearance:** 12 June 2017 (`arxiv-v1`), §3.1 of arXiv:1706.03762.
**Primary source:** Vaswani et al., *Attention Is All You Need*.

## The claim

The 2017 Transformer is not "attention plus a pile of MLPs." It is a **specific wiring**: six
encoder layers, six decoder layers, three kinds of attention, a position-wise feed-forward
network in every layer, residual connections around every sublayer, and **layer normalization
after the residual add** (post-LN). That wiring is the object later papers mean when they say
"vanilla Transformer," and it is also the object they start moving (Pre-LN, RMSNorm, decoder-only
deletion of cross-attention, encoder-only deletion of the decoder).

## What the artifact specified

**Encoder layer.** Two sublayers: multi-head self-attention, then the position-wise FFN. Each
is wrapped as \(\mathrm{LayerNorm}(x + \mathrm{Sublayer}(x))\). Dropout is applied to the
sublayer output before it is added.

**Decoder layer.** Three sublayers: masked self-attention, encoder–decoder cross-attention, then
the FFN. Same residual-plus-LayerNorm wrapper. The extra cross-attention sublayer is how target
tokens read the source. Delete it, and you no longer have this paper's translation model; you
have something that must get its conditioning another way (prompts, prefixes, adapters, or a
different encoder fusion).

**FFN.** Two linear maps with ReLU between them, inner width \(d_{\mathrm{ff}} = 2048\) on base,
applied identically at every position, different parameters per layer. This is the "position-wise"
part: no mixing across tokens inside the FFN. All token mixing is attention's job.

**Depth.** \(N = 6\) is the published default, not a discovered scaling law. The paper does not
train a 96-layer decoder. Later depth (GPT-3's 96, PaLM's 118) is a different era's bet, using
this residual template.

Figure 1 is the canonical drawing. Later slides that show only a decoder stack are teaching
GPT, not teaching this paper.

## What it displaced

The residual wrapper is borrowed (He et al. ResNet; Ba et al. LayerNorm) and should not be
credited as a 2017 invention. What is dated here is **post-LN as the transformer default**.
That default turned out to be brittle at depth. Xiong et al. (arXiv:2002.04745, 12 February 2020)
publicly analyze why post-LN transformers want warmup and why **Pre-LN** (LayerNorm before the
sublayer, residual add un-normalized) trains more stably. GPT-2 had already shipped a Pre-LN
decoder in 2019; the 2020 paper is the analysis, not the first use.

RMSNorm (Zhang and Sennrich, arXiv:1910.07467, 16 October 2019) later replaces LayerNorm's mean
subtraction with a root-mean-square, and becomes the open-weight default in the LLaMA family.
That is a 2019 public paper, not a 2023 invention.

## Immediate lineage

The encoder–decoder topology survives in T5, BART, and a long tail of translation and
summarization models. The residual-plus-norm template survives in almost everything, including
decoder-only LLMs that deleted half the diagram.

Two deletions define 2018:

- **No encoder** (`tph-07`, GPT-1): causal decoder, language-modeling objective, conditioning
  by prefix.
- **No decoder** (`tph-08`, BERT): bidirectional encoder, masked-LM objective, no
  auto-regressive stack.

A reader who calls BERT "a transformer" is correct in the layer sense and wrong in the
Figure-1 sense. This card exists so later cards can say which half they kept.

## What this draft does not claim

It does not claim post-LN is "wrong." It was what they trained, and it worked at \(N = 6\) with
warmup. It does not claim Pre-LN was secret before 2020. It does not claim any closed 2023–2026
model still uses ReLU FFNs (SwiGLU is public from 2020 and widely adopted; see `tph-32`).

Layer counts in later closed models are unpublished unless a report says them. This card does
not fill them in.

## Sources

- Vaswani et al., arXiv:1706.03762, §3.1 and Figure 1, published 2017-06-12 (`arxiv-v1`).
- Zhang and Sennrich, *Root Mean Square Layer Normalization*, arXiv:1910.07467, published
  2019-10-16 (`arxiv-v1`).
- Xiong et al., *On Layer Normalization in the Transformer Architecture*, arXiv:2002.04745,
  published 2020-02-12 (`arxiv-v1`).
- Shazeer, *GLU Variants Improve Transformer*, arXiv:2002.05202, published 2020-02-12
  (`arxiv-v1`).

## Draft debt

- Add He 2016 / Ba 2016 as predecessor citations with their own first-public dates if a
  predecessor pack opens.
- Quote GPT-2's Pre-LN wording from the 14 February 2019 report on the next pass.
