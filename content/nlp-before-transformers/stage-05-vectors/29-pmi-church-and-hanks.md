---
id: nlp-bt-29
title: "Church and Hanks: PMI and the collocation as a number"
slug: pmi-church-and-hanks
series: nlp-before-transformers
stage: draft
status: staged
publish: false
novelty: public-record
era: "1990"
topics: [PMI, collocation, Church, Hanks]
---

# Church and Hanks: PMI and the collocation as a number

Kenneth Church and Patrick Hanks,
1990, "Word Association Norms,
Mutual Information, and
Lexicography." They took a simple
information-theoretic score —
how much more do two words happen
together than chance would allow —
and used it as a lexicographer's
tool. Pointwise mutual
information. A number for
"this pair is not an accident."

The score has a known vice. It
loves rare events. Two words
that appear together twice in
a huge corpus can look like
destiny. People later used
positive PMI, count thresholds,
and simple discounting to keep
the vice in a box. The original
paper is still the one that made
association computable without a
committee.

I used PMI tables the way I used
WordNet: as a cheap oracle. Is
"strong tea" a collocation?
The number says yes. "Powerful
tea" says no. Firth would have
liked the example; he used tea
himself. The computational
version lets you run the
question over a newswire dump
instead of an armchair.

Church's broader 1980s and 1990s
presence — tagging, parsing
adjacent work, the sense that
a UNIX pipeline could be a
linguistic instrument — belongs
with this paper. PMI is a
one-liner. The culture is "we
will measure the association
and then argue."

Vector people absorbed PMI
directly. A word-context matrix
of PMI values, sometimes
shifted, is a strong embedding
before anyone says neural. Levy,
Goldberg, and Dagan showed in
the mid-2010s that a lot of
Word2Vec's glow is this matrix
plus factorization. That result
did not make Word2Vec smaller
as an event. It made 1990
larger as an ancestor.

If you teach only one
pre-neural semantic score,
teach PMI and then immediately
teach its rare-event mania.
Otherwise students will ship
a thesaurus that thinks every
typo pair is profound.
