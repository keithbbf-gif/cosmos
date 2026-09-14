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
---

# Collobert and Weston: almost end-to-end NLP in 2011

Ronan Collobert and Jason
Weston (with later
coauthors on the JMLR 2011
version) trained a
convolutional network to
do several sequence tasks
from the same word lookup
table: POS, chunking, NER,
SRL. The system that
traveled was called SENNA.
The attitude that traveled
was more important. Stop
handing the model a bag of
engineered features. Hand
it windows of words and
let the lookup table
absorb the lexicon.

They used a ranking-style
objective and a lot of
unlabeled text to pretrain
the embeddings. That
sentence should sound
familiar. It is the
2010s in prototype.

I remember SENNA as a
binary that was fast. Speed
was part of the argument.
A neural tagger that could
not run was a paper. A
neural tagger that ran on
a CPU was a threat to CRF
templates. Threats change
citations.

Was it "end-to-end"? Almost,
and the almost matters.
They still had task
heads. They still
evaluated on the same
CoNLL files. They still
benefited from task
labels that someone had
paid for. What they
removed was the
linguist-hours inside
the feature template.
That removal is a
political act inside a
lab as much as a
technical one.

The 2011 JMLR paper is
more complete than the
2008 NIPS one and is
the one I would hand
someone. It is also a
reminder that "deep
learning for NLP" has a
pre-seq2seq chapter.
Not everything waited
for Sutskever 2014.

If Word2Vec popularized
the embedding file,
Collobert and Weston
popularized the idea
that the embedding file
is the first layer of
the task model, not a
separate science. A lot
of later "we fine-tune"
talk is that idea with
more layers.
