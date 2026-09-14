---
id: mmh-20
title: "CLIP as a frozen encoder: when a paper becomes a part"
slug: clip-as-frozen-encoder
series: multimodal-ai-public-history
stage: draft
status: staged
publish: false
novelty: public-record
era: "2021-2023"
topics: [CLIP, frozen-encoder, unCLIP, Stable-Diffusion]
voice_check: edited
---

# CLIP as a frozen encoder: when a paper becomes a part

By late 2021 a pattern is public: do not train a visual
backbone if you can freeze CLIP. Style-transfer repos embed
images. Retrieval demos embed images. Diffusion papers condition
on CLIP text embeddings. UnCLIP (DALL·E 2, Ramesh et al., 2022)
generates a CLIP *image* embedding and then decodes it.
Rombach et al.'s latent diffusion, in the Stable Diffusion
configuration, freezes a CLIP text encoder and trains a UNet
to respect it. The 2021 matching game has become a **part**.

This is ordinary engineering, and it is a historical event.
ImageNet-pretrained ResNets were parts. BERT was a part. CLIP
joined that shelf. Once a part exists, papers get shorter in
the vision section and longer in the loss section. "We use
CLIP" stops being a contribution and starts being a
materials-and-methods line.

Consequences that showed up in public, not in folklore:

- **The text tower is a bottleneck.** If CLIP cannot embed a
  concept, the denoiser has a hard time painting it. Later
  SDXL and SD3 papers will talk about larger or different
  text encoders for a reason.
- **Image embeddings become a language.** UnCLIP's prior is
  a model of CLIP space. That is a strange sentence if you
  still think CLIP is only a classifier.
- **Evaluation leaks.** If your retrieval metric is CLIP
  similarity and your generator was guided by CLIP, you are
  talking to yourself. The field noticed. It did not always
  stop.

LiT (Zhai et al., 2022) is a useful public cousin: lock the
image tower, train the text tower, save compute. BLIP-2 will
lock both an image encoder and a language model and train a
thin connector. The frozen-part genre is bigger than CLIP.
CLIP is the part that escaped the paper.

I want a reader to feel the *humility* of this moment, not
just the hype. A lot of 2022–2023 multimodal systems are
composition. Composition is not theft and it is not a
miracle. It is what a field does when a public encoder is
good enough and compute is not free. The next stages will
look like new art. Under the art, a cosine.

---

**Stage:** draft. **Claim type:** public-record recap. This piece does
not propose a new method or a new research result.
