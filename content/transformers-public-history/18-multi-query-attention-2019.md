---
id: "tph-18"
slug: "multi-query-attention-2019"
title: "Multi-query attention (6 November 2019)"
status: "staged-draft"
series: "transformers-public-history"
era: "2019-refine"
first_public: "2019-11-06"
date_kind: "arxiv-v1"
arxiv: "1911.02150"
venue_later: ""
novelty_lane: "public-prior-art-only"
private_systems: "excluded"
depends_on: ["tph-03"]
leads_to: ["tph-42", "tph-47"]
---

# Multi-query attention (6 November 2019)

**Status:** staged draft. Not a publication.
**Lane:** public transformer architecture history.
**First public appearance:** 6 November 2019 (`arxiv-v1`).
**Primary source:** Shazeer, *Fast Transformer Decoding: One Write-Head is All You Need*,
arXiv:1911.02150.

## The claim

Shazeer isolates a decode-time fact the 2017 paper did not have to care about: **auto-regressive
generation is memory-bandwidth bound on the KV cache**, and most of that cache is duplicated
across heads. Multi-query attention (MQA) keeps many query heads and **one** key/value head.
The 2017 score formula does not change. The number of distinct K/V tensors per layer per token
does.

This is 6 November 2019. Grouped-query attention is 22 May 2023. Filing them together as
"2023 KV tricks" erases three and a half years and the reason GQA exists (MQA's quality gap).

## What the artifact specified

At training and at decode, \(h\) query projections, **one** shared \(K\) and \(V\). Cache
footprint per layer per token drops from \(2 \cdot h \cdot d_k\) to \(2 \cdot d_k\) (plus the
usual bytes-per-element). Shazeer reports large decode-speed wins on TPU-class hardware of
that era with small quality loss on the translation-style setups in the paper.

The paper is short and should be read. A lot of later "we use GQA" one-liners assume this
note.

## What it displaced

The identity "number of KV heads = number of query heads" as an architectural law. After MQA
it is a **cache vs quality knob**. Most of the field did not turn the knob until 2022–2023,
when longer contexts and larger batches made the cache the bill. That lag is the story
(`tph-00` already named it). The mechanism did not get better in 2023; the bill got bigger.

## Immediate lineage

PaLM (5 April 2022 arXiv) is a prominent later public model that uses MQA. GQA (Ainslie et
al., 2023) interpolates: \(g\) KV groups, typically \(g \in \{1, 8, h\}\), and — crucially —
an **uptraining** recipe from existing MHA checkpoints. Llama 2 70B is a widely cited GQA
adopter. DeepSeek-V2 MLA is a different compression (low-rank latent KV), 7 May 2024.

## What this draft does not claim

It does not claim MQA is free in quality at every size. The GQA paper exists because it was
not. It does not claim every 2024 open model uses MQA (many use GQA). It does not assign MQA
to closed models that have not said so.

## Sources

- Shazeer, arXiv:1911.02150, published 2019-11-06 (`arxiv-v1`).
- Chowdhery et al., *PaLM*, arXiv:2204.02311, published 2022-04-05 (`arxiv-v1`).
- Ainslie et al., arXiv:2305.13245, published 2023-05-22 (`arxiv-v1`).

## Draft debt

- Quote Shazeer's speedup table against the PDF.
