---
id: "tph-44"
slug: "mixtral-dpo-2023"
title: "Mixtral and DPO: sparse experts and RL-free preference (2023–2024)"
status: "staged-draft"
series: "transformers-public-history"
era: "2023-open-serve"
first_public: "2023-05-29"
date_kind: "arxiv-v1-family"
arxiv: "2305.18290"
venue_later: "DPO 2023-05-29; Mixtral announcement 2023-12-11; Mixtral paper 2024-01-08"
novelty_lane: "public-prior-art-only"
private_systems: "excluded"
voice_check: "edited"
voice_check_date: "2026-09-14"
depends_on: ["tph-27", "tph-34"]
leads_to: ["tph-47"]
---

# Mixtral and DPO: sparse experts and RL-free preference (2023–2024)

**Status:** staged draft. Not a publication.
**Lane:** public transformer architecture history.
**First public appearance:** 29 May 2023 (DPO); Mixtral announcement 11 December 2023;
Mixtral paper 8 January 2024.
**Primary sources:** Rafailov et al., arXiv:2305.18290; Jiang et al., *Mixtral of Experts*,
arXiv:2401.04088.

## The claim

Two late-2023 public moves changed what people trained *on top of* the modern decoder.

**DPO** (29 May 2023) shows that the RLHF-with-PPO loop can be replaced, under stated
assumptions, by a **classification-style loss on preference pairs** that treats the language
model itself as the implicit reward model. No separate PPO trainer is required. That is a
training-architecture deletion.

**Mixtral 8×7B** (announcement 11 December 2023; paper 8 January 2024) is a sparse MoE:
for each token, **top-2 of 8** FFN experts fire. Active FLOPs look like a ~13B dense model;
parameters look like ~47B. Attention stays dense (plus the Mistral-family window/GQA
choices). This is Switch/GShard's family, finally as a widely run open-weight chat base.

## What the artifacts specified

DPO: the Bradley-Terry derivation, the closed-form policy loss, experiments vs PPO-class
baselines on the paper's setups. Mixtral: 8 experts, top-2, sliding window / GQA inherited
from the 7B family, multilingual + code claims, author-reported evals. An 8×22B sibling
appears later and is not this stamp.

## What it displaced

"You must stand up PPO to align" as the only adult path (DPO), and "open 7B/13B dense is
the only small-lab MoE-free default" (Mixtral). Neither displacement is total. Many labs
still run PPO/GRPO; many still ship dense 7B.

## Immediate lineage

ORPO, KTO, SimPO, and GRPO (later public preference/policy papers, especially in reasoning
models). DeepSeekMoE / V2 / V3 expert layouts. Zephyr (25 October 2023) is an early public
DPO-flavored alignment of a Mistral base.

## What this draft does not claim

It does not claim DPO matches PPO on every product metric. It does not claim Mixtral is
the first MoE LM (`tph-27`). It does not reconstruct unpublished GPT-4 routing.

## Sources

- Rafailov et al., arXiv:2305.18290, published 2023-05-29 (`arxiv-v1`).
- Jiang et al., arXiv:2401.04088, published 2024-01-08 (`arxiv-v1`).
- Mistral, *Mixtral of experts*, 2023-12-11 (`official-blog`).

## Draft debt

- Quote Mixtral's exact active-parameter arithmetic from the paper.
