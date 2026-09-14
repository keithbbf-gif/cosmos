---
id: mmh-26
title: "Imagen and Parti: published methods, withheld checkpoints"
slug: imagen-parti-closed-weights
series: multimodal-ai-public-history
stage: draft
status: staged
publish: false
novelty: public-record
era: "2022"
topics: [Imagen, Parti, Saharia, Yu, Google]
voice_check: edited
---

# Imagen and Parti: published methods, withheld checkpoints

Saharia, Chan, Saxena, Li, Whang, Denton, Ghasemipour,
Ayan, Mahdavi, Lopes, Salimans, Ho, Fleet, and Norouzi's
*Photorealistic Text-to-Image Diffusion Models with Deep
Language Understanding* (Imagen, arXiv:2205.11487, May
2022) and Yu, Xu, Koh, Luong, Baid, Wang, Vasudevan,
Ku, Yang, Ayan, et al.'s *Parti* (arXiv:2206.10789, June
2022) are Google's paired public bets. Imagen: a frozen
large language model as a text encoder, then a cascade
of diffusion models. Parti: a sequence-to-sequence
transformer on discrete image tokens, the DALL·E-1 family
at a different scale. Both papers are detailed. Both
withheld the generators as downloadable weights.

This draft exists to teach a **reading skill**. A PDF can
be generous — architectures, ablations, DrawBench prompt
lists, human preference protocols — and still leave you
unable to run the system. That is not a failure of the
PDF. It is a publication policy. Comparing Imagen's
DrawBench to Stable Diffusion's user memes is a type
error unless you say so.

What the papers contributed even without a hobbyist
checkpoint:

- **Frozen LLMs as text encoders** (Imagen's T5-XXL
  story). Later open models will try smaller T5s and
  multiple text towers. The 2022 claim licensed the
  idea that CLIP text is not the only handle.
- **Cascades.** Generate small, then super-resolve.
  UnCLIP had a related hierarchy. Imagen is explicit
  about the cascade as the system.
- **DrawBench and PartiPrompts.** Evaluation sets with
  named categories (counting, composition, simple,
  complex). They are incomplete. They are better than
  a mood. Open work cited them because they were
  *written down*.

A recap that treats "Google's 2022 models" as one blob
has already lost. Diffusion versus discrete tokens was
still a live fork. The later public default (latent
diffusion, then diffusion transformers and flow) is not
proof that Parti was confused. It is proof that the
open-weights path ran through CompVis and Stability,
whose paper was a latent diffusion paper.

I will not quote cherry-picked photoreal figures as if
they were a census. I will say the 2022 Google papers
raised the **published** quality ceiling and kept the
**runnable** ceiling in other people's repos. Both
ceilings are historical facts.

---

**Stage:** draft. **Claim type:** public-record recap. This piece does
not propose a new method or a new research result.
