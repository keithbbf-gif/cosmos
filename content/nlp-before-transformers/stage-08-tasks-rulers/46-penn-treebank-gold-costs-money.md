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

Mitchell Marcus, Beatrice
Santorini, and Mary Ann
Marcinkiewicz's 1993
paper on Building a Large
Annotated Corpus of
English — the Penn
Treebank — is a budget
document disguised as a
resource paper. Wall
Street Journal text,
about a million words in
the famous slice, tagged
and parsed by people,
with guidelines, with
disagreements, with a
tagset that became the
air later students
breathed.

I insist on the labor.
A treebank is not "data
that exists." It is
wages, training,
reconciliation, a
stylebook. The WSJ
slice is also a genre
choice. Financial
newswire is not
conversation, not
fiction, not a
clinical note. Systems
that "solve parsing"
on WSJ solve WSJ.

The scientific effect
was immediate. You
could train. You could
report labeled
attachment or evalb
F1 and be compared.
Collins, Charniak,
later Berkeley and
Stanford parsers —
their sport existed
because the file
existed. Unsupervised
parsing research
existed as a protest
against the file's
cost and domain.

The tagset leaked
everywhere. `NNP`,
`VBD`, `IN`. Even
people who never
parsed used the tags
as features. A
treebank is a
language. Once you
speak it, you start
seeing its joints
as nature.

There is a quiet
ethics point, public
and ordinary.
Newspaper text of
that era has
reporters, editors,
and subjects. It is
not a neutral
sample of English.
It is a particular
institution's
English. Models
trained on it
inherit the
institution.

If Brown made
counting shareable,
Penn made structure
shareable. Sharing
structure is how
statistical parsing
escaped the demo.
It is also how a
million WSJ words
became, for twenty
years, a stand-in
for "language."
That stand-in was
useful. It was
never complete.
