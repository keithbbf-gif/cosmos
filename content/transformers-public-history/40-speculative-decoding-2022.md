---
id: "tph-40"
slug: "speculative-decoding-2022"
title: "Speculative decoding (30 November 2022)"
status: "staged-draft"
series: "transformers-public-history"
era: "2022-align-kernel"
first_public: "2022-11-30"
date_kind: "arxiv-v1"
arxiv: "2211.17192"
venue_later: ""
novelty_lane: "public-prior-art-only"
private_systems: "excluded"
depends_on: ["tph-23"]
leads_to: ["tph-45"]
---

# Speculative decoding (30 November 2022)

**Status:** staged draft. Not a publication.
**Lane:** public transformer architecture history.
**First public appearance:** 30 November 2022 (`arxiv-v1`).
**Primary source:** Leviathan, Kalman, Matias, *Fast Inference from Transformers via
Speculative Decoding*, arXiv:2211.17192.

## The claim

Speculative decoding is a **serving architecture**, not a new score function. A cheap
draft model proposes several future tokens; the large model **verifies** them in one
parallel forward over the draft span; accepted prefix is kept, the first rejection is
resampled from the large model's distribution. The output distribution is that of the
large model (under the paper's analysis), at lower wall-clock if the draft is good.

Same calendar day as the ChatGPT blog (30 November 2022). They are not the same artifact.
One is a product launch; one is an inference algorithm.

## What the artifact specified

The rejection-sampling / verification scheme, the claim of distributional equivalence, and
speedups that depend on draft acceptance rate. The large model still defines the
distribution; the draft model is a **proposer**. If the draft is a smaller sibling trained
on the same tokenizer, acceptance is often high on "easy" tokens and low on the first
hard one — which is why measured speedups are workload-dependent and must stay
author-reported until re-measured.

Two implementation details later papers keep tripping on:

1. Verification is a **single forward** of the large model over the drafted span, not a
   cheap heuristic. If your serving stack cannot batch that forward, you have not
   implemented the paper.
2. The first rejected token is sampled from the **adjusted** large-model distribution, not
   from the draft. Drop that correction and you have a greedy drafter, not speculative
   decoding.

Medusa, EAGLE, and later multi-token prediction heads are descendants that change how
drafts are proposed (sometimes without a second model). Those get their own dates when a
sequel serving pack opens. DeepSeek-V3's multi-token prediction is a *training* objective
that can feed a drafter; it is not this 2022 paper.

## What it displaced

The identity "auto-regressive = one token per large-model forward." After this paper, that
is an implementation default, not a law.

## Immediate lineage

Chen et al. concurrent/related speculative sampling work should be checked on a later pass
for exact independence. vLLM (12 September 2023) is a different serving move (paged KV).
They compose.

## What this draft does not claim

It does not claim every production API uses speculative decoding. It does not claim
acceptance rates from the paper transfer to 2026 chat workloads.

## Sources

- Leviathan, Kalman, Matias, arXiv:2211.17192, published 2022-11-30 (`arxiv-v1`).
- Kwon et al., *PagedAttention / vLLM*, arXiv:2309.06180, published 2023-09-12 (`arxiv-v1`).

## Draft debt

- Check concurrent DeepMind / other speculative sampling stamps so credit is not
  over-concentrated.
