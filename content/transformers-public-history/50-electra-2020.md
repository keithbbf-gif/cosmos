---
id: "tph-50"
slug: "electra-2020"
title: "ELECTRA: replaced-token detection (23 March 2020)"
status: "staged-draft"
series: "transformers-public-history"
era: "2020-long-scale"
first_public: "2020-03-23"
date_kind: "arxiv-v1"
arxiv: "2003.10555"
venue_later: "ICLR 2020"
novelty_lane: "public-prior-art-only"
private_systems: "excluded"
depends_on: ["tph-08", "tph-14"]
leads_to: ["tph-16"]
---

# ELECTRA: replaced-token detection (23 March 2020)

**Status:** staged draft. Not a publication.
**Lane:** public transformer architecture history.
**First public appearance:** 23 March 2020 (`arxiv-v1`).
**Primary source:** Clark, Luong, Le, Manning, *ELECTRA: Pre-training Text Encoders as
Discriminators Rather Than Generators*, arXiv:2003.10555.

## The claim

ELECTRA keeps a BERT-class **encoder** and changes the pre-training *game*. A small
generator (usually a MLM) proposes replacements for masked tokens; a discriminator sees
the whole corrupted sequence and must detect, at every position, whether the token is
original or replaced. Every token provides a loss signal, not only the 15% BERT masks.

This is an objective-and-compute architecture paper, in the RoBERTa sense: the attention
block is familiar; the **sample efficiency** of the encoder is not.

ICLR 2020 is the venue. The public date is 23 March 2020.

## What the artifact specified

Two Transformer encoders (generator smaller than discriminator in the type-case), weight
tying options, a replaced-token-detection loss, and GLUE/SQuAD tables at small, base, and
large compute budgets. They emphasize that an ELECTRA-Small trained on one GPU is a
serious baseline — a different prestige axis from GPT-3's 175B, four months later.

The discriminator cannot be used as a language model in the GPT sense. Like BERT, it is an
encoder. Generation still wants a decoder or a seq2seq (T5/BART that same year).

## What it displaced

The assumption that encoder pre-training *had* to be MLM. After ELECTRA, RTD is a named
alternative, and later DeBERTa / other encoder papers have to say which game they play.
It did not displace MLM as the default citation; BERT's name stuck.

## Immediate lineage

DeBERTa (He et al., later in 2020) combines a different attention/position story with
encoder pre-training and should not be filed as "ELECTRA-2." CoCO-LM and other
efficiency-pretrain papers sit here. The 2024–2025 "ModernBERT" style revivals are recipe
papers on this encoder line.

## What this draft does not claim

It does not claim RTD is always cheaper at 2024 scale. It does not treat decoder-only
LLMs as secret ELECTRAs. ICLR 2020 must not replace 23 March 2020.

## Sources

- Clark, Luong, Le, Manning, arXiv:2003.10555, published 2020-03-23 (`arxiv-v1`).
- Devlin et al., arXiv:1810.04805, published 2018-10-11 (`arxiv-v1`).
- Liu et al., arXiv:1907.11692, published 2019-07-26 (`arxiv-v1`).

## Draft debt

- Quote the small/base/large compute table from the PDF.
