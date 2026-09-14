---
id: "17"
slug: vqvae-vqgan-image-as-vocabulary
title: VQ-VAE, VQGAN, and the image as a vocabulary
stage: 03-discrete-generation
stage_title: Discrete generation
status: draft
voice: human
novelty_safe: true
public_record_only: true
primary_public_sources:
  - "van den Oord et al., Neural Discrete Representation Learning (VQ-VAE), NeurIPS 2017"
  - "Razavi et al., VQ-VAE-2, NeurIPS 2019"
  - "Esser, Rombach, Ommer, Taming Transformers for High-Resolution Image Synthesis (VQGAN), CVPR 2021"
does_not_claim:
  - "unpublished codebook training recipes"
  - "that all later latents are VQ"
last_reviewed: 2026-09-14
---

# VQ-VAE, VQGAN, and the image as a vocabulary

Pixels are a terrible alphabet. Too long, too correlated, too low-level. If you want a transformer to write a picture the way it writes a paragraph, you need a shorter string that still decodes into something a person will accept as the picture. That object is a **codebook**.

VQ-VAE, in 2017, is the public name I will use for the modern version of the idea. An encoder emits continuous vectors. Each vector is snapped to the nearest entry in a learned dictionary. The decoder sees only the snapped entries. A separate prior (in the original story, a PixelCNN; later, a transformer) models the sequence of dictionary indices. The picture has been given a vocabulary. The vocabulary has been given a language model.

VQ-VAE-2 stacked the idea, hierarchical, more detail. It made faces and ImageNet samples that, in 2019, looked like a GAN competitor if you squinted. It did not, by itself, change popular culture. It changed what people who wanted discrete generation were allowed to hope.

VQGAN, Esser, Rombach, and Ommer, public in the 2020–2021 window and at CVPR 2021, is the codebook that a lot of *humans* actually met. They trained the autoencoder with a perceptual and adversarial diet so that the discrete latents decoded into sharp, plausible images, then put a transformer on the indices. The paper’s title is the tell: *Taming Transformers for High-Resolution Image Synthesis*. The transformer was already the celebrity. The codebook was the leash.

I met VQGAN the way a lot of non-authors met it: through notebooks that paired it with CLIP. The codebook made a generator you could optimize or sample; CLIP made a critic you could type at. The joint was improvised and public. It is easy, after Stable Diffusion, to treat that summer as a prehistory of latent diffusion. Please don’t. VQGAN is a GAN at the decoder and a transformer at the prior. Latent diffusion will throw away the discrete snap for a continuous latent and throw away the adversarial decoder-loss as the main story. Same labs, overlapping authors (Rombach, Esser), different physics. Continuity of people is not continuity of method. I will get to that honesty again in draft 24.

Why the vocabulary idea keeps surviving even when the popular generator is not discrete:

Because language models want tokens. If your product plan is “one model, many modalities,” a codebook is a diplomatic passport. Gemini’s public technical report talks about discrete image tokens in the native-output story. DALL·E 1 already lived there. Muse and Parti lived there. Masked token models have advantages you can explain in a meeting: you can decode in parallel, you can edit a subset. Diffusion has advantages you can explain in a different meeting: a natural way to add noise as data augmentation, a natural slider for quality vs speed, a literature that exploded.

The codebook has a known vice, public and stubborn: **the snap**. The index is not the vector. You lose the leftover. Sometimes the leftover is texture. Sometimes it is text rendered in the image, which is why so many early discrete models wrote unreadable letters. Later tokenizers got better; I will not invent their recipes. The vice is the historical object.

A human note. “Vocabulary of images” sounds poetic and is, in practice, a spreadsheet of embeddings and a commitment to a resolution. 16×16 tokens, 32×32 tokens, a face that will never be sharper than the decoder. People who dreamed of infinite resolution in 2021 were not dreaming in this school. They were dreaming in the GAN school or in the “we will cascade” school. Both dreams show up in 2022.

If you take one thing: **tokenization is a multimodal decision**. You are deciding what counts as an atomic unit of a picture. Patch embeddings (ViT) are a tokenization for understanding. Codebook indices are a tokenization for writing. They look similar on a whiteboard. They are trained for opposite verbs. Confusing the verbs is how you get a paper that claims unification and a demo that can only do one.

Next: what it feels like, as a public event, to run next-token prediction on those indices — the autoregressive picture — and why that path lost the popular 2022 war without dying.
