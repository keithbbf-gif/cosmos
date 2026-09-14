---
voice_check: human
title: "Ashish Vaswani’s group, 2017: attention without the recurrent spine"
slug: attention-and-transformers
kind: essay
era: 2014–2018
tags: [transformer, attention, vaswani, seq2seq, google]
portrait: null
portrait_status: none
---

The 2017 NIPS paper is eight pages plus appendices, and its title is a dare: “Attention Is All You Need.” The authors — Ashish Vaswani, Noam Shazeer, Niki Parmar, Jakob Uszkoreit, Llion Jones, Aidan N. Gomez, Łukasz Kaiser, Illia Polosukhin — were at Google. They proposed the Transformer: no recurrence, no convolution in the main stack, scaled dot-product attention, positional encodings, a training regime that could parallelize where an LSTM could not.

The dare was aimed at a five-year local tradition. Sequence-to-sequence models with attention, from Bahdanau, Cho, and Bengio (2014–2015) and from Luong, Pham, and Manning (2015), had already taught the field that a decoder could look back at a source. Those models still carried a recurrent spine. The 2017 paper cut the spine.

## What the architecture is, without mystique

A Transformer layer mixes information among positions with a weighted sum whose weights come from comparing queries and keys. Multi-head attention does that in several learned subspaces. Feed-forward networks sit between. Residual connections and layer normalization keep the stack trainable. None of this is occult. The occult arrived later, when the same skeleton, scaled, began to complete emails in a convincing tone.

The paper’s experiments were machine translation numbers — BLEU scores, training-time comparisons — not a claim about general intelligence. Google’s subsequent Tensor2Tensor code and the paper’s diagrams did more to spread the design than any manifesto.

## BERT and the encoder year

In 2018, Jacob Devlin, Ming-Wei Chang, Kenton Lee, and Kristina Toutanova posted BERT: bidirectional pretraining with a masked-language objective, then fine-tuning. The NAACL 2019 version became a default citation. For two years, “NLP progress” meant a leaderboard movement measured from a BERT baseline.

OpenAI’s GPT line, beginning earlier with a 2018 transformer language model and then the 2019 GPT-2 report (“Language Models are Unsupervised Multitask Learners”), kept the decoder and the left-to-right bet. The split — bidirectional encoder for classification, autoregressive decoder for generation — is a 2018–2019 fact, not an eternal law. Later models would blur it.

## Priority and the usual mess

Attention mechanisms have a longer bibliography than a single NIPS paper. The Transformer’s contribution is the deletion of recurrence as a requirement for state-of-the-art translation, plus a training story that hardware could love. Credit the eight names on the 2017 author list. Do not invent a lone genius.

By 2020 the architecture was infrastructure. That is the quiet fate of successful papers. They stop being news and start being the air a later surprise breathes.
