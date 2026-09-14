---
id: nlp-bt-42
title: "Bahdanau attention: the patch that became the point"
slug: bahdanau-attention-the-patch
series: nlp-before-transformers
stage: draft
status: staged
publish: false
novelty: public-record
era: "2014-2015"
topics: [attention, Bahdanau, NMT]
  - attention-alignment
  - attention-alignment
portrait: null
portrait_status: essay-only
image_rights: documented
image_pass: 2026-09-14
figure_id: attention-alignment
meta_description: "Dzmitry Bahdanau, Kyunghyun Cho, and Yoshua Bengio put the 2014/2015 paper on arXiv as \"Neural Machine Translation by Jointly Learning to Align and Tran…"
figures:
  - ../assets/bahdanau-attention-the-patch/historical-timeline.svg
  - ../assets/bahdanau-attention-the-patch/concept-chart.svg
  - attention-alignment
---

# Bahdanau attention: the patch that became the point

Dzmitry Bahdanau, Kyunghyun Cho, and Yoshua Bengio put the
2014/2015 paper on arXiv as "Neural Machine Translation by
Jointly Learning to Align and Translate." The encoder no
longer had to cram a sentence into one vector. It produced
a vector per source position. At each decoder step, a
small net scored those positions, softmaxed the scores,
and made a weighted sum. That sum was the context.

<!-- graphics-pack:nlp-bt-v1 -->

<figure class="nlp-bt-figure">
<img src="../assets/bahdanau-attention-the-patch/historical-timeline.svg" alt="Timeline of public milestones for Bahdanau attention: the patch that became the point: dated anchors from the published record, not scraped leaderboard data." width="760" height="460" loading="lazy" decoding="async" />
<figcaption>Figure 1. Dated public anchors for this piece. Years follow the essay; verify against the prose before print.</figcaption>
</figure>

<!-- graphics-pack:nlp-bt-v1 -->

<figure class="nlp-bt-figure">
<img src="../assets/bahdanau-attention-the-patch/concept-chart.svg" alt="Concept chart for Bahdanau attention: the patch that became the point: schematic of the method or task shape (illustrative, not a copyrighted paper figure)." width="760" height="460" loading="lazy" decoding="async" />
<figcaption>Figure 2. Schematic of the method or task — editorial diagram, not live scores.</figcaption>
</figure>

<!-- graphics-pack:nlp-bt-v1 -->

<figure class="nlp-bt-figure nlp-bt-figure--archival">
<img src="https://upload.wikimedia.org/wikipedia/commons/c/c7/Seq2seq_RNN_encoder-decoder_with_attention_mechanism%2C_training.png" alt="Attention links between encoder states and decoder steps." width="760" height="480" loading="lazy" decoding="async" />
<figcaption>Figure 3. Attention mechanism in encoder-decoder training. License: See Commons</figcaption>
</figure>


They called it aligning. The field later called it
attention. I try to keep both words. Aligning connects it
to IBM Model 1 and to GIZA++. Attention connects it to
everything after 2017. The mechanism is a soft,
differentiable alignment table learned from the same loss
as the translation. EM used to estimate alignments as a
latent. Here the latent is differentiable and does not
need its own E-step.

The qualitative pictures in that paper — a French
sentence, an English sentence, a heat map — did as much
work as the BLEU table. You could *see* the verb pick up
the verb. You could see the system look back.
Interpretability here is not a philosophy seminar. It is
a debugging tool that also happened to make slides. I
have used those heat maps to find a model that was
looking at the period. Looking at the period is a
confession.

I want to keep the motivation small. Seq2seq without
attention degraded on long sentences. Everyone who
trained one felt it. Bahdanau et al. measured it and
then removed the funnel. That is a conservative paper,
in the best sense. It does not announce a new age. It
fixes a bottleneck and shows the alignments you would
hope for. The new age happened anyway, because once
you can look, you start asking why the encoder itself
has to walk a chain to produce the things you look at.

Luong, Pham, and Manning (2015) soon gave a catalog of
simpler attention flavors. The catalog mattered because
it made the idea a module. Once a thing is a module, it
leaves translation. Summarization, image captions,
speech — the same softmax over memory.

This series stops before self-attention takes over the
encoder itself. That is a later plot. The
pre-transformer fact is already enough. By 2015 the
field had learned that a decoder should be allowed to
look, not only to remember. Looking turned out to be
the more scalable skill. Remembering was the older
virtue. The bruise in the last essay is what happens
when looking is still sitting on top of a hallway.
