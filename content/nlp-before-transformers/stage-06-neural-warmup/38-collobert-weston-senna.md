---
id: nlp-bt-38
title: "Collobert and Weston: almost end-to-end NLP in 2011"
slug: collobert-weston-senna
series: nlp-before-transformers
stage: draft
status: staged
publish: false
novelty: public-record
era: "2008-2011"
topics: [SENNA, Collobert, Weston, multitask]
voice_check: edited
---

# Collobert and Weston: almost end-to-end NLP in 2011

Ronan Collobert and Jason Weston — with later coauthors on the 2011
*JMLR* version, including Léon Bottou, Michael Karlen, Koray
Kavukcuoglu, and Pavel Kuksa — trained a convolutional network to do
several sequence tasks from the same word lookup table: part of
speech, chunking, named-entity recognition, semantic role labeling.
The system that traveled was called SENNA. The attitude that traveled
was more important. Stop handing the model a bag of engineered
features. Hand it windows of words and let the lookup table absorb
the lexicon.

They used a ranking-style objective and a lot of unlabeled text to
pretrain the embeddings. That sentence should sound familiar. It is
the 2010s in prototype: a cheap contrast on raw text, then a
supervised head. Word2Vec would make the first half a lifestyle.
Collobert and Weston already had both halves in one stack.

I remember SENNA as a binary that was fast. Speed was part of the
argument. A neural tagger that could not run was a paper. A neural
tagger that ran on a CPU, in C, without a feature template file, was
a threat to the CRF++ workflow. Threats change citations. People
who had been proud of a gazetteer feature suddenly had to ask
whether a lookup table trained on Wikipedia had eaten the gazetteer.

Was it "end-to-end"? Almost, and the almost matters. They still had
task-specific heads. They still evaluated on the same CoNLL files.
They still benefited from labels someone had paid for. What they
removed was the linguist-hours inside the feature template. That
removal is a political act inside a lab as much as a technical one.
It says: the representation is the model's job now. A lot of
careers were built on the opposite sentence.

The 2008 NIPS paper is the short version. The 2011 *JMLR* paper is
the one I would hand someone. It is also a reminder that "deep
learning for NLP" has a pre-seq2seq chapter. Not everything waited
for Sutskever 2014. Convolution over a window, a max, a linear
layer — that is not a transformer and it is not an LSTM. It is a
third object that worked on tagging before recurrence became
mandatory fashion.

If Word2Vec popularized the embedding file, Collobert and Weston
popularized the idea that the embedding file is the first layer of
the task model, not a separate science. A lot of later "we
fine-tune" talk is that idea with more layers and a prettier
optimizer. The 2011 system already knew the lookup table was not
decoration. It was the place meaning, or something like it, was
allowed to live.
