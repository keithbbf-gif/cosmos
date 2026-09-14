---
id: "20"
slug: when-diffusion-beat-gans
title: When diffusion beat GANs
stage: 04-diffusion-mechanics
stage_title: Diffusion mechanics
status: draft
voice: human
novelty_safe: true
public_record_only: true
primary_public_sources:
  - "Dhariwal and Nichol, Diffusion Models Beat GANs on Image Synthesis, NeurIPS 2021"
  - "Brock et al., BigGAN; Karras et al., StyleGAN line (as the public GAN peak)"
  - "Nichol and Dhariwal, Improved DDPM, 2021"
does_not_claim:
  - "that GANs ended"
  - "that FID is a complete verdict"
last_reviewed: 2026-09-14
---

# When diffusion beat GANs

The title is the paper’s title. I am stealing it because it was a public act. Dhariwal and Nichol, 2021, ADM — an ablation-heavy UNet diffusion model — reported image synthesis numbers that sat on top of the GAN numbers people had been treating as the ceiling. ImageNet class-conditional samples. FID. They also argued, with the confidence of people who had looked at a lot of pictures, that the samples were not only better-scoring but better.

I was trained, like everyone, to flinch at “beats.” Beats on which FID. Beats with how much compute. Beats with a classifier to guide the sampler (they used classifier guidance; classifier-*free* is the next draft’s cousin). The flinch is healthy. The event is still real. A monopoly of *look* broke. For five years, if you wanted a sharp, stylish fake face or a sharp ImageNet object, you were in GAN country unless you were a likelihood person with modest ambitions. After ADM, you could be a diffusion person with immodest ones.

What did they actually change, in public?

They treated the UNet as a thing you scale and ablate, not as a default from the DDPM paper. Architecture mattered: residual blocks, attention at certain resolutions, the usual bag, done with care. They treated **guidance** as a way to trade diversity for fidelity — push the sample toward a class. They wrote in a dialect the GAN people could hear: show the pictures, show the FID, show the nearest neighbors so you cannot be accused of copying the training set too lazily.

GANs did not die. StyleGAN3 and the later style literature kept going. GAN inversion, GAN editing, the whole “W space” craft — that is a parallel city that still has residents. What died was the assumption that *if you want the pretty sample, you must live with an adversary*. That assumption had organized a lot of careers. You can feel the reorganization in 2022 hiring and in 2022 arXiv titles. I will not quantify it. I will say it was visible.

There is a cruelty in leaderboard revolutions. A lot of hard GAN work became, overnight, “previous.” Some of that work is still the reason we know how to look at a generated face and say the teeth are wrong. Diffusion inherited a visual culture that GANs had already trained into reviewers. The metrics were GAN-era metrics. Draft 45 is about that hangover. Here I only want the irony: diffusion “beat” GANs *on GAN’s exam*.

Improved DDPM, earlier in 2021 from overlapping authors, is the quieter sibling: learning the variance, tweaking the schedule, making the likelihood and the samples less at war. I mention it so ADM does not look like a single leap from the 2020 skeleton. There was a year of making diffusion *not slow and not dull*. The year is public. The dullness was the 2020 samples compared to a BigGAN. The not-dullness is ADM’s ImageNet plates.

Why this draft sits before CLIP-conditioned generation: because the field had to believe diffusion could make a *class-conditional* picture before it could believe it could make a *sentence-conditional* one. Class is a cheap sentence. “Class 292” is “a photo of a lion, I guess.” GLIDE will type the real sentence. Imagen will type it into a large language model first. The permission starts with 292.

A human memory of the GAN years I will allow myself: the pictures had a glaze. Even when they were good, they had a glaze. Diffusion’s early good pictures had a different glaze — a photographic one, sometimes a little muddy, sometimes uncannily ordinary. Ordinary was the shock. GANs had taught us that fakes would look like fashion. Diffusion taught us that fakes might look like a file you forgot you took.

That ordinary look is one reason the 2022 ethics conversation landed harder. A StyleGAN celebrity face was already a genre. A diffusion photograph of a place that does not exist is a different social object. ADM did not cause that. ADM made it plausible.

Next: the knob that turned plausible into *punchy* — classifier-free guidance — which most people who used Midjourney never named and used anyway.
