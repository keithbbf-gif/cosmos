---
id: "tph-07"
slug: "gpt1-decoder-only-2018"
title: "GPT-1: decoder-only generative pre-training (11 June 2018)"
status: "staged-draft"
series: "transformers-public-history"
era: "2018-fork"
first_public: "2018-06-11"
date_kind: "official-pdf"
arxiv: ""
venue_later: "OpenAI technical report PDF (not an arXiv v1)"
novelty_lane: "public-prior-art-only"
private_systems: "excluded"
depends_on: ["tph-05"]
leads_to: ["tph-10", "tph-09"]
---

# GPT-1: decoder-only generative pre-training (11 June 2018)

**Status:** staged draft. Not a publication.
**Lane:** public transformer architecture history.
**First public appearance:** 11 June 2018 (`official-pdf`).
**Primary source:** Radford, Narasimhan, Salimans, Sutskever, *Improving Language Understanding
by Generative Pre-Training*, OpenAI.

## The claim

One year after the 2017 encoder–decoder paper, OpenAI published a **decoder-only** Transformer
trained with a causal language-modeling objective on unlabeled text, then fine-tuned with extra
task heads. The public object is a PDF on OpenAI's site, not an arXiv v1. That matters for date
kind: 11 June 2018 is an official report date, not a submission-history stamp.

The architectural deletion is the point. There is no encoder and no cross-attention. Conditioning
for downstream tasks is a **prefix** plus a linear head, not a second stack reading a source
memory. This is the topology that GPT-2, GPT-3, and the 2023 open-weight wave keep.

## What the artifact specified

The report describes a 12-layer decoder, \(d_{\mathrm{model}} = 768\), 12 heads, 117M parameters,
trained on BooksCorpus. Tokenization is BPE. Positions are learned absolute embeddings. Attention
is masked so token \(t\) sees only \(\le t\). Fine-tuning adds start/delimiter tokens and a
task-specific linear layer; the pretrained weights stay.

The paper's intellectual claim is as much about **the two-stage recipe** (generative pre-train,
discriminative fine-tune) as about the block. ULMFiT (Howard and Ruder, January 2018) and ELMo
(Peters et al., 15 February 2018, arXiv:1802.05365) had already made "pretrain a language model,
then specialize" public, but they were LSTM stacks. GPT-1 is that recipe on the 2017 decoder
half.

Numbers in the report (GLUE, SciTail, RACE, and the rest of their table) are author-reported
2018 fine-tune scores. They are not a 2026 re-eval and they are not why this card exists. The
card exists because **decoder-only + causal LM + then a head** becomes the default LLM shape.

## What it displaced

For generation, the 2017 encoder–decoder is optional. If your "source" is the previous tokens,
self-attention with a causal mask is enough. That sounds obvious in 2026. In mid-2018 the
public pretrained Transformer that people cited next was about to be BERT, which went the other
way.

GPT-1 did not displace BERT. The two papers, ten weeks apart in the other order from how
slides tell it (GPT-1 June, BERT October), split the architecture into two research programs
that barely shared objectives for three years.

## Immediate lineage

GPT-2 (14 February 2019) scales the same topology and deletes the fine-tune-head story in favor
of zero-shot task specification in the prompt. GPT-3 (28 May 2020) scales it again and names
in-context learning. LLaMA (27 February 2023) is still this topology, with later public
replacements for PE, norm, and FFN.

Encoder–decoder does not die. T5 and BART reopen it in 2019. But the *causal* line from this
PDF is the one that later hosts ChatGPT-class products — whose own blocks, after GPT-3, are
often unpublished.

## What this draft does not claim

It does not treat the 117M figure as sacred; it is what the report stated. It does not claim
OpenAI invented causal language modeling. It does not back-date GPT-2 or GPT-3 architecture
secrets into this PDF. It does not analogize this report to any private system.

Because there is no arXiv v1, a later pass should keep the PDF URL and a content hash if the
host ever moves the file.

## Sources

- Radford, Narasimhan, Salimans, Sutskever, *Improving Language Understanding by Generative
  Pre-Training*, OpenAI, 2018-06-11 (`official-pdf`).
  https://cdn.openai.com/research-covers/language-unsupervised/language_understanding_paper.pdf
- Peters et al., *Deep contextualized word representations*, arXiv:1802.05365, published
  2018-02-15 (`arxiv-v1`) — ELMo, LSTM predecessor recipe.
- Devlin et al., arXiv:1810.04805, published 2018-10-11 (`arxiv-v1`).

## Draft debt

- Confirm page-level layer / width / head counts against the PDF, not secondary blogs.
- Add ULMFiT (arXiv:1801.06146) as a dated recipe predecessor if the sequel pack opens.
