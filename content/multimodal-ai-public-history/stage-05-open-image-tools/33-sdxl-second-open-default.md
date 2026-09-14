---
id: mmh-33
title: "SDXL: the second open default"
slug: sdxl-second-open-default
series: multimodal-ai-public-history
stage: draft
status: staged
publish: false
novelty: public-record
era: "2023"
topics: [SDXL, Podell, Stability, refiner]
voice_check: edited
voice_check_date: 2026-09-14
---

# SDXL: the second open default

Podell, English, Lacey, Blattmann, Dockhorn, Müller,
Penna, and Rombach's *SDXL: Improving Latent Diffusion
Models for High-Resolution Image Synthesis*
(arXiv:2307.01952, July 2023) is the public paper for
the checkpoint that replaced v1.5 as the thing a lot
of open tools assumed. Larger UNet. Two text encoders
(CLIP ViT-L and OpenCLIP ViT-bigG). Conditioning on
size and crop parameters so the model knows what
resolution it is being asked for. A separate refiner.
Weights released. A model card again more useful than
the launch thread.

Why "second default" is the right phrase:

- **UIs retargeted.** ControlNet, LoRA trainers, and
  workflow graphs grew XL versions. That retargeting
  is the social proof of a default.
- **The text handle got wider.** Two encoders are an
  admission that a single CLIP L/14 was a bottleneck.
  The admission is in the architecture, not in a
  keynote.
- **1024×1024 became ordinary** in the open stack,
  after a year of 512×512 and latent upscalers.

The refiner is easy to mythologize. It is a second
diffusion stage that spends steps on high-frequency
detail. Some users loved it. Some skipped it. The
paper's job is to describe it. The community's job
was to argue. Both are public.

SDXL does not retire the 22 August 2022 event. It
**inherits** it: same lab lineage, same latent-plus-
text recipe, same open-checkpoint culture, new
capacity. A history that only has v1.4 is stuck in
the first weekend. A history that starts at XL
forgets why the ecosystem existed to receive XL.

I will not rank XL against Midjourney or DALL·E 3.
Those are different release policies and different
interfaces. What I will say: in the *open-weights*
column, SDXL was the 2023 workhorse, the way v1.4/v1.5
was the 2022 workhorse. Workhorses are historical
objects. Leaderboard winners sometimes are not.

---

**Stage:** draft. **Claim type:** public-record recap. This piece does
not propose a new method or a new research result.
