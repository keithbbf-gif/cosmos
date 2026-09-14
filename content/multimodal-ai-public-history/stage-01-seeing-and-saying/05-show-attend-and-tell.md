---
id: mmh-05
title: "Show, Attend and Tell: a map over the photograph"
slug: show-attend-and-tell
series: multimodal-ai-public-history
stage: draft
status: staged
publish: false
novelty: public-record
era: "2015"
topics: [Xu, attention, captioning, ICML]
voice_check: edited
---

# Show, Attend and Tell: a map over the photograph

Xu, Ba, Kiros, Cho, Courville, Salakhutdinov, Zemel, and Bengio's
*Show, Attend and Tell* (ICML 2015, arXiv:1502.03044) is the captioning
paper people remember because of the pictures. The decoder, at each
word, puts a soft weight on a grid of convolutional features. You can
draw the weights. For a year or two, every talk had a heat map that
lit up the frisbee when the model said "frisbee."

The technical move is Bahdanau attention, lifted from neural machine
translation into vision. That is not a smear. The authors say so. The
public contribution is that **alignment became visible**. A reader who
did not want to read a derivation could still see that the model was
looking at something. Visibility recruited people. It also flattered
the model. A heat map is a genre. Genres can be cropped for the slide.

Two variants sat in the paper: a deterministic soft attention and a
hard attention trained with a variational or REINFORCE-style story.
The field, being the field, mostly shipped soft attention. Soft
attention is a weighted average. It is differentiable. It is also a
compromise. The model never has to choose a box. Later object-based
models will decide that compromise is the bug.

Why this draft is not just a sequel to Show and Tell:

- It makes **the interface spatial**. The photograph is no longer one
  vector. It is a set of places the language model can query.
- It is an ancestor of **cross-attention** in later visual-language
  models, including the gated cross-attention Flamingo will publish in
  2022. The 2022 paper is larger and stranger. The 2015 paper is the
  one that taught a generation the diagram.
- It is a warning about **explanation theater**. A map that correlates
  with a word is not a proof of grounding. The 2010s learned this the
  hard way; the 2020s sometimes forgot.

If you are coming from diffusion, notice the direction. Here, language
is the output and vision is the memory. In text-to-image diffusion,
language is the condition and vision is the output. Same family of
"one modality attends to the other." Opposite arrows. Histories that
treat those arrows as unrelated are leaving a tool on the table.

I do not need you to reimplement the 2015 LSTM. I need you to know
that "the model looked at the right region" was already a public
claim, with figures, in the captioning literature, six years before
CLIP's paper and seven years before Stable Diffusion's weight dump.
Looking is old. Scaling is new.

---

**Stage:** draft. **Claim type:** public-record recap. This piece does
not propose a new method or a new research result.
