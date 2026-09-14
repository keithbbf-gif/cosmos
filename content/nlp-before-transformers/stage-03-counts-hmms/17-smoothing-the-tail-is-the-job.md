---
id: nlp-bt-17
title: "Smoothing: Good–Turing, Kneser–Ney, and the dignity of the tail"
slug: smoothing-the-tail-is-the-job
series: nlp-before-transformers
stage: draft
status: staged
publish: false
novelty: public-record
era: "1953-1999"
topics: [smoothing, Good-Turing, Kneser-Ney]
  - ngram-count-table
  - ngram-count-table
portrait: null
portrait_status: essay-only
image_rights: documented
image_pass: 2026-09-14
figure_id: ngram-count-table
meta_description: "Zipf's law is not a trivia item. It is the reason language modeling is a tail problem. A few words do most of the work. An endless list of words do almo…"
figures:
  - ../assets/smoothing-the-tail-is-the-job/historical-timeline.svg
  - ../assets/smoothing-the-tail-is-the-job/concept-chart.svg
  - ngram-count-table
---

# Smoothing: Good–Turing, Kneser–Ney, and the dignity of the tail

Zipf's law is not a trivia item. It is the reason
language modeling is a tail problem. A few words
do most of the work. An endless list of words do
almost none, until the one time they do and your
model assigns them nothing.

<!-- graphics-pack:nlp-bt-v1 -->

<figure class="nlp-bt-figure">
<img src="../assets/smoothing-the-tail-is-the-job/historical-timeline.svg" alt="Timeline of public milestones for Smoothing: Good–Turing, Kneser–Ney, and the dignity of the tail: dated anchors from the published record, not scraped leaderboard data." width="760" height="460" loading="lazy" decoding="async" />
<figcaption>Figure 1. Dated public anchors for this piece. Years follow the essay; verify against the prose before print.</figcaption>
</figure>

<!-- graphics-pack:nlp-bt-v1 -->

<figure class="nlp-bt-figure">
<img src="../assets/smoothing-the-tail-is-the-job/concept-chart.svg" alt="Concept chart for Smoothing: Good–Turing, Kneser–Ney, and the dignity of the tail: schematic of the method or task shape (illustrative, not a copyrighted paper figure)." width="760" height="460" loading="lazy" decoding="async" />
<figcaption>Figure 2. Schematic of the method or task — editorial diagram, not live scores.</figcaption>
</figure>

<!-- graphics-pack:nlp-bt-v1 -->

<figure class="nlp-bt-figure nlp-bt-figure--archival">
<img src="https://upload.wikimedia.org/wikipedia/commons/f/f3/Shannon_communication_system.svg" alt="Information channel diagram tied to prediction and counting." width="760" height="400" loading="lazy" decoding="async" />
<figcaption>Figure 3. Shannon communication diagram as entropy / prediction visual. License: Public domain</figcaption>
</figure>


I. J. Good's 1953 twist on Turing's wartime
thinking — Good–Turing frequency estimation —
says the probability of things seen r times
should be adjusted using how many things were
seen r+1 times. Unseen events get a mass stolen
from the hapaxes. The idea feels like a card
trick the first time. Then you realize every
later smoother is a way to steal from the
seen and give to the unseen without wrecking
the head.

Kneser–Ney is the one I would teach if I could
only teach one. The insight is about backoff
distributions. The unigram you back off to
should not be "how common is this word." It
should be "in how many different contexts does
this word appear." "Francisco" is common and
still a terrible generic backoff after a random
verb. It is a good backoff after "San." Lower
order, in this philosophy, is about
continuation, not raw popularity.

Stanley Chen and Joshua Goodman's report at
the end of the 1990s is the engineering
document. Modified Kneser–Ney, count
binning, interpolation versus backoff — they
measured it. A lot of later "we used KN
smoothing" footnotes are a pointer to that
measurement culture.

Add-k smoothing is the pedagogical toy. It
makes every count a little less lonely. It
also smears probability into impossible
places if you are not careful with the
vocabulary. I have seen student models that
assigned more mass to garbage tokens than
to the comma. That is add-k without a
grown-up vocab policy.

Why does this still belong in a
pre-transformer series? Because neural
models did not abolish the tail. They
moved it. Rare words became rare pieces,
or rare types in a softmax, or UNK.
Subword tokenization is, among other
things, a smoothing strategy you apply
before training. The old papers are more
honest about the theft.

When someone says a language model
"generalizes," ask where the mass for the
new thing came from. Good–Turing had an
answer. It was not romantic. It was a
reallocation.

I will be concrete. You have a trigram
that never saw "of the fjord." A bad
smoother gives it nothing, or gives it
the same dust it gives "of the
asdfgh." A grown smoother backs off to
"the fjord" or to a continuation
distribution that knows "fjord" is the
kind of word that follows "the" after
geographical talk. The difference is
not a metaphor. It is a held-out
perplexity you can print. Print it.
