---
id: nlp-bt-22
title: "MEMMs and the label-bias trap"
slug: memm-and-the-label-bias-trap
series: nlp-before-transformers
stage: draft
status: staged
publish: false
novelty: public-record
era: "2000-2001"
topics: [MEMM, label-bias, McCallum]
---

# MEMMs and the label-bias trap

A maximum-entropy Markov model is the
obvious hybrid. You want HMM-like
sequence structure. You want maxent-like
features of the observation. So you
make each next-state distribution a
maxent classifier that sees the previous
state and the current observations.
Andrew McCallum, Dayne Freitag, and
Fernando Pereira described the setup
around 2000. It worked. It also had a
failure mode with a name.

Label bias, as Lafferty, McCallum, and
Pereira framed it in the 2001 CRF paper,
is about mass that cannot go anywhere.
If a state has only a few outgoing
transitions, it will pass probability
along those transitions even when the
observation is screaming that the whole
path is wrong. Local normalization at
each step makes the model conservative
in a bad way. It trusts the state too
much and the observation too little
when the state's fan-out is thin.

I have felt this in practice more than I
have proved it on a board. You build a
MEMM chunker. It gets addicted to its
own previous I-NP decision. A new token
that should start a new phrase cannot
break the streak because the transition
distribution from I-NP is peaked. You
add features. The peak remains. The
architecture is the peak.

The fix that stuck was to stop
normalizing locally. Conditional random
fields put one big normalization over
the whole path. That is computationally
ruder and statistically kinder. The
observation can veto a path even if
each local gate would have let it
through.

I do not tell this as "MEMMs were
foolish." They were the right next
attempt after HMMs and maxent
classifiers. A lot of software shipped
on them. The label-bias discussion is
one of the better examples of the field
doing criticism in public and then
changing the model class. That is rarer
than people think.

If you implement both a MEMM and a
linear-chain CRF on the same NER
feature set, do not only compare F1.
Watch the errors that start with a
wrong first tag and then coast. Coasting
is the trap. CRFs do not make you
immune. They make the coasting more
expensive.
