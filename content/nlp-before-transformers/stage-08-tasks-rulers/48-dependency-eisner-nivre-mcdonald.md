---
id: nlp-bt-48
title: "Dependency parsing: Eisner, Nivre, McDonald"
slug: dependency-eisner-nivre-mcdonald
series: nlp-before-transformers
stage: draft
status: staged
publish: false
novelty: public-record
era: "1996-2006"
topics: [dependency-parsing, Eisner, Nivre, McDonald]
---

# Dependency parsing: Eisner, Nivre, McDonald

A dependency tree is a
set of arcs from heads
to dependents. No
internal NP node
unless you want one.
For a lot of
languages, and for a
lot of information
extraction, that is
the structure you
actually use.

Jason Eisner's 1990s
dynamic programs gave
projective dependency
parsing a cubic
method with a clean
recurrence. Joakim
Nivre's transition
systems (arc-standard,
arc-eager) made
parsing look like a
sequence of stack
operations you could
learn with a
classifier. Ryan
McDonald and
colleagues' maximum
spanning tree parser
(2005) treated the
sentence as a graph
and found the best
tree, with
non-projective
arcs allowed if you
used the right
algorithm.

I like this trio
because they
disagree usefully.
Eisner is
exactness under
assumptions. Nivre
is linear-time
greed (or beam)
with a feature
rich classifier,
very fast, very
shippable. McDonald
is global scoring
of arcs. In the
2000s you could
pick a personality.

The CoNLL shared
tasks on
dependency parsing
(2006, 2007) did
for this sport
what CoNLL-03 did
for NER. Many
languages. A
standard format
(the CoNLL columns
that still haunt
files). A ranking.
MaltParser and
MSTParser became
verbs.

Neural
transition-based
and graph-based
parsers later
replaced the
feature templates
with BiLSTMs.
The objects
remained. A stack,
a buffer, an arc
score. When a
modern system
emits a
dependency tree,
it is speaking
this dialect
whether or not
the citation is
polite.

The
pre-transformer
lesson is
practical. If
your downstream
task wants "who
did what to
whom,"
constituents are
a lovely
intermediate and
dependencies are
often the
interface. The
2000s figured
that out in
public, with
scores.
