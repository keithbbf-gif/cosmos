---
id: "tph-20"
slug: "longformer-2020"
title: "Longformer: sliding window plus global tokens (10 April 2020)"
status: "staged-draft"
series: "transformers-public-history"
era: "2020-long-scale"
first_public: "2020-04-10"
date_kind: "arxiv-v1"
arxiv: "2004.05150"
venue_later: ""
novelty_lane: "public-prior-art-only"
private_systems: "excluded"
depends_on: ["tph-12"]
leads_to: ["tph-43", "tph-22"]
---

# Longformer: sliding window plus global tokens (10 April 2020)

**Status:** staged draft. Not a publication.
**Lane:** public transformer architecture history.
**First public appearance:** 10 April 2020 (`arxiv-v1`).
**Primary source:** Beltagy, Peters, Cohan, *Longformer: The Long-Document Transformer*,
arXiv:2004.05150.

## The claim

Longformer is the paper this series uses to date **sliding-window attention** as a public
Transformer mechanism, plus a small set of **global** tokens that attend to (and are
attended from) the whole sequence. That combination — local band plus hubs — is the pattern
Mistral 7B later ships for *causal* decode (27 September 2023 announcement), thirty-nine
months after this paper.

If you date sliding windows at Mistral, you lose the most informative lag in the pack.

## What the artifact specified

A dilated or non-dilated sliding window of width \(w\) on self-attention, implemented so
memory is \(O(n \cdot w)\) rather than \(O(n^2)\). Selected positions (for example `[CLS]`,
or task-specific question tokens) use **global attention**. Encoder and a Longformer-Encoder-
Decoder (LED) variant are discussed for seq2seq.

They fine-tune from RoBERTa-class checkpoints onto long documents (TriviaQA, Hyperpartisan,
WikiHop, and others). This is a **document encoder** paper first, not a 32k-chat paper.

## What it displaced

"BERT but we split the document into 512-token chunks and hope." After Longformer, long-
document QA and classification have a named block. It did not displace dense attention for
short sequences, where the window buys little.

## Immediate lineage

BigBird (28 July 2020) adds random sparse connections and more theory-flavored claims.
LED is the seq2seq cousin. Mistral 7B (announcement 2023-09-27; paper 2023-10-10) uses a
**rolling-buffer** sliding window at decode, window 4096, and is a causal LM, not a RoBERTa
fine-tune. Gemma 2 (31 July 2024 arXiv) interleaves local sliding and global layers. Those
are adoption and hybridization events. The window itself is 2020.

A "receptive field = window × layers" number is an **upper bound**, not a measurement. Cards
that repeat vendor receptive-field figures must say so (`tph-43` will).

## What this draft does not claim

It does not claim Longformer invented local attention in all of ML (convolutions are local
attention with weight sharing). It claims Longformer is the type-case *Transformer document*
window. It does not claim Mistral copied this paper; it claims the *mechanism class* is
already public.

## Sources

- Beltagy, Peters, Cohan, arXiv:2004.05150, published 2020-04-10 (`arxiv-v1`).
- Zaheer et al., arXiv:2007.14062, published 2020-07-28 (`arxiv-v1`).
- Jiang et al., *Mistral 7B*, arXiv:2310.06825, published 2023-10-10 (`arxiv-v1`);
  announcement 2023-09-27 (`official-blog`).

## Draft debt

- Quote default window widths from the paper.
- Confirm LED's first-public is this paper vs a later release note.
