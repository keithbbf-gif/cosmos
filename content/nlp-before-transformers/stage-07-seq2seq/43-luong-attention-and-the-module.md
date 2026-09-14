---
id: nlp-bt-43
title: "Luong attention: when looking became a module you could swap"
slug: luong-attention-and-the-module
series: nlp-before-transformers
stage: draft
status: staged
publish: false
novelty: public-record
era: "2015"
topics: [Luong, attention, OpenNMT]
---

# Luong attention: when looking became a module you could swap

Minh-Thang Luong, Hieu
Pham, and Christopher
Manning's 2015 EMNLP
paper is the one I hand
people who want to
implement attention
without drowning in the
Bahdanau notation. Score
functions are listed.
Global versus local is
listed. Input-feeding —
letting the previous
attention context back
into the next decoder
state — is listed. The
tone is "here is the
kit."

Local attention was an
attempt to keep the
cost from growing with
source length: predict
a pivot, look in a
window. It is easy to
skip in retrospect
because full attention
won on the sentence
lengths people actually
used. The impulse was
right. Cost would come
back as a plot problem
later, under a different
architecture.

Stanford's later
OpenNMT-adjacent
culture, and Harvard's
OpenNMT, and SYSTRAN's
involvement, and
Google's production NMT
announcements in
2016 — I will not turn
those into a corporate
scorecard. The public
fact is that by 2016
you could download a
seq2seq-with-attention
trainer. Moses no
longer had the only
serious open pipeline.

I like input-feeding as
a historical tell. It
admits that the decoder
state, by itself, forgets
what it just looked at.
So you pass the look
back in. A lot of
"architectural
innovations" of that
period are memory aids
for a recurrent core
that is trying its
best. Once the core
stops being recurrent,
some of the aids become
unnecessary. Some
become the core.

If Bahdanau is the
existence proof, Luong
is the API. APIs change
fields. People who
would not have derived
an alignment model from
first principles could
now type a class name
and join the comparison
table on WMT.

Keep the date. 2015 is
not 2017. The models
are still recurrent.
Training is still
fiddly. Byte-pair
encoding (Sennrich,
Haddow, Birch, 2016)
is about to make the
vocabulary less cursed.
The stack that
transformers inherit
is almost assembled:
subwords, attention,
a generation loss, a
beam. The missing
replacement is the
recurrent hallway
itself.
