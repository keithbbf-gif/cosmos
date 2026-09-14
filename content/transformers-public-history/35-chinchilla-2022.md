---
id: "tph-35"
slug: "chinchilla-2022"
title: "Chinchilla: compute-optimal tokens vs parameters (29 March 2022)"
status: "staged-draft"
series: "transformers-public-history"
era: "2022-align-kernel"
first_public: "2022-03-29"
date_kind: "arxiv-v1"
arxiv: "2203.15556"
venue_later: ""
novelty_lane: "public-prior-art-only"
private_systems: "excluded"
depends_on: ["tph-24"]
leads_to: ["tph-41"]
---

# Chinchilla: compute-optimal tokens vs parameters (29 March 2022)

**Status:** staged draft. Not a publication.
**Lane:** public transformer architecture history.
**First public appearance:** 29 March 2022 (`arxiv-v1`).
**Primary source:** Hoffmann, Borgeaud, Mensch, Buchatskaya, Cai, Rutherford, Casas,
Hendricks, Welbl, Clark, Hennigan, Noland, Millican, van den Driessche, Damoc, Guy, Osindero,
Simonyan, Elsen, Rae, Vinyals, Sifre, *Training Compute-Optimal Large Language Models*,
arXiv:2203.15556.

## The claim

Chinchilla re-opens Kaplan's frontier and argues that under their accounting, **models like
Gopher (280B) were under-trained on tokens**. A compute-optimal 70B model (Chinchilla)
trained on more tokens beats a larger, hungrier model at the same compute. The architectural
consequence is immediate: the next public wave (LLaMA, many 7B–70B open models) chases
**data volume** rather than a 500B trophy.

## What the artifact specified

Three approaches to fitting the compute-optimal \(N(C)\) and \(D(C)\), a ~70B model trained
on ~1.4T tokens (paper figures; author-reported), and tables vs Gopher, GPT-3, and Jurassic
on then-current suites. The model is a decoder-only Transformer in the Gopher family
(DeepMind), not a new attention primitive.

The "20 tokens per parameter" folk number is a **popularization** of this paper and should
be treated as a slogan, not as a constant the paper asked everyone to tattoo. Later work
(including "over-training" small models for inference-optimal regimes) will move the ratio
again.

## What it displaced

The operational Kaplan-era bias toward parameter count as the primary prestige axis. After
Chinchilla, a 7B model trained on 1T–2T tokens is a serious object (LLaMA 7B is in that
cultural neighborhood). It did not displace MoE, where parameters and FLOPs had already
split (`tph-27`).

## Immediate lineage

LLaMA (27 February 2023), Llama 2, and the "TinyLlama / Phi train on more tokens than Kaplan
would have" line. Inference-optimal scaling (e.g. later papers arguing to over-train small
models) is a third regime and must not be back-dated to March 2022.

## What this draft does not claim

It does not claim DeepMind released Chinchilla weights (they did not). It does not claim
the fitted exponents travel to every tokenizer and every MoE. No private token counts are
invented for closed models.

## Sources

- Hoffmann et al., arXiv:2203.15556, published 2022-03-29 (`arxiv-v1`).
- Kaplan et al., arXiv:2001.08361, published 2020-01-23 (`arxiv-v1`).
- Touvron et al., arXiv:2302.13971, published 2023-02-27 (`arxiv-v1`).

## Draft debt

- Quote the paper's recommended \(N\) and \(D\) vs compute from the main table.
