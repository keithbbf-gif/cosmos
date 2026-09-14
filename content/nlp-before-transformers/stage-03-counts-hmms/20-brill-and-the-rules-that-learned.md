---
id: nlp-bt-20
title: "Brill's tagger: rules that learned, and why that felt like a truce"
slug: brill-and-the-rules-that-learned
series: nlp-before-transformers
stage: draft
status: staged
publish: false
novelty: public-record
era: "1992-1995"
topics: [Brill-tagger, transformation-based-learning, POS]
voice_check: edited
---

# Brill's tagger: rules that learned, and why that felt like a truce

Eric Brill's transformation-based tagger (papers in the early
1990s, the *Computational Linguistics* account in 1995) starts with
a simple guess — most-frequent tag, or a small lexicon — and then
learns a list of repair rules. "Change NN to VB if the previous tag
is TO." The rules are readable. You can argue with them. They also
come from a greedy search over a training set, not from a
committee.

That combination is why people who hated pure statistics and people
who hated pure hand-writing both used it. The output looked like
the old craft. The induction looked like the new one.

I implemented a tiny Brill-style learner once for a class and then
again, years later, because a client wanted to *see* the rules.
Seeing is not a metric. It is a deployment constraint. A
hospital-adjacent or legal- adjacent workflow — I will stay general
— sometimes needs a change you can explain without a matrix.
Transformation lists explain.

The algorithm is greedy and knows it. Each rule is the current best
repair on the current tagging. Order matters. A later rule sees a
different landscape. There is no global optimum hiding in the
drawer. There is a list that stops growing when the gains get
small. That honesty is rare.

HMM taggers of the same era were often a point or two better on the
standard WSJ splits after enough tuning. Brill was close, fast to
apply, and culturally portable. Close plus portable beats
best-plus-opaque when the user is a linguist who has to maintain
the thing.

Transformation-based learning had a brief wider life (chunking, and
some spelling work). It did not become the universal learner. CRFs
and later neural taggers took the accuracy crown. I still think
Brill belongs in the main hallway of this history, not the closet.
It is the moment the field admitted that a learned system could
speak in if-then without apology.

If you teach tagging, run an HMM and a Brill list on the same messy
text and read the disagreements aloud. The disagreements are the
syllabus.

One more reason it belongs in this series: it is a public example
of a learner whose hypothesis class a non-programmer can read. That
is rare after 2001. CRFs can be inspected if you sort the weights.
Neural nets can be probed if you enjoy probes. A Brill list you can
tape to the wall. I have taped one to a wall. The third rule was
stupid and we deleted it. Deletion is a kind of science.
