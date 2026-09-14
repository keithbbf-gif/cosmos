---
id: "tph-22"
slug: "bigbird-performer-2020"
title: "BigBird and Performer: random sparsity and FAVOR+ (July–September 2020)"
status: "staged-draft"
series: "transformers-public-history"
era: "2020-long-scale"
first_public: "2020-07-28"
date_kind: "arxiv-v1-family"
arxiv: "2007.14062"
venue_later: "Performer arXiv:2009.14794 on 2020-09-30"
novelty_lane: "public-prior-art-only"
private_systems: "excluded"
voice_check: "edited"
voice_check_date: "2026-09-14"
depends_on: ["tph-20", "tph-21"]
leads_to: ["tph-37", "tph-46"]
---

# BigBird and Performer: random sparsity and FAVOR+ (July–September 2020)

**Status:** staged draft. Not a publication.
**Lane:** public transformer architecture history.
**First public appearance:** 28 July 2020 (BigBird); 30 September 2020 (Performer).
**Primary sources:** Zaheer et al., *Big Bird: Transformers for Longer Sequences*,
arXiv:2007.14062; Choromanski et al., *Rethinking Attention with Performers*,
arXiv:2009.14794.

## The claim

By late summer 2020 the efficient-Transformer wave had a **sparse** capstone and a **kernel**
capstone.

**BigBird** (28 July 2020) combines window attention, global tokens, and **random** sparse
connections. The authors argue this pattern is expressive enough (they discuss universal
approximation and Turing completeness under stated conditions). It is Longformer plus random
edges plus a theory section, not a new score function.

**Performer** (30 September 2020) introduces **FAVOR+**: positive orthogonal random features
that unbiasedly (or nearly) approximate softmax attention in linear time and space. It is the
softmax-kernel cousin of Katharopoulos, aimed at being closer to the 2017 primitive rather
than replacing softmax with an arbitrary kernel.

## What the artifacts specified

BigBird: BERT-like and seq2seq experiments on long documents, genomics-flavored sequences,
and QA. Pattern hyperparameters (window, number of globals, number of random blocks) are
first-class. Implementation is still a sparse matmul problem.

Performer: the FAVOR+ estimator, analysis of variance / positivity, and drops into existing
Transformer code as a layer swap. They emphasize that the approximation is of *softmax*
attention, which is why this paper, not Linformer, is the one later "soft-max preserving
linear attention" citations reach for.

## What it displaced

A 2020 reader could honestly believe dense softmax attention was about to leave the default
stack. That belief did not survive FlashAttention (27 May 2022) plus the 2022–2023 decode-time
KV-cache era. BigBird and Performer remain correct papers; they ceased to be inevitable
defaults. Recording that reversal is part of architecture history.

## Immediate lineage

Pegasus, LongT5, and various "BigBird in production search/docs" talks are adoption. Performer
shows up more in research and in some long-sequence non-LLM settings. The 2025 Native Sparse
Attention paper is closer in spirit to BigBird's "learn or align a pattern" than to FAVOR+.

## What this draft does not claim

It does not certify the Turing-completeness discussion. It notes the paper makes it. It does
not claim FAVOR+ has vanishing error at 128k LLM context in production — that measurement is
not this card's artifact.

## Sources

- Zaheer et al., arXiv:2007.14062, published 2020-07-28 (`arxiv-v1`).
- Choromanski et al., arXiv:2009.14794, published 2020-09-30 (`arxiv-v1`).
- Beltagy et al., arXiv:2004.05150, published 2020-04-10 (`arxiv-v1`).
- Dao et al., arXiv:2205.14135, published 2022-05-27 (`arxiv-v1`).

## Draft debt

- Pull BigBird's exact pattern diagram labels.
- Quote FAVOR+ definition from Performer §2.
