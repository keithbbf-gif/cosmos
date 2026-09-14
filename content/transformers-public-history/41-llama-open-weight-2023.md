---
id: "tph-41"
slug: "llama-open-weight-2023"
title: "LLaMA: the open-weight decoder assembly (27 February 2023)"
status: "staged-draft"
series: "transformers-public-history"
era: "2023-open-serve"
first_public: "2023-02-27"
date_kind: "arxiv-v1"
arxiv: "2302.13971"
venue_later: "Llama 2 arXiv:2307.09288 on 2023-07-18"
novelty_lane: "public-prior-art-only"
private_systems: "excluded"
voice_check: "edited"
voice_check_date: "2026-09-14"
depends_on: ["tph-32", "tph-30", "tph-35"]
leads_to: ["tph-42", "tph-43"]
---

# LLaMA: the open-weight decoder assembly (27 February 2023)

**Status:** staged draft. Not a publication.
**Lane:** public transformer architecture history.
**First public appearance:** 27 February 2023 (`arxiv-v1`).
**Primary source:** Touvron et al., *LLaMA: Open and Efficient Foundation Language Models*,
arXiv:2302.13971.

## The claim

LLaMA is not a new attention formula. It is the **public assembly** that most 2023–2024
open decoders copy: Pre-LN, RMSNorm, SwiGLU, RoPE, no biases on many linear layers, a
tokenizer in the BPE family, and sizes 7B / 13B / 33B / 65B trained on more tokens than a
2020 Kaplan-operational reader expected. The architecture event is the *combination plus
weights that other people could actually run* (under the paper's license terms of that
moment).

Llama 2 (18 July 2023, arXiv:2307.09288) adds a longer context, a different data mix, a
published RLHF story, and **GQA on 70B**. Do not collapse LLaMA-1 and Llama 2. The Llama 3
herd report (31 July 2024, arXiv:2407.21783) is a third artifact.

## What the artifact specified

Section 2 of the 27 February paper lists the block choices with citations (RMSNorm, SwiGLU,
RoPE). Context length 2048 in LLaMA-1. Training token counts per size are tabled
(author-reported). The models are dense, not MoE.

What spread in the wild (Alpaca 13 March 2023 blog; Vicuna 30 March 2023 blog) is
**instruction wrapping** of these weights, not a new block. Those blogs are alignment /
data events (`tph-34`'s grandchildren).

## What it displaced

The practical monopoly of API-only dense decoders for people who wanted to fine-tune. OPT
(2 May 2022) and BLOOM (9 November 2022) were already public weights; LLaMA is the one
whose quality/size points became the default starting checkpoint. That is adoption, and it
is real.

## Immediate lineage

Llama 2, Llama 3, Code Llama, the Mistral 7B "we are a better 7B" announcement, and an
entire PEFT ecosystem. GQA belongs to `tph-42` and to Llama 2 70B, not to LLaMA-1.

## What this draft does not claim

It does not claim Meta invented RMSNorm, RoPE, or SwiGLU. It does not treat leaked or
unofficial weight dumps as this paper. License drama is not architecture.

## Sources

- Touvron et al., arXiv:2302.13971, published 2023-02-27 (`arxiv-v1`).
- Touvron et al., *Llama 2*, arXiv:2307.09288, published 2023-07-18 (`arxiv-v1`).
- Zhang and Sennrich, arXiv:1910.07467; Shazeer, arXiv:2002.05202; Su et al.,
  arXiv:2104.09864.

## Draft debt

- Quote LLaMA-1 token-count table exactly.
