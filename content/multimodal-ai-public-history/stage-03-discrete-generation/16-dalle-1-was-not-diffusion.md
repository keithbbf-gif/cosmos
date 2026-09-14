---
id: "16"
slug: dalle-1-was-not-diffusion
title: DALL·E 1 was not diffusion
stage: 03-discrete-generation
stage_title: Discrete generation
status: draft
voice: human
novelty_safe: true
public_record_only: true
primary_public_sources:
  - "OpenAI DALL·E blog, 5 January 2021"
  - "Ramesh et al., Zero-Shot Text-to-Image Generation, arXiv:2102.12092, ICML 2021"
  - "openai/DALL-E (public dVAE code)"
does_not_claim:
  - "unpublished DALL·E 1 sampling recipes"
  - "that later DALL·E versions share this architecture"
last_reviewed: 2026-09-14
---

# DALL·E 1 was not diffusion

I have to say this in the first sentence because the culture smeared it. The first DALL·E was a transformer over discrete image tokens, trained to generate those tokens from a text caption. It was announced on January 5, 2021, the same day as CLIP. It was not a diffusion model. DALL·E 2, in 2022, would live in a different physics. DALL·E 3, later, would live in a different product. If you say “DALL·E” as if it were one machine, you are talking about a brand, not a method.

The public paper is *Zero-Shot Text-to-Image Generation*. The method, in public, has two stages.

First, a **discrete variational autoencoder** (they discuss a dVAE) that turns a picture into a grid of tokens from a codebook, and back again. The picture becomes something a language model can eat: a sequence.

Second, a **transformer** that sees the caption and then the image tokens, autoregressive, like a GPT that has learned a second alphabet. At inference you type a caption, sample a token grid, decode the grid into pixels.

That is the whole spell. It is the 2015 captioner run in reverse, with a codebook instead of an LSTM over words, and with a lot more compute. The joint is sequential. Text is a prefix. Pixels are a continuation, once pixels have agreed to be tokens.

What the public actually received, in January 2021, was not the spell. It was a blog of carefully chosen samples: an armchair in the shape of an avocado, a snail made of a harp, the kind of compositional dare people used to say neural nets failed. The samples were real enough to rearrange a conversation and not real enough to hold. There was no public weight for the transformer. There was, later, code for the dVAE. The generator you could play with in 2021 was mostly not this model. It was CLIP-guided things, then GLIDE’s limited release, then DALL·E 2’s waitlist, then Midjourney, then the August 2022 weights. DALL·E 1 is a **published existence proof** more than a public instrument.

I still want it in the spine. Because it states, early and out loud, that **text-to-image is a language modeling problem if you are willing to tokenize the image**. A lot of later work — Parti, the Muse line, masked token models, Gemini’s public talk of discrete image tokens — is this bet again, sometimes with better tokenizers, sometimes with parallel decoding instead of left-to-right. Diffusion won the 2022 popular war. The token bet did not die. It went backstage and then returned in product language about “native image generation.”

The paper’s “zero-shot” is not CLIP’s zero-shot. Here it means: the model can compose concepts it was not explicitly trained as a supervised pair, because the language prefix generalizes. Avocado + armchair. The evaluation is a mix of FID-on-COCO style numbers and human looking. I will not pretend those numbers travel cleanly. I will say the rhetorical job they did: convince a reader that this is not a lookup table of memes.

CLIP sits beside DALL·E 1 in the official story as a ranker. The generator proposes. The retriever sorts. Already, on day one, the lab treated contrastive space as a quality knob on a discrete generator. That pairing is more important than the avocado. It is the first time the two 2021 objects are a system.

A novelty-safe pause. I do not know, from the public record, the full data mix of DALL·E 1. I do not know the unpublished sampling tricks that made the blog look like the blog. I know the architecture class, the announcement date, the paper, and the fact that the transformer weights were not a 2021 download. That is enough to stop people from calling it Stable Diffusion’s older brother. It is not. It is Stable Diffusion’s cousin who went to a different school.

Next: the school they both, in different years, had to attend — the codebook. VQ-VAE, VQGAN, the idea that a picture has a vocabulary.
