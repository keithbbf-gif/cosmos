---
id: "09"
slug: contrastive-learning-before-clip
title: Contrastive learning before CLIP
stage: 02-contrastive-vl
stage_title: Contrastive vision–language
status: draft
voice: human
novelty_safe: true
public_record_only: true
primary_public_sources:
  - "Chen et al., SimCLR, ICML 2020"
  - "He et al., MoCo, CVPR 2020"
  - "van den Oord et al., CPC, 2018"
  - "Sohn, InfoNCE lineage; Chopra / Hadsell contrastive roots (public metric learning)"
  - "Zhang et al., ConVIRT, 2020/2022 (medical image–text, cited by CLIP)"
does_not_claim:
  - "a single inventor of contrastive loss"
  - "that SimCLR is CLIP's only parent"
last_reviewed: 2026-09-14
---

# Contrastive learning before CLIP

The contrastive idea is almost insultingly simple when you say it out loud. Take two things that belong together. Pull their representations together. Take things that do not. Push them apart. A batch is a little universe of belongs-together and does-not. The model learns a space where the universe makes sense.

Vision, around 2019–2020, fell in love with a special case: the two things are **two views of the same image**. Crop it twice. Color-jitter one of them. Maybe flip. The “label” is identity. SimCLR made this brutally clear and, with a big batch and a projection head, brutally strong. MoCo made it work with a memory bank and a moving encoder when you could not afford the big batch. CPC and the InfoNCE spelling gave people a loss they could write without blushing. None of this required a sentence.

I remember the mood. Self-supervised vision had been a slightly embarrassed project — pretext tasks that predicted rotation or filled in a patch, clever and a little fake. Contrastive two-view learning felt less fake. The fake part was still there (a crop is not a meaning), but the fake part was *photographic*. The model had to survive a photographer’s choices. That is closer to a real job than “which way is up.”

CLIP’s leap, said in that dialect, is: **the second view can be a sentence.**

Not a crop. Not a color jitter. A string written by some stranger on the internet who wanted a search engine to find their picture. The belongs-together pair is (image, text). The does-not pairs are the other texts in the batch, or the other images. The space that falls out has a property the two-crop space does not: you can enter it from a keyboard.

The CLIP paper is not shy about neighbors. It points at VirTex, ICMLM, ConVIRT. ConVIRT is worth saying twice because it is the same shape in a smaller, cleaner room: paired medical images and reports, contrastive, two towers. The public lesson is that the recipe was already in circulation. What was not in circulation was the willingness to treat the web as the pairing machine, and to evaluate the result as a *zero-shot classifier* rather than as a pretraining for a downstream head.

I want to keep the two-crop work in the story because it explains a habit CLIP inherits. Augmentations still matter. The image tower still has to be invariant to things that should not change the match. Batch size still matters, because the negatives *are* the batch (or the queue). People who only met contrastive learning through CLIP sometimes think the magic is “language.” A lot of the magic is **negative sampling at scale**. Language supplies richer positives. The batch supplies the rest.

There is a human tell in the 2020 papers: they still needed ImageNet linear-probe numbers to be taken seriously. The protocol was: train without labels, freeze, train a linear classifier, report. CLIP keeps a version of that ritual and then walks past it. The walking past is the phase change. A linear probe says the space contains the categories if you are allowed to draw new planes. Zero-shot with prompt templates says the categories are already *named* in the space.

Metric learning, older than all of this, should get a nod so we do not pretend 2020 invented pulling and pushing. Face verification, siamese nets, triplet losses — a decade of “this photo and that photo are the same person.” The new move was using the trick as *pretraining for everything*, then as *the model itself*.

If you want a single sentence to carry forward: contrastive learning taught the field that a pair can replace a label. CLIP believed the pair could be mixed-modality. The next draft is the public paper that made that belief a tool.
