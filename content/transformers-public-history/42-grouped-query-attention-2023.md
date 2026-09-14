---
id: "tph-42"
slug: "grouped-query-attention-2023"
title: "Grouped-query attention (22 May 2023)"
status: "staged-draft"
series: "transformers-public-history"
era: "2023-open-serve"
first_public: "2023-05-22"
date_kind: "arxiv-v1"
arxiv: "2305.13245"
venue_later: ""
novelty_lane: "public-prior-art-only"
private_systems: "excluded"
voice_check: "edited"
voice_check_date: "2026-09-14"
depends_on: ["tph-18", "tph-41"]
leads_to: ["tph-47"]
---

# Grouped-query attention (22 May 2023)

**Status:** staged draft. Not a publication.
**Lane:** public transformer architecture history.
**First public appearance:** 22 May 2023 (`arxiv-v1`).
**Primary source:** Ainslie, Lee-Thorp, de Jong, Zemlyanskiy, Lebrón, Sanghai, *GQA:
Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints*,
arXiv:2305.13245.

## The claim

GQA is the continuum between 2017 multi-head attention and 2019 multi-query attention:
\(h\) query heads share \(g\) key/value heads, \(1 \le g \le h\). The paper's second gift
is an **uptraining** recipe: take an already-trained MHA checkpoint, convert it, and train
a short extra phase rather than starting from scratch. That is why GQA could land in
production 70B models within weeks, not years.

MQA is 6 November 2019. GQA is 22 May 2023. They are not synonyms.

## What the artifact specified

Group structure, conversion from MHA, quality vs MQA vs MHA tables, and decode-time memory
math (cache scales with \(g\), not \(h\)). Llama 2 70B is the widely cited early adopter
(paper 18 July 2023 — eight weeks later). Many 2024 open `config.json` files show
`num_key_value_heads: 8` with `num_attention_heads: 32` or 64; that *shape* is GQA.

Uptraining is the reason this paper is not just "MQA with extra groups." An already-trained
MHA checkpoint has \(h\) distinct \(W^K, W^V\). The conversion has to **mean-pool or
otherwise collapse** those into \(g\) groups without throwing away the query heads. The
paper specifies that conversion plus a short continued-training phase. Ideas that need no
new pretrain ship in weeks; this is the type-case (`tph-00` already used it).

At decode, each query head still computes its own \(q\), but it reads the K/V of its
group. FLOPs for the score matmul drop only by the KV-side factor; the **memory traffic**
drop is the product feature. That is why GQA shows up in every 2024 serving slide even
when training FLOPs barely moved.

## What it displaced

A forced choice between MHA quality and MQA cache. After GQA, 8 KV heads is a boring
default at 7B–70B. MLA (`tph-47`) is the next cache compression that is *not* this
grouping.

## Immediate lineage

Llama 2 70B, Mistral 7B (also GQA + window), Mixtral, Gemma, and most 2024 dense open
decoders. Models that still use full MHA at 7B (some early LLaMA-1 configs) look dated on
the cache axis.

## What this draft does not claim

It does not claim GQA is always quality-neutral at \(g=1\). The paper exists because
\(g=1\) (MQA) hurt. It does not assign GQA to closed models that have not said so.

## Sources

- Ainslie et al., arXiv:2305.13245, published 2023-05-22 (`arxiv-v1`).
- Shazeer, arXiv:1911.02150, published 2019-11-06 (`arxiv-v1`).
- Touvron et al., arXiv:2307.09288, published 2023-07-18 (`arxiv-v1`).

## Draft debt

- Quote the uptraining schedule from the paper.
