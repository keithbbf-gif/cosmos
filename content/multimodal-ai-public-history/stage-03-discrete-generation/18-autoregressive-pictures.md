---
id: "18"
slug: autoregressive-pictures
title: Autoregressive pictures
stage: 03-discrete-generation
stage_title: Discrete generation
status: draft
voice: human
novelty_safe: true
public_record_only: true
primary_public_sources:
  - "Ramesh et al., DALL·E 1 paper"
  - "Ding et al., CogView, 2021"
  - "Yu et al., Parti (Google), 2022"
  - "Chang et al., Muse (Google), 2023, as a masked-token neighbor"
does_not_claim:
  - "that autoregression 'lost' as a research program"
  - "unpublished sampling speeds"
last_reviewed: 2026-09-14
---

# Autoregressive pictures

Once a picture is a sequence, you can do the oldest neural language trick to it. Predict the next token. Then the next. Left to right, or in some raster order you chose and now have to live with. That is DALL·E 1. That is CogView. That is Parti, Google’s 2022 public bet on a large transformer that writes image tokens from text, with a paper full of samples and a model you could not download.

I want this draft to be about the *feeling* of the bet, not a table.

Autoregression is honest about time. A picture, in this school, has a beginning. Usually the top-left, or a summary token, or a text prefix that owns the first seconds of compute. Errors cascade. A bad token early is a deformed hand later. People who sampled these models in public (when they could) learned to recognize a kind of accumulating tiredness in the image, the way a long GPT sample accumulates tiredness in a paragraph.

It is also honest about **compute at inference**. Every token is a step. High resolution is a long book. The 2022 diffusion models had their own cost — many denoising steps — but they had an industry suddenly obsessed with cutting those steps. Autoregressive image models had a harder popular story: the sequence gets longer when the picture gets bigger, and the transformer’s attention gets more expensive, and your marketing site wants 1024 pixels yesterday. This is not a proof that the bet is wrong. It is a reason the bet lost the *consumer* war of 2022.

Parti is the paper I name so Google does not appear in this history only as Imagen. Imagen is diffusion plus a language-model text encoder. Parti is the token transformer. Same season, two public bets from the same wider institution. That is a useful reminder that 2022 was not a conversion experience. It was a fork. The press followed the fork that had a waitlist and then the fork that had a weights drop. The token fork kept publishing.

Muse, a bit later, is the neighbor that tries to keep the vocabulary and drop the left-to-right tiredness. Masked token modeling: predict many indices at once, iterate. I will not flatten Muse into DALL·E 1. I will say the family resemblance: discrete latents, a transformer, text as condition, no denoising-in-Gaussian-noise story. If your historiography only has room for diffusion, you will misread every later “native image token” product claim as a surprise. It is not a surprise. It is this school wearing a 2024–2025 badge.

Why did civilians experience 2022 as diffusion anyway?

Because the pictures that escaped were easier to make pretty with classifier-free guidance and a UNet (or a latent UNet), because Midjourney and Stable Diffusion were *interfaces*, and because CLIP-space plus latent diffusion produced a look you could iterate on a consumer GPU. Autoregressive models of comparable public prettiness tended to live behind papers and occasional demos. History, for better or worse, is what you can touch.

A technical humility, public: raster order is a fiction. A picture is not left-to-right. Researchers tried spiral orders, unknown-token first, hierarchical tokens (VQ-VAE-2’s instinct). Each order is a different lie about space. Diffusion’s lie is different — a picture is a noise level — and, for a couple of years, a more convenient lie.

I am not picking a winner for 2027. I am picking a memory for 2021. The first widely shown text-to-image transformer was a language model. If we forget that, we will keep being astonished when language models start emitting pictures again, as if the avocado armchair had not already happened.

Stage 04 leaves the vocabulary and enters the other physics: noise, scores, a slow 2020 paper, and the 2021 result that made GANs look optional.
