---
id: nlp-bt-39
title: "LSTM: a 1997 paper that got its career in the 2010s"
slug: lstm-1997-career-2010s
series: nlp-before-transformers
stage: draft
status: staged
publish: false
novelty: public-record
era: "1997-2015"
topics: [LSTM, Hochreiter, Schmidhuber, vanishing-gradient]
---

# LSTM: a 1997 paper that got its career in the 2010s

Sepp Hochreiter and Jürgen
Schmidhuber published "Long
Short-Term Memory" in 1997
in *Neural Computation*.
The problem they named was
already known: vanishing
(and exploding) gradients
in recurrent nets. The
fix was a memory cell with
gates, so a signal could
pass through time without
being crushed at every
step.

For years this was a
specialist's object.
Speech and handwriting
groups (Alex Graves's
line of work is the one
I would point a reader
at) kept the flame.
Then, in the early 2010s,
LSTMs became the default
recurrent unit for
language. Neural machine
translation, language
modeling, sequential
tagging — if it was
recurrent and ambitious,
it was probably an LSTM,
later a GRU (Cho and
colleagues, 2014) if you
wanted fewer gates.

I do not want a gates
tutorial here. Those
exist. I want the
historical kink. The
algorithm was old. The
career was new. CUDA,
datasets, and a community
shift did more than a
sudden insight in 2014.
When a method sits in
the literature for
fifteen years and then
takes over, look at the
computers.

NLP's use of LSTMs had a
particular smell.
Bidirectional LSTMs for
tagging (the past and
the future both get a
say). Encoder LSTMs for
a sentence, decoder
LSTMs for a translation.
Dropout recipes that
people treated as folklore.
Gradient clipping.
The craft was real and
fiddly. Anyone who says
the pre-transformer
neural years were clean
is lying or was not
training them.

The limitation that
matters for the next
stage is not romance
about long memory. It is
the fact that a chain is
still a chain. A
hundred-token sentence
is a long path for a
gradient and a long path
for a hidden state that
has to remember the
subject until the verb
in German. Attention
will be sold as a patch
for that path. The patch
will eat the host.

1997 remains the date.
2014 is when most NLP
people I knew started
typing `LSTM` without
looking up the
abbreviation.
