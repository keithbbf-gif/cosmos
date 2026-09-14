---
id: mmh-16
title: "What CLIP released, and what it locked"
slug: clip-what-was-released
series: multimodal-ai-public-history
stage: draft
status: staged
publish: false
novelty: public-record
era: "2021"
topics: [CLIP, openai/CLIP, WIT, weights]
voice_check: edited
---

# What CLIP released, and what it locked

A paper can be public while a dataset stays closed. CLIP is the
teaching example. The 2021 paper, the blog post, the GitHub
repository `openai/CLIP`, and several pretrained image encoders
(ResNet and ViT variants) went out. The WIT collection — WebImageText,
the 400 million pairs — did not. That split is not a rumor. It is
the release.

Why the split matters for this history:

- **Reproduction became a research program.** OpenCLIP, LAION,
  and later DataComp are public answers to a locked set. They do
  not claim to be WIT. They claim to be *a* web image-text set
  you can train on. The difference is the whole point.
- **Downstream work froze around the released towers.** Thousands
  of papers say "we use CLIP ViT-L/14" the way an older literature
  said "we use ResNet-50 pretrained on ImageNet." A frozen encoder
  is a social fact. It is also a scientific risk: the field
  overfits a few public checkpoints.
- **You cannot audit what you cannot list.** Critiques of CLIP's
  training data are critiques of a *distribution inferred from
  behavior*, plus whatever the paper disclosed (queries, filtering
  notes). That is weaker than an audit of files. It is what the
  release allowed.

The model card and the repository README are primary pages. They
tell you how to embed an image, how to embed a text, and that the
similarity is a cosine with a temperature. They do not give you
the pair list. A responsible recap keeps that sentence in the
body, not in a footnote.

Neighbors in the same week complicate the myth of a single
opening. DALL·E 1's blog post shares the 5 January 2021 dateline.
One post is a generative demo with no public weights of the full
system. The other is a discriminative model with weights. Public
does not mean "everything." Public means "this object, on this
URL, on this day."

Later Stable Diffusion model cards will say, in writing, that the
text encoder is a CLIP ViT-L/14. That sentence is only possible
because the CLIP *tower* was a released artifact. The 22 August
2022 diffusion dump spends a 2021 contrastive dump. Locked data,
open encoder, then open denoiser: three different doors. This
draft exists so a reader does not call all three "open AI."

---

**Stage:** draft. **Claim type:** public-record recap. This piece does
not propose a new method or a new research result.
