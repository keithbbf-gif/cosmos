---
id: "tph-14"
slug: "roberta-2019"
title: "RoBERTa: the BERT recipe was the architecture (26 July 2019)"
status: "staged-draft"
series: "transformers-public-history"
era: "2019-refine"
first_public: "2019-07-26"
date_kind: "arxiv-v1"
arxiv: "1907.11692"
venue_later: ""
novelty_lane: "public-prior-art-only"
private_systems: "excluded"
depends_on: ["tph-08"]
leads_to: ["tph-15", "tph-16"]
---

# RoBERTa: the BERT recipe was the architecture (26 July 2019)

**Status:** staged draft. Not a publication.
**Lane:** public transformer architecture history.
**First public appearance:** 26 July 2019 (`arxiv-v1`).
**Primary source:** Liu, Ott, Goyal, Du, Joshi, Chen, Levy, Lewis, Zettlemoyer, Stoyanov,
*RoBERTa: A Robustly Optimized BERT Pretraining Approach*, arXiv:1907.11692.

## The claim

RoBERTa is deliberately **not** a new attention primitive. It is a public demonstration that
BERT's published recipe under-trained the same block: more data, larger batches, longer
training, dynamic masking, no next-sentence prediction, and a different byte-level BPE.
Architecture history includes these papers because they show when "a new model" was actually
**compute and data around an unchanged stack**.

Without this card, T5 and GPT-3's scale stories look like they invented "more data." They did
not. RoBERTa made the point at encoder-only size in 2019.

## What the artifact specified

Same Transformer encoder as BERT. Changes the paper commits to:

- train longer, bigger batches, more data (they include CC-News, OpenWebText, Stories on top
  of BERT's books+wiki mix);
- **dynamic masking** (new mask pattern per sequence presentation) instead of BERT's once-and-
  cached static mask;
- drop NSP;
- longer sequences in a second training phase;
- byte-level BPE like GPT-2.

They match or exceed XLNet on several GLUE/SQuAD numbers at comparable or specified sizes.
Author-reported 2019 figures.

## What it displaced

NSP as a required BERT ingredient, and the folklore that BERT-Large was "fully trained." It
also displaced a certain kind of architecture paper that changes a block, under-trains the
baseline, and declares victory. RoBERTa is the public control experiment.

## Immediate lineage

Every later "we just trained BERT better" model (including some 2024 encoder revivals) sits
here. T5's ablation culture and the Kaplan/Chinchilla scaling papers are the scale-law
continuation. ALBERT goes the other way: **fewer** parameters, same encoder family.

## What this draft does not claim

It does not claim data recipe is the only architecture. Attention, position, and topology
still change outcomes. It claims the converse: **not every named model is a new architecture.**
This series will keep saying that (InstructGPT, Vicuna, Alpaca).

## Sources

- Liu et al., arXiv:1907.11692, published 2019-07-26 (`arxiv-v1`).
- Devlin et al., arXiv:1810.04805, published 2018-10-11 (`arxiv-v1`).
- Yang et al., arXiv:1906.08237, published 2019-06-19 (`arxiv-v1`).

## Draft debt

- Quote the exact corpus sizes from Table 1 of the PDF.
