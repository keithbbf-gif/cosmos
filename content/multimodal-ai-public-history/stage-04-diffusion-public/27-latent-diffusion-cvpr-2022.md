---
id: mmh-27
title: "Latent diffusion: compress first, denoise second"
slug: latent-diffusion-cvpr-2022
series: multimodal-ai-public-history
stage: draft
status: staged
publish: false
novelty: public-record
era: "2021-2022"
topics: [LDM, Rombach, CompVis, CVPR]
voice_check: edited
voice_check_date: 2026-09-14
---

# Latent diffusion: compress first, denoise second

Rombach, Blattmann, Lorenz, Esser, and Ommer's
*High-Resolution Image Synthesis with Latent Diffusion
Models* (CVPR 2022 Oral, arXiv:2112.10752, 20 December
2021 — the same day as GLIDE) is the paper under Stable
Diffusion. The move is easy to say and easy to cheapen.
Train an autoencoder that throws away high-frequency
detail you can reconstruct. Run the diffusion process in
that smaller latent. Condition with cross-attention on
whatever you have — class, text, a layout. Decode.

The reason it is a hinge: **pixel-space diffusion at
512×512 was expensive** for the labs that wanted to
release something a single consumer GPU could run. A
latent of, say, 4× downsampling turns the UNet into a
job that fits in the memory numbers later listed on the
v1.4 card (the public release note said 6.9 GB). Method
and product constraint meet in one paper.

The CompVis group is the same circle that had just
published VQGAN. The continuity is public if you read
both PDFs. Discrete codes were one compression. A
continuous latent with a slight KL or VQ regularization
is another. LDM tries several autoencoders. The later
Stable Diffusion v1 stack uses a specific variational
autoencoder and a CLIP text conditioner. The paper is
broader than the celebrity checkpoint. Cite the paper
for the method. Cite the model card for the instance.

Cross-attention as the conditioner matters for the
multimodal story. Text is not concatenated as a class
embedding only. It is a sequence the UNet can attend to
at multiple layers. That is the Show-Attend-and-Tell
arrow pointed the other way, now inside a denoiser.

The GitHub `CompVis/latent-diffusion` predates the
August weight dump. Researchers could already train and
sample LDMs. What August added was a **particular
text-to-image checkpoint** at a particular resolution
on a particular LAION subset. Papers and checkpoints
are different public objects. This draft is the paper.
The next draft is the dump.

---

**Stage:** draft. **Claim type:** public-record recap. This piece does
not propose a new method or a new research result.
