---
id: "19"
slug: ddpm-the-slow-idea
title: DDPM, the slow idea
stage: 04-diffusion-mechanics
stage_title: Diffusion mechanics
status: draft
voice: human
novelty_safe: true
public_record_only: true
primary_public_sources:
  - "Sohl-Dickstein et al., Deep Unsupervised Learning using Nonequilibrium Thermodynamics, 2015"
  - "Ho, Jain, Abbeel, Denoising Diffusion Probabilistic Models, NeurIPS 2020"
  - "Song et al., Score-Based Generative Modeling through SDEs, ICLR 2021"
  - "Song & Ermon, NCSN / score matching (2019) as public neighbor"
does_not_claim:
  - "a single inventor of diffusion generative models"
  - "unpublished sampler implementations"
last_reviewed: 2026-09-14
---

# DDPM, the slow idea

In 2020, a paper about adding Gaussian noise to pictures until nothing is left, then training a net to walk the noise back, did not look like a culture-shifting object. It looked like a generative-modeling paper: careful, a bit expensive, a cousin of score matching, with ImageNet and CIFAR tables. Ho, Jain, and Abbeel called it Denoising Diffusion Probabilistic Models. People who liked the lineage pointed at Sohl-Dickstein’s 2015 thermodynamics paper and at Song & Ermon’s score-based work. People who liked GANs pointed at the sampling time and went back to their FID.

I want to stay with the slowness. Not only the sampling slowness — hundreds of steps, a picture that arrives like a developing photograph — but the *intellectual* slowness. Diffusion asks you to believe that a useful model of images is a model of **how images are destroyed**. The network does not write a token. It predicts a noise, or a score, or a slightly less ruined picture, at a given ruin level. The generative act is a chain of small repairs.

That is a weird way to think if you grew up on autoencoders and adversaries. It is a less weird way to think if you grew up on denoising as pretraining (Vincent’s stacked denoising autoencoders, the whole “corrupt and recover” family). Diffusion makes the corruption *the* training distribution. Every noise level is a task. The model is a specialist in leftovers.

The public math comes in more than one dialect. DDPM is a discrete Markov chain with a variational bound that, after some pleasant cancellations, looks like predicting the noise that was added. Song et al.’s SDE paper is a continuous dialect: a stochastic differential equation that noisies the data, another that denoises it, a score network that estimates the gradient of the log-density. I will not pretend these dialects are identical. I will say what a historian can say: **by 2021, a competent reader could see they were in the same city.** Samplers, later, would travel between them (DDIM and the faster paths). The city is what matters.

Why did this feel optional in 2020?

Because the pictures were not yet *steerable by a sentence* in a way a civilian could feel, and because GANs already made sharp faces. A method that takes a second (or many) to sample, to produce something a StyleGAN could spit in one forward pass, needs a different virtue to win. The virtue, in 2020, was mostly “the likelihood story is cleaner” and “mode coverage might be better.” Those are researcher virtues. They are real. They do not ship a Discord bot.

The other reason is fashion. GANs had the journals and the art-world screenshots. Diffusion had a thermodynamics citation. I say this without sneer. Fashion is part of public history. The 2021 paper that will dent the fashion is Dhariwal & Nichol’s *Diffusion Models Beat GANs on Image Synthesis* — next draft — and even that dent was a leaderboard dent. The civilian dent is 2022.

A thing I like about DDPM, as a human reading a methods section: the training loop is almost embarrassingly implementable. Sample an image. Sample a time. Sample a noise. Mix. Ask the net to name the noise. Mean squared error. That loop, plus a UNet with time embeddings, is the skeleton of a year of open repos. GAN training loops, by comparison, were a folklore of collapses and learning-rate folklore. Diffusion’s folklore would come later (guidance scales, samplers, “use this scheduler”). The first loop was simple enough to copy. Copiability is a historical force.

Sohl-Dickstein et al. 2015 deserves the ancestor plaque so 2020 does not look like a creation myth. The idea that you can define a nonequilibrium destruction process and learn a reversal is older than the pretty UNets. What 2020 did was make the reversal *work* on natural images with a recipe other people could train. Working is different from being first. This series is not a patent file. It is a public memory of what worked *out loud*.

Next: the year the leaderboard flipped, and why that flip still was not the avocado armchair.
