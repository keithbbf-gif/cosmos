---
id: tph-04
slug: original-positional-encodings
title: "Sinusoidal and learned absolute positions (2017)"
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
depends_on: ["tph-01"]
leads_to: ["tph-06", "tph-30", "tph-31"]
---

# Sinusoidal and learned absolute positions (2017)

**Status:** staged draft. Not a publication.
**Lane:** public transformer architecture history.
**First public appearance:** 12 June 2017 (`arxiv-v1`), §3.5 of arXiv:1706.03762.
**Primary source:** Vaswani et al., *Attention Is All You Need*.

## The claim

Self-attention has no built-in order. Without a position signal, the 2017 encoder is a bag of
token vectors. Section 3.5 adds **positional encodings** of the same dimension as
\(d_{\mathrm{model}}\) to the input embeddings. The paper's default is a fixed sinusoid:

\[
PE_{(pos, 2i)} = \sin\left(pos / 10000^{2i/d_{\mathrm{model}}}\right)
\]
\[
PE_{(pos, 2i+1)} = \cos\left(pos / 10000^{2i/d_{\mathrm{model}}}\right)
\]

They also trained **learned** absolute position embeddings and reported that the two versions
produced "nearly identical results" on the development set. The sinusoid was chosen because it
might extrapolate to sequence lengths unseen at training time — a hope later public work would
repeatedly test and, often, disappoint.

## What the artifact specified

Positions are **absolute indices** starting at the beginning of the (packed, batched) sequence.
The encoding is added, not concatenated. The same PE is shared across encoder and decoder
embeddings. Nothing in §3.5 is relative: the model is not told "token \(i\) is 3 steps left of
token \(j\)" except insofar as the sinusoidal basis makes that recoverable.

Table 3 row (E) is the positional ablation: learned vs sinusoidal, with essentially matched
BLEU. That is the entire 2017 public comparison. There is no long-context evaluation, no
"train short, test long" protocol, and no rotary construction.

ConvS2S (Gehring et al., arXiv:1705.03122, 8 May 2017) had already used learned absolute
position embeddings in a convolutional seq2seq model. The 2017 Transformer paper is therefore
not the first public learned-position move; it is the first time those embeddings (and the
sinusoidal alternative) sit under all-pairs self-attention as the only order signal.

## What it displaced

Recurrent unrolling, which carries position for free because time *is* the computation, and
convolution, which carries position via kernel offset. Removing those backbones forced an
explicit position channel. That channel becomes the most-revisited component in this series:
relative representations (Shaw, 6 March 2018), T5 relative bias (23 October 2019), RoPE
(20 April 2021), ALiBi (27 August 2021), NoPE (31 May 2023), interpolation recipes (2023), and
eventual proposals to drop positions from some layers or entirely.

The 2017 hope that sinusoids would extrapolate is the first statement of a problem that 2023
solved operationally by **not using 2017 positions** — by rotating, biasing, interpolating, or
deleting them.

## Immediate lineage

- **BERT** (11 October 2018) uses learned absolute embeddings, max length 512, and does not
  inherit the sinusoid default. That choice, plus the 512 cap, is why early BERT-family work
  treats long documents as a segmentation problem.
- **GPT-1 / GPT-2** also use learned absolute positions, with GPT-2's published window at 1024.
- **Shaw et al.** (6 March 2018) is the first public relative-position paper on this
  architecture; it belongs on the next card, not this one.
- **RoPE** will later argue that a rotation on \(Q\) and \(K\) injects relative position into
  the dot product without adding a vector to the residual stream. That is a different object
  than §3.5.

## What this draft does not claim

It does not claim sinusoids failed in 2017 — they matched learned embeddings on WMT at the
trained lengths. It does not claim the 10000 base is theoretically privileged; it is the
paper's constant. It does not claim later "position interpolation" methods apply to 2017
sinusoids (they are RoPE methods).

Jianlin Su described rotary embeddings on a blog before the RoFormer arXiv stamp. That blog
could not be re-fetched in this pass; RoPE is dated 20 April 2021 by arXiv v1 (`tph-30`) and
this card does not steal that date.

## Sources

- Vaswani et al., arXiv:1706.03762, §3.5 and Table 3 row (E), published 2017-06-12 (`arxiv-v1`).
- Gehring et al., *Convolutional Sequence to Sequence Learning*, arXiv:1705.03122, published
  2017-05-08 (`arxiv-v1`) — learned absolute positions in ConvS2S.
- Devlin et al., arXiv:1810.04805, published 2018-10-11 (`arxiv-v1`).
- Shaw, Uszkoreit, Vaswani, arXiv:1803.02155, published 2018-03-06 (`arxiv-v1`).

## Draft debt

- Quote the exact "nearly identical results" sentence and the Table 3 BLEU pair from the PDF.
- Decide whether ConvS2S learned positions deserve a predecessor card in a sequel pack.
