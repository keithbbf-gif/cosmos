---
id: mmh-21
title: "VQ-VAE and VQGAN: pictures as a codebook"
slug: vqvae-vqgan-discrete-pictures
series: multimodal-ai-public-history
stage: draft
status: staged
publish: false
novelty: public-record
era: "2017-2021"
topics: [VQ-VAE, VQGAN, van-den-Oord, Esser]
voice_check: edited
---

# VQ-VAE and VQGAN: pictures as a codebook

van den Oord, Vinyals, and Kavukcuoglu's VQ-VAE (NeurIPS 2017)
and Esser, Rombach, and Ommer's VQGAN (CVPR 2021,
arXiv:2012.09841) are the public reason a later paper can say
"we generate images like we generate text." You train an
autoencoder whose bottleneck is a **discrete codebook**. A
photograph becomes a grid of integers. A transformer or a
PixelCNN can then model those integers. Decoding paints the
picture back.

DALL·E 1 will use this family. Parti will use this family.
Some unified "any-to-any" 2024 models will still use this
family. Latent diffusion will use a *continuous* latent
instead, but it will still compress first, and the CompVis
group that published VQGAN is the same group that published
the latent diffusion paper. The codebook years and the latent
years are one lab conversation that went public.

What a general reader needs:

- **Compression is a generative method.** If the codebook
  already spent the bits on texture, the sequence model can
  spend its capacity on layout. That split is the 2021 VQGAN
  talk in one sentence.
- **Adversarial loss plus perceptual loss** (VQGAN) made the
  reconstructions look like pictures instead of smears. The
  GAN part is in the name. People who only remember
  "transformer on tokens" skip the reason the tokens were
  worth using.
- **Discrete is a choice, not a destiny.** Diffusion on
  pixels, diffusion on latents, and transformers on codes
  coexist in the 2021–2024 record. Drafts that declare one
  of them "the" image model are picking a fandom.

I am not going to reconstruct DALL·E 1's unreleased stack
from demo videos. The 2021 DALL·E paper (Ramesh et al.,
arXiv:2102.12092) describes a discrete VAE and a transformer
prior. That description is the public object. The VQGAN paper
is the public object you can actually train. Between a
description and a train-able repo sits a lot of later open
work (including CompVis's own taming-transformers).

If CLIP is how text became a handle on an image *embedding*,
VQGAN is how an image became a handle for a *sequence model*.
Both handles are 2021-adjacent. Diffusion will soon offer a
third handle: a noisy latent and a UNet. The rest of this
stage is that third handle going public.

---

**Stage:** draft. **Claim type:** public-record recap. This piece does
not propose a new method or a new research result.
