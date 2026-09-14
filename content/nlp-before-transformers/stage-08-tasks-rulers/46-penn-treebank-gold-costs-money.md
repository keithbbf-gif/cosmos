---
id: nlp-bt-46
title: "Penn Treebank: gold structure, and what it costs"
slug: penn-treebank-gold-costs-money
series: nlp-before-transformers
stage: draft
status: staged
publish: false
novelty: public-record
era: "1993"
topics: [Penn-Treebank, Marcus, annotation]
---

# Penn Treebank: gold structure, and what it costs

Mitchell Marcus, Beatrice Santorini, and Mary Ann Marcinkiewicz's 1993
paper — *Building a Large Annotated Corpus of English: The Penn
Treebank* — is a budget document disguised as a resource paper. Wall
Street Journal text, about a million words in the famous parsed slice,
tagged and bracketed by people, with guidelines, with disagreements,
with a tagset that became the air later students breathed.

I insist on the labor. A treebank is not "data that exists." It is
wages, training, reconciliation, a stylebook, and a decision about
what a node is allowed to mean. The annotation manual is the real
theory of syntax that the 1990s statistical parsers learned. If the
manual said a certain adverb was inside the VP, the parser that
"got it right" was matching the manual, not the mind of God.

The WSJ slice is also a genre choice. Financial newswire is not
conversation, not fiction, not a clinical note, not a tweet. Sentences
are long, names are companies, and the passive voice does a lot of
work. Systems that "solve parsing" on sections 22 and 23 solve that
institution's English. The later OntoNotes and Switchboard and
question-treebank efforts were admissions of this, not decorations.

The scientific effect was immediate. You could train. You could report
evalb F1 or labeled attachment and be compared. Collins, Charniak,
later the Berkeley parser and the Stanford parser — their sport
existed because the file existed. Unsupervised parsing research
existed as a protest against the file's cost and domain: what if we
cannot afford another million gold trees?

The tagset leaked everywhere. `NNP`, `VBD`, `IN`, the slightly
neurotic `TO`. Even people who never parsed used the tags as features
in CRFs and in chunkers. A treebank is a language. Once you speak it,
you start seeing its joints as nature. I have heard students argue
about whether something "is a PRT" as if the tag had been found in
the ground.

There is a quiet ethics point, public and ordinary. Newspaper text of
that era has reporters, editors, and subjects. It is not a neutral
sample of English. It is a particular institution's English, sold as
a product, with the usual silences. Models trained on it inherit the
institution. That does not make the resource illegitimate. It makes
the generalization claim a claim, not a fact.

If Brown made counting shareable, Penn made structure shareable.
Sharing structure is how statistical parsing escaped the demo. It is
also how a million WSJ words became, for twenty years, a stand-in for
"language." That stand-in was useful. It was never complete. Any
history that treats section 23 as the world is telling a funding
story, not a linguistic one.
