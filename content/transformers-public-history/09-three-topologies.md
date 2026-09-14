---
id: "tph-09"
slug: "three-topologies"
title: "Three topologies: encoder-only, decoder-only, encoder–decoder"
status: "staged-draft"
series: "transformers-public-history"
era: "2018-fork"
first_public: "2018-10-11"
date_kind: "taxonomy-after-bert"
arxiv: ""
venue_later: "Taxonomy card; dates belong to the three source papers"
novelty_lane: "public-prior-art-only"
private_systems: "excluded"
voice_check: "edited"
voice_check_date: "2026-09-14"
depends_on: ["tph-01", "tph-07", "tph-08"]
leads_to: ["tph-16", "tph-23"]
---

# Three topologies: encoder-only, decoder-only, encoder–decoder

**Status:** staged draft. Not a publication.
**Lane:** public transformer architecture history.
**First public appearance:** 11 October 2018 as a completed fork (`taxonomy-after-bert`).
**Primary source:** the three papers already dated in `tph-01`, `tph-07`, `tph-08`.

## The claim

By 11 October 2018 the public record contains three incompatible ways to stack the 2017
layer, and the field will spend years using the same word for all three.

| Topology | Attention pattern | Typical objective | Type case | First public |
|---|---|---|---|---|
| Encoder–decoder | self + masked self + cross | seq2seq (later T5 span corruption) | Vaswani et al. | 2017-06-12 |
| Decoder-only | masked (causal) self | next-token LM | GPT-1 | 2018-06-11 |
| Encoder-only | bidirectional self | MLM / replaced-token / etc. | BERT | 2018-10-11 |

This card exists so later drafts can say **which columns they keep**. A "transformer LLM" in
2024 is almost always column two. A "transformer for embeddings" is often column three. A
"transformer for translation or any-to-any text" is often column one. Calling all of them
"BERT-like" is a category error that this series refuses.

## What the artifact specified

No new paper is introduced here. The specification is the **compatibility matrix**:

- Causal decoders cannot use BERT's `[MASK]` recipe without becoming something else
  (span corruption on a decoder is possible, and UL2 later says so, but that is a 2022 paper).
- Encoder-only stacks do not produce tokens auto-regressively unless someone adds a decode
  procedure the original paper did not train.
- Cross-attention is not a luxury. It is the only 2017 mechanism that lets a target sequence
  read a source sequence without stuffing the source into the same causal stream. Prefix-LM
  and packed "source then target" decoders are later workarounds, public in T5 and in many
  2023 instruction models, and they are not free (the source occupies context).

Prefix language models (unmasked bidirectional prefix, causal target) sit between columns.
T5 discusses the option; UniLM and later prefix-LM papers make it a first-class object. This
card treats prefix-LM as a **hybrid attention mask**, not a fourth topology, until a sequel
draft is opened for it.

## What it displaced

The idea that "the Transformer" is a single diagram. After 2018, a paper that does not say
which topology it uses is underspecified. So is a vendor report that says "transformer-based"
and then withholds the mask.

## Immediate lineage

- Column one: T5 (2019-10-23), BART (2019-10-29), Flan-T5 (2022-10-20).
- Column two: GPT-2, GPT-3, Gopher, Chinchilla, PaLM, LLaMA, Mistral, Mixtral (decoder + MoE).
- Column three: RoBERTa, ALBERT, ELECTRA, DeBERTa, ModernBERT-class late encoders.

Vision will copy the encoder column first (ViT, 22 October 2020) and only later grow
decoder-only and encoder–decoder image generators (DiT, 19 December 2022).

## What this draft does not claim

It does not claim one topology won on merit alone. Decode-time KV-cache economics, teacher
forcing, and the 2020–2022 scale-up all favored column two for *generation products*. Retrieval
and classification products still live in column three. This is not a ranking.

It does not assign unpublished closed models to a column. GPT-4's report does not give the
diagram.

## Sources

- Vaswani et al., arXiv:1706.03762, published 2017-06-12 (`arxiv-v1`).
- Radford et al., GPT-1 official PDF, 2018-06-11 (`official-pdf`).
- Devlin et al., arXiv:1810.04805, published 2018-10-11 (`arxiv-v1`).
- Raffel et al., arXiv:1910.10683, published 2019-10-23 (`arxiv-v1`).

## Draft debt

- Open a dedicated prefix-LM / UL2 card rather than leaving the hybrid in a paragraph.
