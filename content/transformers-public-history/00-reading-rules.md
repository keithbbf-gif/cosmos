---
id: tph-00
slug: reading-rules
title: "Reading rules: first public appearance, not lore"
status: staged-draft
series: transformers-public-history
era: method
first_public: "2017-06-12"
date_kind: series-start
arxiv: ""
venue_later: ""
novelty_lane: public-prior-art-only
private_systems: excluded
voice_check: edited
voice_check_date: 2026-09-14
depends_on: []
leads_to: ["tph-01"]
---

# Reading rules: first public appearance, not lore

**Status:** staged draft. Not a publication.
**Lane:** public transformer architecture history.
**First public appearance of the series object:** 12 June 2017 (arXiv v1 of *Attention Is All You Need*).
**Primary source:** this card states method; later cards cite artifacts.

## The claim

A history of transformer architecture that uses conference years, press-release metaphors, or
memory will silently reorder the field and then invent mechanisms to fill the gaps. This series
treats **the first public artifact** as the event: an arXiv v1 stamp, an official blog or model
card, a release post, or a readable configuration file. Venue years, invited talks, and
secondary surveys are later decorations.

The series starts at 12 June 2017 because that is when Vaswani, Shazeer, Parmar, Uszkoreit,
Jones, Gomez, Kaiser, and Polosukhin first put a recurrence-free, convolution-free
encoder–decoder stacked on multi-head scaled dot-product attention in public. Earlier attention
(Bahdanau 2014; Luong 2015) is predecessor context, not the start of *this* architecture.

## What the method specified

Four rules, used on every later card:

1. **Date the first public appearance.** For a paper that is `date_kind: arxiv-v1`. The export
   API `published` field is the v1 timestamp; that is what these drafts used. A later pass should
   still open the abstract page and read the submission-history block, because that is the
   checkable object. Camera-ready and journal versions can sit months later and must not steal
   the clock.
2. **Name the kind of date.** An OpenAI blog (GPT-2, 14 February 2019), a Mistral announcement
   (7B, 27 September 2023), and an arXiv v1 (Mistral 7B paper, 10 October 2023) are three
   different evidence classes. The announcement can precede the paper. The paper can precede
   production. Neither is "the architecture appearing in a leaderboard screenshot."
3. **Refuse reconstructions of withheld blocks.** The GPT-4 technical report (15 March 2023,
   arXiv:2303.08774) is explicit about what it does not disclose. A draft that then "fills in"
   layer counts, routing, or multimodal fusion from rumor has left this series.
4. **Keep invention and adoption on separate clocks.** Multi-query attention is 6 November 2019
   (Shazeer, arXiv:1911.02150). Grouped-query attention is 22 May 2023 (Ainslie et al.,
   arXiv:2305.13245). Sliding-window-plus-global tokens is 10 April 2020 (Longformer). The 2023
   production wave reused 2019–2021 mechanisms because context bills finally made them
   mandatory, not because the mechanisms were new.

## What this method displaced

The default popular timeline — "Transformer 2017, BERT 2018, GPT-3 2020, ChatGPT 2022, Llama
2023" — is not false so much as *lossy*. It hides Shaw relative positions (6 March 2018), the
encoder-only / decoder-only split, the 2019–2021 sparsity and linear-attention papers, the
systems stack (Megatron, ZeRO), and the fact that FlashAttention (27 May 2022) changed the
baseline that every approximation had to beat.

It also hides a category error: **a context-window number is not a measured usable context.**
A sliding-window stack's "receptive field" (window × depth) is an upper bound on influence
through lossy hops. Cards in this series are required to say so when a vendor number is an
upper bound.

## Immediate lineage

`tph-01` is the 2017 paper. `tph-02` through `tph-05` stay inside that paper until the
pieces are named well enough to watch them mutate. `tph-07` and `tph-08` are the 2018 fork.
Everything after is a response to cost, length, memory, data, or alignment — still of the
2017 block or a stated alternative.

## What this draft does not claim

This card is not a complete historiography of sequence models. It does not date Bahdanau or
Luong as transformer events. It does not treat "attention" in neuroscience, or the 1990s
fast-weight literature, as the 2017 architecture. Those belong in a longer predecessor pack.

It does not claim the export API is a substitute for reading a PDF. Numbers in later cards
(layer counts, BLEU, cache reductions) are taken from the cited artifact and marked when they
are author-reported rather than independently measured.

It does not claim this pack is exhaustive. Forty-plus drafts is a spine, not a census. Routing
Transformer, Sinkhorn, Nyströmformer, FlashDecoding, Medusa, EAGLE, and most vision-only
refinements after Swin are owed and absent.

## Sources

- Vaswani et al., *Attention Is All You Need*, arXiv:1706.03762, published 2017-06-12 (`arxiv-v1`).
- Devlin et al., *BERT*, arXiv:1810.04805, published 2018-10-11 (`arxiv-v1`).
- Shazeer, *Fast Transformer Decoding*, arXiv:1911.02150, published 2019-11-06 (`arxiv-v1`).
- Beltagy, Peters, Cohan, *Longformer*, arXiv:2004.05150, published 2020-04-10 (`arxiv-v1`).
- Dao et al., *FlashAttention*, arXiv:2205.14135, published 2022-05-27 (`arxiv-v1`).
- OpenAI, *GPT-4 Technical Report*, arXiv:2303.08774, published 2023-03-15 (`arxiv-v1`).
- Ainslie et al., *GQA*, arXiv:2305.13245, published 2023-05-22 (`arxiv-v1`).

## Draft debt

- Open each later card's abstract page and photograph the submission-history block.
- Add a predecessor card (Bahdanau / Luong / ConvS2S learned positions) if a sequel pack is
  opened. That pack would still be public history; it is out of scope here only because the
  assignment starts at the 2017 paper.
