---
id: "tph-08"
slug: "bert-encoder-only-2018"
title: "BERT: bidirectional encoder pre-training (11 October 2018)"
status: "staged-draft"
series: "transformers-public-history"
era: "2018-fork"
first_public: "2018-10-11"
date_kind: "arxiv-v1"
arxiv: "1810.04805"
venue_later: "NAACL 2019"
novelty_lane: "public-prior-art-only"
private_systems: "excluded"
depends_on: ["tph-05"]
leads_to: ["tph-14", "tph-15", "tph-09"]
---

# BERT: bidirectional encoder pre-training (11 October 2018)

**Status:** staged draft. Not a publication.
**Lane:** public transformer architecture history.
**First public appearance:** 11 October 2018 (`arxiv-v1`).
**Primary source:** Devlin, Chang, Lee, Toutanova, *BERT: Pre-training of Deep Bidirectional
Transformers for Language Understanding*, arXiv:1810.04805.

## The claim

BERT takes the **encoder** half of Figure 1, drops the decoder, and pre-trains with a masked
language-model objective so every position can attend to every other position in both
directions. A second objective, next-sentence prediction, tries to give the `[CLS]` token a
pair-level signal. Fine-tuning then attaches small task heads. The public date is 11 October
2018, not NAACL 2019.

This is the other 2018 fork. Where GPT-1 is causal and generative, BERT is bidirectional and
discriminative. Both are "transformers." They are not the same architecture in use.

## What the artifact specified

Two published sizes:

- **BERT-Base:** \(L = 12\), \(H = 768\), \(A = 12\), 110M parameters.
- **BERT-Large:** \(L = 24\), \(H = 1024\), \(A = 16\), 340M parameters.

WordPiece vocabulary of 30,000. Learned absolute position embeddings, **maximum length 512**.
Input is the sum of token, segment, and position embeddings. Masked LM replaces 15% of tokens;
of those, 80% become `[MASK]`, 10% a random token, 10% left unchanged. Training data is
BooksCorpus plus English Wikipedia.

Those details are why later "BERT refinements" have somewhere to attach. RoBERTa will delete
NSP and change the data and batch recipe. ALBERT will factor embeddings and share layers.
ELECTRA will replace MLM with a discriminator. None of that is in the 2018 paper; the 2018
paper is the thing they refine.

Google later used BERT in Search (officially discussed in 2019). That is a deployment event,
not an architecture event, and it does not change the 11 October stamp.

## What it displaced

ELMo-style concatenated LSTM states as the default contextual encoder, and GPT-1-style
unidirectional pre-training as the default *understanding* recipe. The paper's own comparisons
are to those systems on GLUE, SQuAD, and SWAG. The famous sentence is that unidirectional
language models are the wrong pre-training objective for token-level bidirectional tasks.

It did not displace causal decoders for generation. BERT is a poor language model in the GPT
sense because MLM is not next-token prediction and because there is no auto-regressive stack.

## Immediate lineage

RoBERTa (26 July 2019), ALBERT (26 September 2019), ELECTRA (23 March 2020), DeBERTa (later),
and a forest of domain BERTs. SpanBERT, TinyBERT, DistilBERT are compression and objective
variants. Sentence-BERT is a pooling/training change, not a new attention primitive.

T5 will argue that even BERT-style tasks can be written as text-to-text and trained on an
encoder–decoder. That is 2019's unification move, not BERT's.

## What this draft does not claim

It does not claim NSP was a good idea (RoBERTa publicly argues it was not). It does not claim
the 512-token cap is fundamental; it is a learned-absolute-position plus memory choice. It
does not treat later encoder-only industrial models as having unpublished BERT deviations
unless a paper says so.

NAACL 2019 is the venue, not the appearance.

## Sources

- Devlin, Chang, Lee, Toutanova, arXiv:1810.04805, published 2018-10-11 (`arxiv-v1`).
- Radford et al., GPT-1 official PDF, 2018-06-11 (`official-pdf`).
- Liu et al., *RoBERTa*, arXiv:1907.11692, published 2019-07-26 (`arxiv-v1`).

## Draft debt

- Quote the exact MLM 80/10/10 paragraph from the PDF.
- Add the Search-deployment official post as a dated *adoption* footnote, not a first-public
  architecture date.
