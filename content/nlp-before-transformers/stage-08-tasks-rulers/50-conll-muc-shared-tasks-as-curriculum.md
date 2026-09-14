---
id: nlp-bt-50
title: "MUC, ACE, CoNLL: shared tasks as the real curriculum"
slug: conll-muc-shared-tasks-as-curriculum
series: nlp-before-transformers
stage: draft
status: staged
publish: false
novelty: public-record
era: "1987-2003"
topics: [MUC, ACE, CoNLL, shared-tasks]
---

# MUC, ACE, CoNLL: shared tasks as the real curriculum

If you want to know what pre-transformer NLP actually studied, do
not start with a textbook chapter on meaning. Start with the
shared tasks. MUC, the Message Understanding Conferences, from
the late 1980s into the 1990s, paid people to extract who did
what in newswire and in terrorist-incident reports, with scoring
that could make you wince. ACE later widened the entity and
relation game. CoNLL, year after year, picked a task and a
format and a deadline.

I am not romantic about competitions. They distort. They overfit.
They turn a messy social problem into a column file. They also
create a curriculum that does not depend on one professor's
taste. A student in Prague and a student in Baltimore could train
on the same splits and disagree about a number. That is a
civilization. It is also a way to make a field feel like a sport,
with the usual sport diseases.

MUC's scoring — precision, recall, the way partial credit and
alignment of templates worked — taught the field that extraction
is not classification. You have to find the span, type it, and
sometimes link it. Named-entity recognition as we still teach it
is a simplified grandchild of that pain. If your NER F1 looks
clean, remember that MUC was willing to score a whole template
wrong because one slot drifted.

CoNLL-2000 chunking, CoNLL-2002 and 2003 NER, CoNLL-2006
dependencies: I can still see the column layouts. `B-NP`,
`I-PER`, head indices, a blank line between sentences. Formats
are pedagogy. They tell you what a token is, what a sentence is,
what counts as a mistake. They also tell you that a sentence is
a line-oriented object, which is a lie about speech and a
convenience about newswire.

The darker side is domain. Newswire again. English often. A lot
of "language-independent" tasks were independent the way a hotel
breakfast is international. Spanish and Dutch in CoNLL-2002 were
a real widening and still a small club. Anyone who cites a 2003
English NER number as "NLP is solved for entities" is selling
something.

ALPAC asked for measurement. Shared tasks were one answer: not a
committee report, a recurring contest with a file you could
fetch. That is a different institution. This series owes it a
draft because almost every method above — HMM, CRF, Word2Vec as
a feature, seq2seq as a later guest — proved itself by walking
into one of these rooms and putting a number on the board.
