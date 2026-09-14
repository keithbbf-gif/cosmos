---
id: mmh-23
title: "Classifier-free guidance: a scalar that became taste"
slug: classifier-free-guidance
series: multimodal-ai-public-history
stage: draft
status: staged
publish: false
novelty: public-record
era: "2021-2022"
topics: [CFG, Ho, Salimans, guidance-scale]
voice_check: edited
voice_check_date: 2026-09-14
---

# Classifier-free guidance: a scalar that became taste

Ho and Salimans' *Classifier-Free Diffusion Guidance*
(NeurIPS 2021 Workshop on Deep Generative Models; later
arXiv:2207.12598) is a small paper with a large afterlife.
Train the denoiser to work with and without the condition
(drop the class or the text some fraction of the time). At
sample time, combine the two predictions so the conditional
direction is exaggerated. No separate classifier. A scale
factor. In the interfaces that followed, that factor is the
slider labeled CFG or "guidance."

The public consequence is that **taste became a number**.
Too low, and the picture ignores you. Too high, and the
picture saturates, duplicates objects, and looks like a
poster that has been sharpened twice. Every 2022 Discord
that shared Stable Diffusion samples argued about 7.5. The
argument is applied aesthetics. The paper is a training
trick plus a sampler equation.

Why it displaced classifier guidance for text-to-image:

- You do not need a classifier in CLIP space or pixel space
  that you trust at every noise level.
- The same network already knows the unconditional score
  if you trained it that way.
- Text conditions are not ImageNet classes. Building a
  good classifier for "a film still of…" is harder than
  dropping the text 10% of the time.

The Stable Diffusion v1.4 model card is explicit: v1.3 and
v1.4 used 10% text-conditioning dropout "to improve
classifier-free guidance sampling." That sentence is how a
workshop paper enters a weight file. Imagen's 2022 paper
also leans on CFG. Once two famous systems name the same
trick, the trick is infrastructure.

A recap should not treat CFG as a solved theory of beauty.
It is a **heuristic steering term**. Later papers will
propose better samplers, dynamic guidance, and
guidance-free distillation. Users will still type 7. Some
defaults outlive their papers. This is one.

If you are reading toward ControlNet and InstructPix2Pix,
notice that those systems still live inside a guided
sampler. They change what the condition is (an edge map, an
instruction). They do not retire the scalar. The scalar is
the culture.

---

**Stage:** draft. **Claim type:** public-record recap. This piece does
not propose a new method or a new research result.
