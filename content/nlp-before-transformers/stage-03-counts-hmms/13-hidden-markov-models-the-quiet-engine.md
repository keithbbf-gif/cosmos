---
id: nlp-bt-13
title: "Hidden Markov Models: the quiet engine under speech and tags"
slug: hidden-markov-models-the-quiet-engine
series: nlp-before-transformers
stage: draft
status: staged
publish: false
novelty: public-record
era: "1966-1989"
topics: [HMM, speech, POS-tagging, Rabiner]
voice_check: edited
---

# Hidden Markov Models: the quiet engine under speech and tags

An HMM is a small story. There is a chain of hidden
states. Each state emits an observation. You see the
emissions. You do not see the chain. You guess the
chain anyway, because the guess is useful.

Leonard E. Baum and colleagues developed the mathematics
in the 1960s. Andrew Viterbi's 1967 decoding algorithm
gave it a backbone. Speech recognition groups at IBM
and elsewhere turned it into a working method for
sound. Lawrence Rabiner's 1989 IEEE tutorial is the
document that taught the rest of us. If you learned
HMMs from a photocopied tutorial with forward-backward
written out in tidy sums, you learned them from
Rabiner's culture even if the photocopy was a
grandchild.

Part-of-speech tagging is the NLP version of the same
story. States are tags. Emissions are words. "Bank"
emits from `NN` or `VB` depending on the neighborhood.
The model is lying — syntax is not a one-state-per-word
Markov chain — but the lie is profitable. Church (1988)
and then a wave of HMM taggers showed you could beat
careful rule lists on accuracy-per-week of labor.

I want to keep the generative direction visible. An
HMM tells you how tags produce words. That felt
backwards to people who thought of tagging as
classification. It is backwards, and it is why the
math is clean. Joint probability. A path. A product
of transitions and emissions. You can write it on
one board.

The limitations are not subtle. A first-order HMM
cannot see far. Emissions are usually assumed
independent given the state, which is false for
spelling, morphology, and any word with internal
structure. Later models loosened this (trigram tags,
maximum-entropy Markov models, CRFs). They did not
abandon the hidden-chain picture so much as change
who the chain was conditional on.

Speech is where the HMM earned its keep. Phones,
triphones, Gaussian mixtures, language-model
combination — a whole industry sat on "hidden state
emits frame." NLP borrowed the prestige and the
algorithms. When you read a 1990s tagging paper that
sounds like a speech paper, that is not an accident.
It is a transfer of a working religion.

If you only remember one operational fact: training
is counting, with a soft assignment when the states
are not labeled. Decoding is dynamic programming.
Everything else is a refinement or a protest.

I will name the implementations people actually
ran. TnT. HunPos. The HMM mode inside various
NLTK tutorials. Speech toolkits that treated
words as just another emission. None of these
were "the paper." They were the reason a
journalist could get a tagged newswire dump
before lunch. A method that does not leave a
binary is a rumor. HMMs left binaries.

The protest that followed — maxent, MEMM, CRF —
did not say "hidden states were a mistake." It
said "we want the observations to talk louder,
and we want overlapping features." That is a
grown argument with the quiet engine, not a
cancellation of it. If you skip HMMs, the CRF
paper is a rabbit out of a hat. It is not. It
is a next sentence.
