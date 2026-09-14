---
id: tph-01
slug: attention-is-all-you-need-2017
title: "Attention Is All You Need (12 June 2017)"
status: staged-draft
series: transformers-public-history
era: 2017-break
first_public: "2017-06-12"
date_kind: arxiv-v1
arxiv: "1706.03762"
venue_later: "NeurIPS 2017 (camera-ready v5, 2017-12-06)"
novelty_lane: public-prior-art-only
private_systems: excluded
depends_on: ["tph-00"]
leads_to: ["tph-02", "tph-03", "tph-04", "tph-05"]
---

# Attention Is All You Need (12 June 2017)

**Status:** staged draft. Not a publication.
**Lane:** public transformer architecture history.
**First public appearance:** 12 June 2017 (`arxiv-v1`).
**Primary source:** Vaswani, Shazeer, Parmar, Uszkoreit, Jones, Gomez, Kaiser, Polosukhin,
arXiv:1706.03762.

## The claim

On 12 June 2017 the first public draft of *Attention Is All You Need* described a sequence
transduction stack that used **no recurrence and no convolution**. Alignment, which had been an
add-on between recurrent encoder and decoder, became the layer. The paper named the stack
**Transformer**, specified multi-head scaled dot-product attention, a position-wise feed-forward
sublayer, residual connections with layer normalization, and sinusoidal positional encodings, and
reported machine-translation numbers that made the bet checkable.

This is the start of the architecture history in this pack. Everything later is a mutation of
these blocks, a training-objective fork that keeps them, or a stated alternative that has to beat
them.

## What the artifact specified

The base model in Table 3 is not a vibe. It is:

- encoder depth \(N = 6\), decoder depth \(N = 6\);
- \(d_{\mathrm{model}} = 512\), \(d_{\mathrm{ff}} = 2048\), \(h = 8\) heads, \(d_k = d_v = 64\);
- residual + LayerNorm around each sublayer, with dropout on the sublayer output before the
  residual add;
- a position-wise feed-forward network \(\mathrm{ReLU}(xW_1 + b_1)W_2 + b_2\);
- learned input and output embeddings, output embedding weights tied to the pre-softmax
  projection, embeddings scaled by \(\sqrt{d_{\mathrm{model}}}\);
- sinusoidal positional encodings added to embeddings (they also tried learned embeddings and
  reported similar results);
- Adam with \(\beta_1 = 0.9\), \(\beta_2 = 0.98\), \(\varepsilon = 10^{-9}\), and the now-famous
  warmup-then-inverse-sqrt learning-rate schedule;
- label smoothing \(\varepsilon_{ls} = 0.1\);
- byte-pair encoding.

The big model doubles width (\(d_{\mathrm{model}} = 1024\), \(d_{\mathrm{ff}} = 4096\),
\(h = 16\)) and trains longer. The translation claims in the abstract are specific: **28.4 BLEU**
on WMT 2014 English-to-German, more than 2 BLEU above the previous best including ensembles;
**41.8 BLEU** on WMT 2014 English-to-French as a single model after 3.5 days on eight GPUs. The
body also says a strong big-model English-to-German run can be reached in about twelve hours on
eight P100s. Those are author-reported figures from the paper, not a later re-eval.

The authors are eight, all at Google for this work: Ashish Vaswani, Noam Shazeer, Niki Parmar,
Jakob Uszkoreit, Llion Jones, Aidan N. Gomez, Łukasz Kaiser, Illia Polosukhin. Later lore that
collapses this to "the Google brain paper" is true as an employer and false as a substitute for
the author list.

## What it displaced

In 2017 the default neural MT stack was still recurrent (often LSTM or GRU) with attention
bridging encoder and decoder, sometimes with convolutional alternatives (ConvS2S, ByteNet). Those
models already *used* attention. What they did not do was throw away the sequence-aligned
recurrent or convolutional backbone and let attention be the only path between positions.

The paper's own argument is not "attention is more linguistic." It is that recurrence prevents
training-time parallelization across positions, and that a constant number of sequential
operations plus \(O(1)\) path length between arbitrary positions is a better computational
inductive bias for long-range dependence than an \(O(n)\) recurrent unroll. Section 4's table
comparing layer type, complexity per layer, sequential operations, and maximum path length is the
architectural claim; the BLEU numbers are the existence proof.

## Immediate lineage

Three lineages leave this paper almost immediately, and they are easy to scramble:

1. **Keep the encoder–decoder and change the task** — later T5 and BART still look like this
   paper's topology.
2. **Throw away the encoder** — GPT-1 (11 June 2018, official PDF) is a decoder-only language
   model that keeps masked self-attention and drops cross-attention.
3. **Throw away the decoder** — BERT (11 October 2018) is an encoder-only bidirectional stack
   with a new objective.

Inside the paper, three mechanisms also become their own later subjects: scaled dot-product
attention (`tph-02`), multi-head attention (`tph-03`), and the positional encoding choice
(`tph-04`). Residual-plus-LayerNorm placement (`tph-05`) looks like plumbing until Pre-LN and
RMSNorm rewrite it.

## What this draft does not claim

It does not claim the 2017 paper invented attention, residual connections, or layer
normalization. It does not claim the eight-author list is the only later contributor to
"transformers." It does not treat the NeurIPS 2017 stamp as the public date; v5 (6 December 2017)
is the camera-ready, not the appearance.

It does not claim 28.4 / 41.8 BLEU would reproduce under a 2026 tokenizer and evaluation script.
Those numbers are what the paper reported on the then-standard WMT setups.

It does not describe any private product stack, and it does not analogize the 2017 block to one.

## Sources

- Vaswani et al., arXiv:1706.03762, published 2017-06-12 (`arxiv-v1`). Abstract-page
  submission history: v1 2017-06-12; v5 2017-12-06 (camera-ready); v7 2023-08-02 (later
  housekeeping). Export API `published` = 2017-06-12.
- Bahdanau, Cho, Bengio, *Neural Machine Translation by Jointly Learning to Align and Translate*,
  arXiv:1409.0473, published 2014-09-01 — predecessor attention, not this architecture.
- Luong, Pham, Manning, *Effective Approaches to Attention-based Neural Machine Translation*,
  arXiv:1508.04025 — predecessor dot-product attention.

## Draft debt

- Quote Table 2 (optimizers / regularizers) and Appendix C (variants) on a second pass.
- Confirm the twelve-hour P100 claim's exact sentence against PDF page, not memory of the
  abstract.
