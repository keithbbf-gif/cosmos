---
id: nlp-bt-40
title: "RNNLM: Mikolov’s recurrent language model you could train at home"
slug: rnnlm-mikolov-at-home
series: nlp-before-transformers
stage: draft
status: staged
publish: false
novelty: public-record
era: "2010-2012"
topics: [RNNLM, Mikolov, language-models]
---

# RNNLM: Mikolov’s recurrent language model you could train at home

Before Word2Vec, Tomas
Mikolov’s name was already
on a recurrent neural
network language model
and a piece of software
called RNNLM. The papers
around 2010–2012, some
with Kombrink, Burget,
Černocký, Khudanpur,
showed perplexity gains
over n-grams and, more
importantly, a culture of
interpolation: neural
plus count model, because
they fail differently.

The software mattered
again. You could compile
it. You could train on a
reasonable corpus. You
could dump probabilities
into a speech decoder.
This is the speech-people
inheritance with a
nonlinear twist.

I put this draft next to
Bengio 2003 on purpose.
Bengio's net was
feed-forward over a
fixed window. RNNLM let
the hidden state carry
an unbounded (in theory)
past. In practice the
past faded. In practice
it still beat a
truncated window on a
lot of data. Unbounded
in theory plus fading in
practice is the recurrent
story in one line.

Speech groups listened
because perplexity and
WER still talked to each
other. NLP groups
listened because a
language model is a
universal component:
translation, recognition,
even tagging if you
squint. Once a component
is universal, a better
one is a career.

The later Word2Vec
project looks, from here,
like someone who had
spent years on a full
language model deciding
to keep the vectors and
throw away the
expensive part. That is
interpretation, not a
quotation. It is
consistent with the
public trail.

If you want a tactile
sense of the era, train
a tiny RNNLM and a
trigram on the same
held-out text and plot
which sentences each
one prefers. The neural
model will like some
long agreements the
trigram misses. The
trigram will be calmer
on a rare proper name
it has actually seen.
Interpolation is not
cowardice. It is
listening to both
errors.
