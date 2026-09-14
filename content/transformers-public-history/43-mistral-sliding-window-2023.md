---
id: "tph-43"
slug: "mistral-sliding-window-2023"
title: "Mistral 7B: sliding window ships in a causal LM (27 September 2023)"
status: "staged-draft"
series: "transformers-public-history"
era: "2023-open-serve"
first_public: "2023-09-27"
date_kind: "official-blog-then-arxiv"
arxiv: "2310.06825"
venue_later: "arXiv v1 2023-10-10; mistral.ai announcement 2023-09-27"
novelty_lane: "public-prior-art-only"
private_systems: "excluded"
depends_on: ["tph-20", "tph-42"]
leads_to: ["tph-45", "tph-48"]
---

# Mistral 7B: sliding window ships in a causal LM (27 September 2023)

**Status:** staged draft. Not a publication.
**Lane:** public transformer architecture history.
**First public appearance:** 27 September 2023 (`official-blog`); paper 10 October 2023
(`arxiv-v1`).
**Primary source:** Jiang et al., *Mistral 7B*, arXiv:2310.06825; Mistral announcement
post.

## The claim

Mistral 7B is the widely noticed **ship** of sliding-window attention in a modern
decoder-only LM, plus GQA, plus a rolling-buffer KV cache the announcement describes as
cutting cache memory at long generations. The window in the paper/announcement type-case
is **4096** across 32 layers. A "131k receptive field" style figure (window × depth) is an
**upper bound on possible influence through 32 lossy hops**, not a measured usable context.

Sliding windows as a public mechanism are Longformer, 10 April 2020. This card is adoption
in the causal-LM product class.

## What the artifact specified

Dense 7B-class decoder, SwiGLU / RoPE / RMSNorm-class modern stack (see paper), GQA,
sliding window with rolling cache. The 27 September post is what most of the field felt;
the 10 October paper is what a hostile check should quote.

Two days later (29 September 2023) StreamingLLM publishes **attention sinks**. The
announcement and that paper sit on the same weekend and should not be merged: one ships a
windowed cache; one explains a softmax mass problem at the start of the sequence.

## What it displaced

The assumption that a "good 7B" had to be a LLaMA fine-tune of a dense full-attention 2k
or 4k window. After Mistral, small dense models with a 32k *marketing* context and a 4k
*window* are a normal design. Readers must keep those two numbers separate.

## Immediate lineage

Mixtral (MoE on a similar modern block), Gemma 2 interleaved local/global (31 July 2024
arXiv), and later configs that alternate sliding and full layers (Gemma 2/3, gpt-oss
cards in 2025). Those are hybridizations of this ship plus Longformer's old idea.

## What this draft does not claim

It does not claim Mistral invented windows. It does not treat later Mistral Large
unpublished blocks as 7B. Author-reported evals in the 7B paper are not re-run here.

## Sources

- Mistral, *Announcing Mistral 7B*, 2023-09-27 (`official-blog`).
- Jiang et al., arXiv:2310.06825, published 2023-10-10 (`arxiv-v1`).
- Beltagy et al., arXiv:2004.05150, published 2020-04-10 (`arxiv-v1`).
- Xiao et al., arXiv:2309.17453, published 2023-09-29 (`arxiv-v1`).

## Draft debt

- Quote the announcement's exact cache-reduction sentence.
