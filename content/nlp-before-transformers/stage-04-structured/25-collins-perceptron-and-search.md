---
id: nlp-bt-25
title: "Collins's perceptron: structure, search, and a weight vector"
slug: collins-perceptron-and-search
series: nlp-before-transformers
stage: draft
status: staged
publish: false
novelty: public-record
era: "2002"
topics: [perceptron, structured-prediction, Collins]
  - parse-tree-cfg
  - parse-tree-cfg
portrait: null
portrait_status: essay-only
image_rights: documented
image_pass: 2026-09-14
figure_id: parse-tree-cfg
meta_description: "Michael Collins's 2002 paper on discriminative training methods for hidden Markov models — the structured perceptron in the form most NLP people met it …"
figures:
  - ../assets/collins-perceptron-and-search/historical-timeline.svg
  - ../assets/collins-perceptron-and-search/concept-chart.svg
  - parse-tree-cfg
---

# Collins's perceptron: structure, search, and a weight vector

Michael Collins's 2002 paper on
discriminative training methods for
hidden Markov models — the structured
perceptron in the form most NLP
people met it — is a small algorithm
with a large attitude. Score a
structure with a dot product. Find
the best structure under the current
weights (or a good approximation).
If it is not the gold, add the gold
features and subtract the guessed
ones. Repeat.

<!-- graphics-pack:nlp-bt-v1 -->

<figure class="nlp-bt-figure">
<img src="../assets/collins-perceptron-and-search/historical-timeline.svg" alt="Timeline of public milestones for Collins's perceptron: structure, search, and a weight vector: dated anchors from the published record, not scraped leaderboard data." width="760" height="460" loading="lazy" decoding="async" />
<figcaption>Figure 1. Dated public anchors for this piece. Years follow the essay; verify against the prose before print.</figcaption>
</figure>

<!-- graphics-pack:nlp-bt-v1 -->

<figure class="nlp-bt-figure">
<img src="../assets/collins-perceptron-and-search/concept-chart.svg" alt="Concept chart for Collins's perceptron: structure, search, and a weight vector: schematic of the method or task shape (illustrative, not a copyrighted paper figure)." width="760" height="460" loading="lazy" decoding="async" />
<figcaption>Figure 2. Schematic of the method or task — editorial diagram, not live scores.</figcaption>
</figure>

<!-- graphics-pack:nlp-bt-v1 -->

<figure class="nlp-bt-figure nlp-bt-figure--archival">
<img src="https://upload.wikimedia.org/wikipedia/commons/a/aa/Syntax_tree.svg" alt="Context-free phrase structure tree diagram." width="760" height="520" loading="lazy" decoding="async" />
<figcaption>Figure 3. Phrase-structure tree used as CFG illustration. License: Public domain</figcaption>
</figure>


No partition function. No EM. The
cost of training is the cost of
decoding, again and again. That is
either a bargain or a nightmare,
depending on the decoder.

I like the perceptron in this history
because it made search first-class.
If your "argmax" is approximate —
beam search, a k-best list, a
cube-pruned decoder — the learning
algorithm is still willing to run.
It will learn around the search
errors if you let it, which is
sometimes what you want and
sometimes how you launder a bug.

Averaging the weight vectors (a
Freund and Schapire idea that
Collins used) was the difference
between a toy and a tool. The last
vector is jumpy. The average is
an adult. People who "tried the
perceptron and it was unstable"
often skipped the average.

The method wandered. POS tagging,
parsing (Collins had already been
a parser person), MT with MIRA and
related online updates in the Och
and Chiang orbit. Anywhere you
could define features of a
structure and a reasonably fast
search, someone pointed a
perceptron at it.

Compared with CRFs, you lose the
pretty likelihood. You gain speed
and a certain indifference to
global normalization. In the
2000s that trade was often
correct. In shared tasks, a
well-tuned perceptron and a
well-tuned CRF were sometimes
separated by pride more than by
F1.

The neural era did not kill this
object so much as rename it.
A lot of "we decode, we get a
loss, we take a gradient" is the
perceptron with a better score
function. Collins's paper is
still the clean copy: features,
search, update. If your modern
system cannot state those three,
it is not more advanced. It is
less housebroken.

MIRA and other large-margin
online updates sat in the same
hallway, especially in MT
tuning after Och. I will not
turn this draft into a catalog
of names. The family is: score
a structure, compare it to the
gold, move the weights so the
gold looks better next time.
Once you see the family, half
of the 2000s ACL anthology
stops looking like separate
religions.
