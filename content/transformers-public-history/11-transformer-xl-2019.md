---
id: "tph-11"
slug: "transformer-xl-2019"
title: "Transformer-XL: segment recurrence beyond a fixed window (9 January 2019)"
status: "staged-draft"
series: "transformers-public-history"
era: "2019-refine"
first_public: "2019-01-09"
date_kind: "arxiv-v1"
arxiv: "1901.02860"
venue_later: "ACL 2019"
novelty_lane: "public-prior-art-only"
private_systems: "excluded"
voice_check: "edited"
voice_check_date: "2026-09-14"
depends_on: ["tph-06", "tph-07"]
leads_to: ["tph-20", "tph-45"]
---

# Transformer-XL: segment recurrence beyond a fixed window (9 January 2019)

**Status:** staged draft. Not a publication.
**Lane:** public transformer architecture history.
**First public appearance:** 9 January 2019 (`arxiv-v1`).
**Primary source:** Dai, Yang, Yang, Carbonell, Le, Salakhutdinov, *Transformer-XL: Attentive
Language Models Beyond a Fixed-Length Context*, arXiv:1901.02860.

## The claim

A learned absolute position embedding plus a 512-token window is a hard stop. Transformer-XL
is the first widely cited **decoder-side** attempt to let a Transformer language model reuse
hidden states from the previous segment instead of pretending each chunk is a new world. The
mechanism is **segment-level recurrence**: cache the last segment's activations, attend to them
as extra memory, and stop the positional scheme from colliding across segments.

This is a 9 January 2019 paper, not an ACL-2019 paper. Dating it by the venue puts it after
GPT-2 (14 February 2019) when it is actually first.

## What the artifact specified

Training and evaluation cut the corpus into segments. For segment \(\tau\), attention over
layer \(n\) may read keys/values (or hidden states, in their formulation) produced for segment
\(\tau-1\) at the same layer, **stopped-gradient**. The effective context is therefore longer
than one segment, and the extra memory does not back-propagate through time without bound.

Absolute 2017 positions would break under this reuse (token 1 of the new segment would look
like token 1 of the old one). They therefore use a **relative** positional scheme related to
Shaw, so scores depend on offset rather than on a recycled absolute id.

They report state-of-the-art perplexity on enwik8, text8, WikiText-103, One Billion Word, and
Penn Treebank, with an attention span they measure in thousands of tokens. Those figures are
author-reported 2019 language-modeling numbers.

## What it displaced

The unspoken identity "Transformer LM = BERT-style fixed window, reset every chunk." It also
previewed, without shipping a product cache, the idea that **past K/V are a first-class
state**. GPT-2 still used a fixed 1024 window. The production KV cache of 2022–2023 is not
Transformer-XL (it is usually same-segment causal decode), but the *mental model* of attending
into a stored past is already public here.

## Immediate lineage

XLNet (19 June 2019) reuses Transformer-XL's backbone as the permutation-LM vehicle. Compressive
Transformer (Rae et al., 2019) adds compressed older memories. Later Infini-attention
(10 April 2024) and various "memory tokens" papers are distant cousins: they keep a compressed
past rather than a raw previous segment. Do not collapse them into this card.

Longformer and BigBird solve a different problem (full bidirectional documents with sparse
patterns) and are 2020.

## What this draft does not claim

It does not claim Transformer-XL is a linear-time attention mechanism. Attention inside the
extended window is still quadratic in the *attended* length. It does not claim modern LLM
serving uses segment recurrence; most do not. It does not treat XLNet's permutation objective
as part of this paper.

## Sources

- Dai et al., arXiv:1901.02860, published 2019-01-09 (`arxiv-v1`).
- Shaw et al., arXiv:1803.02155, published 2018-03-06 (`arxiv-v1`).
- Yang et al., *XLNet*, arXiv:1906.08237, published 2019-06-19 (`arxiv-v1`).

## Draft debt

- Quote the exact relative-encoding formula from the PDF (the paper's version is not identical
  to Shaw's).
- Record enwik8 bit-per-character numbers from the table, not from memory.
