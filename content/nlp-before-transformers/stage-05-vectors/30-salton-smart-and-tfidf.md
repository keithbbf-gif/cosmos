---
id: nlp-bt-30
title: "Salton's SMART: the vector space that search actually used"
slug: salton-smart-and-tfidf
series: nlp-before-transformers
stage: draft
status: staged
publish: false
novelty: public-record
era: "1971-1988"
topics: [Salton, SMART, TF-IDF, vector-space]
---

# Salton's SMART: the vector space that search actually used

Before embeddings were a lifestyle,
Gerald Salton's SMART system
treated documents and queries as
vectors and ranked by cosine
similarity. The work runs from
the 1960s through the 1980s. TF-IDF
weighting — term frequency times
inverse document frequency — is
the piece that escaped into every
stack overflow answer.

IDF is the taste. A word that
appears in every document does
not help you choose. A word that
appears in two documents might.
The formula has variants
(logarithms, smoothed IDF,
Okapi BM25 as a later, ruder
cousin). The attitude is stable.
Not every token deserves the
same shout.

I keep Salton in the vector
stage, not only in the IR
annex, because a lot of people
who think they are doing NLP
are doing SMART with extra
steps. A linear classifier on
bag-of-words is a vector space
model with a learned direction.
A dense embedding average is
a vector space model with a
different basis. The cosine
did not get invented in 2013.

SMART also taught evaluation
hygiene: test collections,
precision and recall, the idea
that a retrieval method is a
public claim. Cranfield, later
TREC, made that claim
enforceable. NLP borrowed the
habit when it finally got tired
of demo transcripts.

BM25 (Robertson and colleagues)
is the 1990s refinement I still
reach for when a neural ranker
is too much theater. It is not
pre-transformer in the narrow
sense of this series' last
chapters, but it is the grown
form of Salton's object. If
your history of "vectors for
language" skips BM25 and jumps
to word2vec, you skipped the
part that sat in production
search for years.

The human remaining point:
weighting is ideology. TF-IDF
says rare is informative. That
is often right for topical
search and wrong for function
words you actually needed. A
good system lets you see the
weights. SMART did. A pile of
dense vectors often does not.
