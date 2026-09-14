---
id: nlp-bt-47
title: "Collins and Charniak: the last great statistical parsers"
slug: collins-charniak-statistical-parsers
series: nlp-before-transformers
stage: draft
status: staged
publish: false
novelty: public-record
era: "1996-2000"
topics: [Collins, Charniak, PCFG, parsing]
---

# Collins and Charniak: the last great statistical parsers

Once the Penn Treebank
existed, parsing became
a likelihood. Eugene
Charniak and Michael
Collins, in different
styles through the
late 1990s, built
parsers that treated
trees as things you
could score with
carefully factored
probabilities:
head-word
dependencies,
lexicalized PCFGs,
features that a
pure CFG would have
called cheating.

Lexicalization is the
heart. A vanilla PCFG
says an NP can be DT
NN and does not care
which NN. That is why
vanilla PCFGs are
mediocre on real
text. A lexicalized
model says this NP
is headed by
"company" or
"stock" and the
attachments change.
The grammar wakes
up. The parameter
space also explodes,
so smoothing — that
word again — becomes
the craft.

I have a fondness
for these parsers
that is not
nostalgia. They
made linguistic
structure compatible
with the speech
people's religion
of likelihood
without giving up
the tree. You could
still draw a
constituent. You
could also train.

The numbers moved
into the high
eighties F1 on
WSJ sections
everyone memorized
(23 for test, 22
for dev, in the
culture). Those
numbers became a
ceiling people
chased with
rerankers and
self-training
(Charniak and
Johnson, later
McClosky). The
chase was real
science. It was
also a bit of a
closed room.

Dependency parsers
(Eisner, Nivre,
McDonald) offered
another sport:
arcs instead of
constituents,
sometimes faster,
sometimes closer
to what a
downstream IE
system wanted.
The last great
statistical
constituency
parsers did not
lose because they
were foolish. They
lost the spotlight
when neural
parsers and then
later encoder
stacks made the
feature
engineering look
optional.

Read Collins's
thesis-era papers
if you want to see
care. The
factorizations are
not arbitrary.
They are a person
trying to put
heads and
arguments into a
generative story
that will not
starve on unseen
word pairs.
