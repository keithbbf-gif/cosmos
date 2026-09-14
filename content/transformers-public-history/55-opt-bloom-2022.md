---
id: "tph-55"
slug: "opt-bloom-2022"
title: "OPT and BLOOM: open dense decoders before LLaMA (2022)"
status: "staged-draft"
series: "transformers-public-history"
era: "2022-align-kernel"
first_public: "2022-05-02"
date_kind: "arxiv-v1-family"
arxiv: "2205.01068"
venue_later: "BLOOM arXiv:2211.05100 on 2022-11-09"
novelty_lane: "public-prior-art-only"
private_systems: "excluded"
depends_on: ["tph-23", "tph-31"]
leads_to: ["tph-41"]
---

# OPT and BLOOM: open dense decoders before LLaMA (2022)

**Status:** staged draft. Not a publication.
**Lane:** public transformer architecture history.
**First public appearance:** 2 May 2022 (OPT); 9 November 2022 (BLOOM).
**Primary sources:** Zhang et al., *OPT: Open Pre-trained Transformer Language Models*,
arXiv:2205.01068; BigScience, *BLOOM*, arXiv:2211.05100.

## The claim

A history that jumps from GPT-3 (closed, May 2020) to LLaMA (February 2023) erases a year
of **public weights**. OPT (2 May 2022) is Meta's dense decoder series up to 175B, released
with a training log that is as important as the block. BLOOM (9 November 2022) is a 176B
multilingual dense decoder from the BigScience collaboration, with a public ROOTS corpus
story and **ALiBi** rather than learned absolute PE.

Neither is a new attention primitive. Both are the reason "open LLM" is not a 2023 noun.

GPT-NeoX-20B (14 April 2022, arXiv:2204.06745) and GPT-J (2021) sit in the same open-dense
season. This card uses OPT and BLOOM as the 100B-class type-cases.

## What the artifacts specified

OPT: GPT-3-like decoder settings, a 125M–175B family, training instability notes (the log
is the architecture-adjacent artifact: loss spikes, restarts). BLOOM: 176B, 70B and smaller
siblings, ALiBi (`tph-31`), multilingual tokenizer, Responsible AI license of that moment,
and a paper that actually describes data governance. BLOOM's ALiBi choice is why this card
depends on `tph-31` rather than on RoPE.

The Pile (31 December 2020 / 1 January 2021, arXiv:2101.00027) is the earlier public
*data* artifact many of these stacks sit on. Data is architecture when it is the only
thing that changed; here it is a cited input.

## What it displaced

The excuse that 100B-class decoders could not be studied outside one API. After OPT/BLOOM,
the limit was GPUs and licenses, not the absence of weights. LLaMA still displaced them
as the *default starting checkpoint* in 2023 on quality-per-size. That is adoption, and
both facts can be on the same timeline.

## Immediate lineage

RedPajama, OpenLLaMA, Pythia (3 April 2023, a *suite* for studying scale, not a new
block), and the 2023 instruction wrappers. Pythia deserves a sequel card if someone wants
the "science of training" axis.

## What this draft does not claim

It does not claim OPT matched GPT-3 on every eval (the paper is frank). It does not claim
BLOOM's license choices are architecture. It does not treat later Llama weights as these
models.

## Sources

- Zhang et al., arXiv:2205.01068, published 2022-05-02 (`arxiv-v1`).
- BigScience, arXiv:2211.05100, published 2022-11-09 (`arxiv-v1`).
- Black et al., arXiv:2204.06745, published 2022-04-14 (`arxiv-v1`).
- Gao et al., *The Pile*, arXiv:2101.00027, published 2020-12-31 (`arxiv-v1`).

## Draft debt

- Quote BLOOM's layer/width table and OPT-175B's published config.
