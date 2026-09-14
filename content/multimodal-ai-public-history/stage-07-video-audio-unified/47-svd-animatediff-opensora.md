---
id: mmh-47
title: "SVD, AnimateDiff, Open-Sora: video diffusion you could run"
slug: svd-animatediff-opensora
series: multimodal-ai-public-history
stage: draft
status: staged
publish: false
novelty: public-record
era: "2023-2024"
topics: [SVD, AnimateDiff, Open-Sora, video-diffusion]
voice_check: edited
---

# SVD, AnimateDiff, Open-Sora: video diffusion you could run

Blattmann, Dockhorn, Kulal, Mendelevitch, Kilian,
Lorenz, Levi, English, Voleti, Letts, et al.'s
*Stable Video Diffusion* (December 2023 paper
and weights) is the named Stability line: take
a latent image model, add temporal layers, train
on video, release image-to-video checkpoints.
Guo, Yang, Rao, Agrawala, Lin, and Dai's
*AnimateDiff* (arXiv:2307.04725, 2023) is the
adapter version: a motion module you plug into
a frozen text-to-image UNet so existing
personalization files can move. Open-Sora
(2024, HPC-AI and collaborators) is an explicit
public attempt to approximate a closed video
system with open code and a training story.

These three are not "Sora." They are the
**runnable video column**. That column is the
one this set can describe without pretending
to have been in a closed preview.

What they taught in public:

- **Temporal layers are a part.** Once
  AnimateDiff existed, motion was a file, like
  LoRA was a file. The file culture migrated.
- **Image-to-video is easier to ship than
  text-to-video.** SVD's public emphasis on
  a still as a condition is an honesty about
  controllability and about data.
- **Open video is a compute wall.** The copies
  say so. Short clips, modest resolution,
  visible artifacts. The artifacts are
  historical. They are what 2024 open compute
  bought.

I will not list every AnimateDiff checkpoint
name. I will say the motion-adapter plus
SD1.5/SDXL ecosystem was how a lot of people
first made a two-second loop. Loops are not
cinema. They are the 2023 public object.

A reader comparing these to the next draft's
announced systems should keep the same three
columns used for ALIGN versus CLIP: method
paper, product demo, downloadable file. Open-
Sora argues in the third column. Sora's
February 2024 page argued in the second.
Mixing the columns is how a timeline becomes
a brand war.

---

**Stage:** draft. **Claim type:** public-record recap. This piece does
not propose a new method or a new research result.
