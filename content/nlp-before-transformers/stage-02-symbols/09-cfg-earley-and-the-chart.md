---
id: nlp-bt-09
title: "CFGs, Earley, and the chart: parsing as bookkeeping"
slug: cfg-earley-and-the-chart
series: nlp-before-transformers
stage: draft
status: staged
publish: false
novelty: public-record
era: "1956-1970"
topics: [CFG, Earley, CYK, chart-parsing]
---

# CFGs, Earley, and the chart: parsing as bookkeeping

Chomsky's hierarchy put context-free grammars in a sweet
spot. Expressive enough to be interesting, constrained
enough to be computable. Jay Earley's 1970 algorithm, and
the slightly earlier Cocke–Younger–Kasami dynamic program,
turned that spot into software. You fill a chart. Each
cell is a span and a nonterminal. You do not wander the
forest hoping a tree appears.

A chart parser is bookkeeping with a theory. The theory
says a sentence is a tree. The bookkeeping says we will
not re-derive the same constituent twice. Anyone who has
implemented CYK on a blackboard remembers the cubic
pain. Anyone who has implemented it on a real grammar
remembers the other pain: ambiguity. The chart does not
give you *the* parse. It gives you a packed forest of
parses. English is not kind.

I learned more about language from packed forests than
from manifesto papers. A newspaper sentence can have a
combinatorial pile of legal trees. Most of them are
garbage by any human standard. The algorithm is not
wrong. The grammar is underconstrained. That is why
the 1990s moved to *weighted* CFGs and why treebanks
became oxygen. Once a tree has a probability, you can
ask for the best one. Before that, you asked for "a"
parse and pretended.

Earley's algorithm still has a following because it
takes the grammar as it is, not only in Chomsky normal
form. It is a practical kindness. The dotted rules look
fussy until you debug a left-recursive grammar at
midnight and realize the dots are the only map you have.

There is a cultural point. For twenty years, "do you
parse?" was a way of asking whether you were a real
computational linguist. Tagging was considered lower.
Information retrieval was a different building. The
chart was a membership card. When statistical taggers
beat hand-written grammars on accuracy-per-hour, the
card lost some of its magic. The bookkeeping did not
become false. It became a layer.

If you want to feel the pre-transformer stack in your
hands, implement CYK on a twenty-rule grammar and then
add PP-attachment. The extra rule is small. The forest
is not. That ratio — small grammar, huge ambiguity — is
the original parsing problem. Neural parsers later hid
it. They did not repeal it.
