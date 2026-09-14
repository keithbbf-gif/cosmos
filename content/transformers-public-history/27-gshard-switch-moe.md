---
id: "tph-27"
slug: "gshard-switch-moe"
title: "GShard and Switch: mixture-of-experts on the FFN (2020–2021)"
status: "staged-draft"
series: "transformers-public-history"
era: "2020-long-scale"
first_public: "2020-06-30"
date_kind: "arxiv-v1-family"
arxiv: "2006.16668"
venue_later: "Switch Transformer arXiv:2101.03961 on 2021-01-11"
novelty_lane: "public-prior-art-only"
private_systems: "excluded"
voice_check: "edited"
voice_check_date: "2026-09-14"
depends_on: ["tph-05"]
leads_to: ["tph-44"]
---

# GShard and Switch: mixture-of-experts on the FFN (2020–2021)

**Status:** staged draft. Not a publication.
**Lane:** public transformer architecture history.
**First public appearance:** 30 June 2020 (GShard); 11 January 2021 (Switch).
**Primary sources:** Lepikhin et al., *GShard*, arXiv:2006.16668; Fedus, Zoph, Shazeer,
*Switch Transformers*, arXiv:2101.03961.

## The claim

Mixture-of-experts, in this pack, is **not a new attention primitive**. It is a new way to
scale the **FFN**: a router sends each token to one or few expert MLPs, so parameter count
grows faster than FLOPs per token. GShard (30 June 2020) shows the device at translation
scale with automatic sharding. Switch (11 January 2021) simplifies to **top-1** routing and
pushes trillion-parameter language models as a public claim.

Shazeer et al. 2017 (*Outrageously Large Neural Networks*) is a predecessor MoE paper
**before** this series' 2017-06-12 start for the *Transformer stack*. The Transformer-era
type-cases are GShard and Switch.

## What the artifacts specified

GShard: MoE on the encoder–decoder FFN, routing and load-balancing, compiler/sharding story
for TPU meshes. Switch: replace the FFN with a Switch layer (router + one expert per token
in the simple form), extensive discussion of instability, auxiliary losses, and the
parameter/FLOP distinction. Both keep dense attention unless they say otherwise.

A later reader who calls Mixtral "the first MoE LM" is wrong by three years. Mixtral
(announcement 11 December 2023; paper 8 January 2024) is the widely *used open-weight*
sparse MoE. The mechanism class is 2020–2021 public.

## What it displaced

The Kaplan-era habit of treating "parameters" and "FLOPs per token" as one knob. After
Switch they are two knobs. That is why a 8×7B Mixture can be a 13B-class flop model and a
47B-class parameter model (Mixtral's later public numbers) without contradiction.

## Immediate lineage

GLaM, ST-MoE, NLLB's experts, Mixtral 8×7B / 8×22B, DeepSeekMoE / DeepSeek-V2–V3 expert
layouts, and many 2024–2025 open MoEs. Expert-choice routing vs token-choice routing is a
later fork (not this card's job except to note it exists).

## What this draft does not claim

It does not claim top-1 Switch routing is what Mixtral uses (Mixtral is top-2 of 8, per its
paper). It does not assign unpublished GPT-4 routing rumors any status. The GPT-4 report
does not specify MoE.

## Sources

- Lepikhin et al., arXiv:2006.16668, published 2020-06-30 (`arxiv-v1`).
- Fedus, Zoph, Shazeer, arXiv:2101.03961, published 2021-01-11 (`arxiv-v1`).
- Jiang et al., *Mixtral of Experts*, arXiv:2401.04088, published 2024-01-08 (`arxiv-v1`).

## Draft debt

- Quote Switch's largest published parameter count from the paper, as author-reported.
