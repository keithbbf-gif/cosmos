---
id: nlp-bt-44
title: "From Pharaoh and Moses to neural MT: what actually got replaced"
slug: from-moses-to-neural-mt
series: nlp-before-transformers
stage: draft
status: staged
publish: false
novelty: public-record
era: "2003-2016"
topics: [Moses, SMT, NMT, Koehn]
---

# From Pharaoh and Moses to neural MT: what actually got replaced

Philipp Koehn's Pharaoh
decoder and then the
Moses toolkit (with
Hoang, Birch, Callison-
Burch, and a long list
of contributors) were
the public factory of
statistical machine
translation in the
2000s. You aligned with
GIZA++. You extracted
phrase pairs. You built
a target language
model. You tuned
weights, often with
Och's MERT, later with
kinder optimizers. You
decoded.

That factory had a
smell. Phrase tables
on disk. Tuning that
could overfit a small
dev set. A hundred
knobs. Also: you could
open the phrase table
and *see* that
"maison blanche" liked
"White House" in a
political corpus. The
system was wrong in a
way you could pursue
with grep.

Neural MT did not
replace Moses because
Moses was unserious. It
replaced Moses because
on a lot of WMT pairs,
by 2016, an
attentional seq2seq
model scored higher
and needed less
feature engineering
from you, provided you
had GPUs and a
subword recipe.
Google's 2016
production NMT paper
(Wu and many
colleagues) is the
industrial public
marker. Research had
already been leaning.

What got lost, for a
while, was
intervenability. You
cannot grep a 512-
dimensional state for
a bad idiom. What got
gained was fluency,
especially on
morphology and on
reordering that phrase
pairs had to memorize
the hard way.

I do not tell this as
a morality play.
Plenty of production
MT in 2016 was still
a hybrid: neural
language models in a
statistical decoder,
or SMT lattices
rescored by an LSTM.
Hybrids are how
factories actually
change. Overnight
replacements are how
keynotes change.

If you want the
pre-transformer
ending in one
workshop memory: a
Moses baseline, a
seq2seq+attention
challenger, a BLEU
table, an argument
about whether BLEU
was allowed to decide
the argument. That
workshop *is* the
field in 2015. The
next year the
challenger was the
baseline.
