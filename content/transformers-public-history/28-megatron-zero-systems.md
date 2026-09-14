---
id: "tph-28"
slug: "megatron-zero-systems"
title: "Megatron and ZeRO: the training-system stack (2019–2020)"
status: "staged-draft"
series: "transformers-public-history"
era: "2020-long-scale"
first_public: "2019-09-17"
date_kind: "arxiv-v1-family"
arxiv: "1909.08053"
venue_later: "ZeRO arXiv:1910.02054 on 2019-10-04"
novelty_lane: "public-prior-art-only"
private_systems: "excluded"
voice_check: "edited"
voice_check_date: "2026-09-14"
depends_on: ["tph-10"]
leads_to: ["tph-23", "tph-36"]
---

# Megatron and ZeRO: the training-system stack (2019–2020)

**Status:** staged draft. Not a publication.
**Lane:** public transformer architecture history.
**First public appearance:** 17 September 2019 (Megatron-LM); 4 October 2019 (ZeRO).
**Primary sources:** Shoeybi et al., *Megatron-LM*, arXiv:1909.08053; Rajbhandari, Rasley,
Ruwase, He, *ZeRO*, arXiv:1910.02054.

## The claim

Some "architecture" is **where the tensors live**. Megatron-LM (17 September 2019) publicizes
**tensor (model) parallelism** for Transformer layers: split heads and MLP matrices across
GPUs inside a layer, with the specific all-reduce pattern that keeps the block correct.
ZeRO (4 October 2019) publicizes **optimizer-state / gradient / parameter sharding** so data
parallel training no longer replicates the full Adam state on every GPU.

Without these papers, GPT-3-class and PaLM-class training stories are magic. With them, the
2017 block is unchanged and the *machine* is not.

## What the artifacts specified

Megatron: intra-layer partitioning of attention and FFN, vocabulary-parallel embeddings in
later revisions, pipeline parallelism as a sibling (the broader Megatron-LM line). The 8.3B
(and later larger) GPT-like models in the paper are existence proofs on NVIDIA then-current
DGX systems.

ZeRO stages 1–3: shard optimizer states, then gradients, then parameters. ZeRO-Offload and
ZeRO-Infinity are later public extensions (2021) and must not steal the 2019-10-04 stamp.
DeepSpeed is the systems vehicle; this card dates the paper, not the repo's every commit.

## What it displaced

The idea that "we cannot train that" was only a modeling problem. After Megatron+ZeRO it is
often a **partitioning** problem. FSDP (FairScale / PyTorch) is a later widely used public
implementation of the ZeRO-3 idea; date FSDP by its own docs if a systems sequel pack
opens.

## Immediate lineage

Megatron-Turing NLG, GPT-NeoX (14 April 2022, arXiv:2204.06745) as an open Megatron-ish
stack, PaLM's Pathways (a different Google systems paper), Alpa, and the 2023–2024
4D-parallel (data / tensor / pipeline / context or sequence) folklore in open pre-training
write-ups. Ring Attention (3 October 2023) is a *context* parallel cousin.

## What this draft does not claim

It does not claim these are the only legal ways to shard a Transformer. It does not describe
any private cluster. It does not treat CUDA kernel names as architecture unless a paper
specifies them (FlashAttention is its own card).

## Sources

- Shoeybi et al., arXiv:1909.08053, published 2019-09-17 (`arxiv-v1`).
- Rajbhandari et al., arXiv:1910.02054, published 2019-10-04 (`arxiv-v1`).
- Black et al., *GPT-NeoX-20B*, arXiv:2204.06745, published 2022-04-14 (`arxiv-v1`).

## Draft debt

- Separate pipeline-parallel GPipe / PipeDream dates in a sequel systems card.
