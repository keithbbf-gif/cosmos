---
id: nlp-bt-49
title: "LDA: Blei, Ng, Jordan, and topics as mixtures"
slug: lda-topics-as-mixtures
series: nlp-before-transformers
stage: draft
status: staged
publish: false
novelty: public-record
era: "2003"
topics: [LDA, topic-models, Blei]
---

# LDA: Blei, Ng, Jordan, and topics as mixtures

Latent Dirichlet
Allocation (David
Blei, Andrew Ng,
Michael Jordan,
2003) gave the
2000s a default
way to say
"what is this
collection about"
without a label
set. A document
is a mixture of
topics. A topic
is a distribution
over words. The
Dirichlet priors
keep the mixtures
sparse-ish. You
infer with
variational
methods or Gibbs
sampling and then
you stare at the
top words.

I have stared at
a lot of top
words. Sometimes
you get a clean
"sports" and a
clean "finance."
Sometimes you get
a topic that is
just the footer
boilerplate of a
web crawl. The
model is not
trying to please
your ontology.
It is trying to
explain counts.

LDA sits next to
LSA in this
history and
disagrees with
it. LSA's latent
directions are
not
distributions
and do not
generate words
in a proper
probabilistic
story. LDA's
do. That
probabilistic
story made it
extendable:
author-topic,
dynamic topic
models, supervised
variants. The
Blei lineage is
a workshop
economy.

NLP people used
LDA as a feature
factory. Topic
proportions went
into classifiers
and into
browsing
interfaces.
Political
science and
digital
humanities used
it as a
measurement
instrument, which
is a heavier
claim and not
one I will
adjudicate here.
The public
caution is the
same as with
Word2Vec
neighbors: the
topics are a
compression of
your corpus's
habits, including
its garbage.

Why include this
in a
before-transformers
series? Because
unsupervised
structure over
bags of words was
a major 2000s
sport, and
because a lot of
later "the model
discovered
concepts" talk
has an older,
more honest
cousin in a list
of top words you
can laugh at.
Laughter is a
validity check.
Use it.
