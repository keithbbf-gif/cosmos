---
id: nlp-bt-33
title: "Negative sampling: the cheap contrast that made embeddings affordable"
slug: negative-sampling-the-cheap-contrast
series: nlp-before-transformers
stage: draft
status: staged
publish: false
novelty: public-record
era: "2013"
topics: [negative-sampling, Word2Vec, NCE]
---

# Negative sampling: the cheap contrast that made embeddings affordable

A language-model softmax over a
large vocabulary is a bill. Every
training step, you normalize over
tens or hundreds of thousands of
words. Hierarchical softmax was
one way to dodge the bill: a
Huffman tree, a path of binary
decisions. Negative sampling was
the ruder dodge, and the one
that traveled.

Instead of asking the model to
assign a proper probability to
the true context word among all
words, you ask a binary
question a few times. Is this
the true pair? Are these k
noise pairs fake? The noise is
drawn from a unigram
distribution, often raised to
the 3/4 power because that
tweak, publicly reported,
worked. Mikolov et al. cited
the family of noise-contrastive
estimation (Gutmann and Hyvärinen;
Mnih and Teh) and then shipped
a simplified version.

I care about this because it is
a case where an approximation
became the object. People did
not treat negative sampling as
a regrettable hack they would
remove later. They treated it
as the training method. The
vectors are whatever that
contrast produces. That is
honest, if you keep it in the
open.

The 3/4 power is a good example
of craft versus myth. It
downweights the very head of
the unigram a bit and gives
the middle more chance to be
drawn as noise. You can
philosophize. You can also
just say: they tried it, the
neighbors looked better, the
note went into the paper.

Negative sampling also makes
the objective local. You can
stream a corpus. You do not
need a giant matrix in RAM if
you are careful. That is why
a desktop in 2013 could train
something useful. Accessibility
changed citation patterns.
Accessibility is part of
scientific success even when
theories are embarrassed by
it.

Later contrastive methods in
representation learning are
cousins. I will not drag this
series into that later weather.
The pre-transformer point is
smaller. Word2Vec was cheap
because it refused to be a
full language model at every
step. The refusal was the
invention users actually felt.
