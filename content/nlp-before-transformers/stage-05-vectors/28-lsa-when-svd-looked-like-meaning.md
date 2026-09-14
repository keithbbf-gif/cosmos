---
id: nlp-bt-28
title: "LSA: when SVD looked like meaning"
slug: lsa-when-svd-looked-like-meaning
series: nlp-before-transformers
stage: draft
status: staged
publish: false
novelty: public-record
era: "1990"
topics: [LSA, LSI, Deerwester, SVD]
---

# LSA: when SVD looked like meaning

Deerwester, Dumais, Furnas, Landauer,
and Harshman, 1990, *Indexing by
Latent Semantic Analysis*. The
practical problem was retrieval.
Query words and document words often
refuse to match. A user says "car."
The paper says "automobile." Exact
term match shrugs.

Latent semantic analysis takes a
term-document matrix, optionally
weighted, and computes a truncated
singular value decomposition. Terms
and documents land in a shared
lower-dimensional space. Inner
products in that space are the new
match. Synonyms can meet even if
they never co-occurred in the same
document, because they hung around
the same latent directions.

I remember the first time this
looked like magic and the first
time it looked like a rotation.
Both impressions are true. SVD
will pull out directions that
explain variance. If your
variance is about topics, you
get something topic-like. If
your variance is about
formatting and a few prolific
authors, you get that instead.
The algorithm does not owe you
semantics. It owes you a
low-rank approximation.

Landauer and Dumais later leaned
into psychological claims — LSA
as a theory of knowledge
acquisition. The IR paper is
enough for this series. It
showed a generation that a
linear algebra primitive could
be a lexical resource. You did
not have to hand-build WordNet
to get a similarity number. You
had to have a matrix and a rank.

The weaknesses are public.
Polysemy gets smashed into one
vector. The space is dense and
a bit greasy; nearest neighbors
can be plausible and still
wrong. Truncation is a
hyperparameter dressed as a
philosophy. None of that
stopped LSA from being the
default "semantic" baseline
for a long time.

When Word2Vec arrived, people
said neural nets had invented
distributional meaning. A
kinder sentence: prediction
trained a cheaper, incrementally
updatable cousin of the same
matrix factorization family.
Levy and Goldberg would later
make that kinship explicit in
public papers. The 1990 SVD
is the older relative at the
table, slightly formal, still
owed a plate.
