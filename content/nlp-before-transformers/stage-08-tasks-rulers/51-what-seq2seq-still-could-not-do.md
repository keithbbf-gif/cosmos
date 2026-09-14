---
id: nlp-bt-51
title: "What seq2seq still could not do in 2016"
slug: what-seq2seq-still-could-not-do
series: nlp-before-transformers
stage: draft
status: staged
publish: false
novelty: public-record
era: "2016"
topics: [seq2seq, limitations, pre-transformer]
voice_check: edited
---

# What seq2seq still could not do in 2016

This is the last essay on purpose. It is not a transformer paper.
It is a list of public bruises that attentional seq2seq still wore
when *Attention Is All You Need* showed up on arXiv in June 2017.

Long documents were awkward. Attention over a sentence is a cost
you can pay. Attention over a chapter is a different invoice.
People truncated. People used hierarchical encoders. People
pretended a summary of a summary was a document model.

Word-level vocabularies were still a cliff until subword recipes
landed. Sennrich, Haddow, and Birch's BPE for NMT (2016) is late in
this timeline and essential. Copy mechanisms (Gu et al.; Gulcehre
et al.; See, Liu, and Manning's pointer-generator, 2017) admitted
that sometimes the right word is literally in the source and the
softmax should steal it.

Training was brittle. LSTM gates, dropout patterns, learning rates,
the occasional exploding gradient, the beam that preferred safe
short outputs — a competent 2016 NMT result was a craft object. Two
labs could disagree because one of them had a better initialization
folklore.

Discourse and consistency were weak. A translation system that
handles a sentence pair does not automatically handle a pronoun two
sentences later. Coreference, as a research program (from Hobbs
through Soon et al. through the CoNLL-2011/2012 shared tasks), had
not been absorbed into the encoder-decoder. It still sat in its
own drawer.

Interpretability was a heat map and a hope. Bahdanau alignments are
prettier than a phrase table and less editable. If a model invented
a number in a summary, you did not have a grep. See et al. measured
exactly that kind of faithfulness problem on CNN/DailyMail.

I am not offering a moral that the next architecture was
inevitable. Other fixes were in play: better RNNs, convolutional
seq2seq (Gehring et al., 2017), more copy, more reinforcement
learning on BLEU, which was its own trap. The public record says
only this. By 2016 the field had a working neural translation
stack, a list of known failure modes, and a growing suspicion that
the recurrent hallway was the part that did not want to scale.

The rest of the story is another folder, if anyone stages one. This
folder stops at the bruise. The bruise is enough to make the
previous fifty drafts feel like a single machine: count, structure,
align, then look. Looking was the last move the older field made
while it was still the older field.
