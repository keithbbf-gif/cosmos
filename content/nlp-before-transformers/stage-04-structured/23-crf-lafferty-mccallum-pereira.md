---
id: nlp-bt-23
title: "CRFs: Lafferty, McCallum, Pereira, 2001"
slug: crf-lafferty-mccallum-pereira
series: nlp-before-transformers
stage: draft
status: staged
publish: false
novelty: public-record
era: "2001"
topics: [CRF, structured-prediction, sequence-labeling]
---

# CRFs: Lafferty, McCallum, Pereira, 2001

The conditional random field paper is short by modern
standards and dense in the way a paper is dense when
the authors know they are replacing a working tool.
John Lafferty, Andrew McCallum, and Fernando Pereira
defined a Markov random field over the output
sequence, conditioned on the whole input. No
generative story for the words. One partition function
for the path.

That last clause is the product. A CRF can look at any
feature of the observation at any position — prefixes,
neighboring words, a lexicon hit two steps away —
without promising to generate those words. HMMs had to
be shy about observations because observations were
emissions. MEMMs could look, then they locally
normalized themselves into trouble. The CRF paper is,
among other things, a diagnosis of that trouble with
a replacement attached.

Linear-chain CRFs kept Viterbi and forward-backward.
The algorithms did not get more magical. The scores
got more honest. Training became a convex problem if
the features were given, which is a kinder mountain
than Baum–Welch. People still managed to hurt
themselves with feature explosions and bad
regularization, because convexity does not save you
from a stupid representation. I have trained a CRF
that memorized a rare spelling and then died on the
next rare spelling. Convex and overfit can sit in
the same run.

I spent a portion of the 2000s living in CRF++
configuration files and templates like
`U07:%x[-2,0]/%x[-1,0]`. That is not a glamorous
memory. It is an accurate one. Named-entity
recognition, Chinese word segmentation, shallow
parsing — the shared-task winners for years were
feature templates plus a CRF plus a gazetteer. The
paper is the theory. The template file is the
culture. If you never opened a template file, you
have not met the method as it was used.

McCallum's later MALLET software made the method
portable. Sutton and McCallum's tutorial became the
teaching document. By the time neural sequence models
arrived, "just put a CRF on top" was a proverb. Even
some neural NER systems kept a CRF layer so the
output tags would not stutter. The 2001 object
refused to leave. That refusal is data. It says the
field still wanted a structured output constraint
after it stopped wanting to type features.

A CRF is not "understanding." It is a principled way
to score a structured output given a kitchen sink of
clues. In a field that had been torn between stories
and counts, that was a truce you could ship. The next
draft is the truce in the wild. This one is the
paper that made the truce legal.
