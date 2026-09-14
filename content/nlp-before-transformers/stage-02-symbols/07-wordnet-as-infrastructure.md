---
id: nlp-bt-07
title: "WordNet: a lexical database that became plumbing"
slug: wordnet-as-infrastructure
series: nlp-before-transformers
stage: draft
status: staged
publish: false
novelty: public-record
era: "1985-1995"
topics: [WordNet, lexical-semantics, Miller]
---

# WordNet: a lexical database that became plumbing

George Miller's group at Princeton started WordNet in the
mid-1980s. The public paper most people cite is the 1995
*Communications of the ACM* overview. The resource is older
than the paper. It grouped English words into synsets —
near-synonym sets — and hung those sets on relations:
hypernym, hyponym, meronym, antonym. A dictionary that
admitted it was a graph.

I used WordNet the way a carpenter uses a stud finder. Not
as a theory of meaning. As a way to ask, in code, whether
two strings might be talking about the same kind of thing.
Lesk-style word-sense disambiguation, simple query expansion,
a cheap "is-a" check for an information-extraction pattern —
that was the daily traffic. The hierarchy was uneven. Some
regions were lovingly tended. Some were a junk drawer. It
still beat having nothing.

WordNet is infrastructure in the boring sense. It got bundled
into NLTK. It got translated and mirrored (EuroWordNet, later
Open Multilingual WordNet). Papers treated `path_similarity`
as if it were a scientific instrument. It is a walk on a
hand-built graph. The walk correlates with something humans
mean by relatedness, sometimes, in some parts of the noun
tree. That is enough for a baseline and not enough for a
worldview.

Miller came from psychology. The synset is closer to a
concept than a dictionary headword. That choice is why
WordNet felt modern next to a printed lexicon and why it
felt crude next to a distributional vector. Concepts do not
actually sit still. "Mouse" the animal and "mouse" the
device are easy. Abstract nouns are a negotiation.

There is a style of 2000s paper that evaluates a new
embedding by how well it reconstructs WordNet relations.
I understand the urge. You need a public yardstick. But
fitting WordNet is not the same as learning language. It
is fitting a particular Princeton-shaped picture of English
nouns, built by people, with budget and taste.

The pre-transformer lesson is about resources that outlive
theories. WordNet survived the statistical turn because it
was a file you could open. It survived the early neural
turn because it was still a file you could open. When a
field has a shared, slightly wrong graph of words, the
graph becomes part of the language the field speaks.
