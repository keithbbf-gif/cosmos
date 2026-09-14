---
id: "tph-24"
slug: "kaplan-scaling-laws-2020"
title: "Kaplan scaling laws (23 January 2020)"
status: "staged-draft"
series: "transformers-public-history"
era: "2020-long-scale"
first_public: "2020-01-23"
date_kind: "arxiv-v1"
arxiv: "2001.08361"
venue_later: ""
novelty_lane: "public-prior-art-only"
private_systems: "excluded"
voice_check: "edited"
voice_check_date: "2026-09-14"
depends_on: ["tph-10"]
leads_to: ["tph-23", "tph-35"]
---

# Kaplan scaling laws (23 January 2020)

**Status:** staged draft. Not a publication.
**Lane:** public transformer architecture history.
**First public appearance:** 23 January 2020 (`arxiv-v1`).
**Primary source:** Kaplan, McCandlish, Henighan, Brown, Chess, Child, Gray, Radford, Wu,
Amodei, *Scaling Laws for Neural Language Models*, arXiv:2001.08361.

## The claim

This paper is architecture history because it **changed which architectures got trained**.
Kaplan et al. fit power laws relating language-modeling loss to parameter count, dataset
size, and compute, for decoder-only Transformers in a then-current recipe. The operational
reading that spread (sometimes past what the paper strictly proved) was: **scale parameters
first; data will keep up**.

GPT-3 is easier to understand after this paper than before it, even though GPT-3's arXiv
stamp is four months later. Chinchilla (29 March 2022) is the public correction to the
compute-optimal *data/params ratio*, not a deletion of power-law thinking.

## What the artifact specified

Empirical loss curves vs \(N\) (non-embedding parameters), \(D\) (tokens), and \(C\)
(compute), with fitted exponents. They discuss overfitting frontiers and the idea of a
compute-efficient frontier. Architecture is held in the decoder-only Transformer family;
this is not a ViT paper and not a MoE paper.

The date is 23 January 2020 — *before* GPT-3, and easy to file wrongly as "the GPT-3
appendix."

## What it displaced

The habit of treating 340M BERT-Large as a destination. After Kaplan, a 10B or 100B run is
arguable as science rather than as vanity, *if* you believe the fitted exponents. That
belief is later qualified.

## Immediate lineage

Hoffmann et al., *Training Compute-Optimal Large Language Models* (Chinchilla),
arXiv:2203.15556, 29 March 2022: for a given compute, **smaller models, more tokens** than
the Kaplan-era operational recipe. LLaMA (27 February 2023) is an open-weight demonstration
of the Chinchilla-ish direction (7B–65B on more tokens than a 2020 reader would have
budgeted).

Sutton's "bitter lesson" is an essay, not this paper. Do not date scaling laws at that essay.

## What this draft does not claim

It does not claim the fitted exponents are universal across MoE, retrieval, or mixture-of-
depths. It does not claim Kaplan "got the math wrong" — Chinchilla changed the **frontier
under a different accounting of the optimal ratio**, with its own assumptions. Both papers
are public and both still get over-quoted.

## Sources

- Kaplan et al., arXiv:2001.08361, published 2020-01-23 (`arxiv-v1`).
- Hoffmann et al., arXiv:2203.15556, published 2022-03-29 (`arxiv-v1`).
- Brown et al., arXiv:2005.14165, published 2020-05-28 (`arxiv-v1`).

## Draft debt

- Quote the main fitted exponents from Kaplan §1 / §3 rather than paraphrasing.
