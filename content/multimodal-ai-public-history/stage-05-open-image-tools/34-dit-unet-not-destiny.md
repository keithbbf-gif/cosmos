---
id: mmh-34
title: "DiT: UNet is not destiny"
slug: dit-unet-not-destiny
series: multimodal-ai-public-history
stage: draft
status: staged
publish: false
novelty: public-record
era: "2022-2023"
topics: [DiT, Peebles, Xie, diffusion-transformer]
voice_check: edited
---

# DiT: UNet is not destiny

Peebles and Xie's *Scalable Diffusion Models with
Transformers* (arXiv:2212.09748, December 2022; ICCV
2023) replaces the ADM-style UNet with a transformer
on latent patches. AdaLN conditioning. A class token
or equivalent. Scaling curves that look, on purpose,
like the curves vision transformers taught people to
want. The code went out. The paper is readable in one
sitting if you already know DDPM and ViT.

The historical claim is not "transformers invented
image generation." VQGAN had already put transformers
on codes. The claim is that **the denoiser itself
can be a transformer in a continuous latent**, and
that this is a scaling story rather than a cute
ablation. Later Sora reporting, Stable Diffusion 3's
MMDiT, and a pile of 2024 video papers will sit in
this neighborhood. Those later systems are not DiT.
They are evidence the 2022 bet had a future.

What a recap should keep small:

- DiT's original public experiments are often
  **class-conditional ImageNet**, not a full
  text-to-image product. Do not paste a Sora frame
  into this citation.
- UNets did not vanish on 22 December 2022. SDXL
  is a UNet paper. Both architectures remained
  live.
- "Diffusion transformer" became a phrase that
  papers used more loosely than Peebles and Xie
  did. Read the figure before you trust the
  acronym.

I include DiT so the open-image-tools stage is not
only adapters on a 2022 UNet. The backbone was
already being renegotiated while ControlNet was
being trained. A field can specialize and
re-architect at the same time. Recaps that
serialize everything into a single hero stack
are easier to read and worse as history.

If you need a one-line hinge: after DiT, a
researcher could say "the generator is a
transformer" without meaning "the generator is a
discrete codebook model." That sentence was
expensive to make ordinary. The paper made it
ordinary.

---

**Stage:** draft. **Claim type:** public-record recap. This piece does
not propose a new method or a new research result.
