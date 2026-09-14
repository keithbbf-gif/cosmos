---
id: "22"
slug: noise-schedules-nobody-wanted
title: Noise schedules nobody wanted to think about
stage: 04-diffusion-mechanics
stage_title: Diffusion mechanics
status: draft
voice: human
novelty_safe: true
public_record_only: true
primary_public_sources:
  - "Ho et al., DDPM (linear schedule as a public default)"
  - "Nichol and Dhariwal, Improved DDPM; Song et al., DDIM"
  - "Karras et al., Elucidating the Design Space of Diffusion-Based Generative Models, 2022"
  - "Public sampler names in open repos: Euler, DPM-Solver, Heun, etc."
does_not_claim:
  - "a best schedule"
  - "unpublished production sampler stacks"
last_reviewed: 2026-09-14
---

# Noise schedules nobody wanted to think about

Every diffusion model has a clock. The clock says how ruined the picture is. Training samples a time from that clock. Sampling walks the clock backward. The mapping from “time” to “how much noise” is a **schedule**. The mapping from “this ruin” to “the next slightly less ruin” is a **sampler**.

I did not want to write this draft. That is why it belongs.

In 2020 the schedule was, for a lot of people, a linear or a cosine curve copied from a paper. In 2022 the sampler was a dropdown. Euler. Euler a. DDIM. DPM++ 2M Karras. Names that sound like printer drivers. The dropdown changed hands, faces, whether text in the image was readable, whether the picture looked finished at 20 steps. Users argued about it with the intensity of people arguing about coffee. Most of them, including me at the time, could not have written the ODE.

Karras et al. 2022 is the public adult conversation: the design space can be *elucidated*. Change variables. Separate the training preconditioning from the sampling integrator. A lot of the dropdown folklore is, in that light, people accidentally picking different integrators and different noise parameterizations and calling it “this sampler has better faces.” Sometimes they were right, in the way cooks are right. Sometimes they were changing two things and crediting one.

DDIM, Song et al., deserves a named pause because it made *fewer steps* a research object. If you can treat the chain as a non-Markovian process with the same training, you can jump. The 2022 product era is unthinkable without jumping. Nobody was going to wait for a thousand steps on a GPU under a desk. The open ecosystem spent a year racing the step count down. I will not crown a winner. I will say the race was public and it was the actual deployment story, more than any one UNet block.

Why put this in a *multimodal* history? Because the condition — the sentence — is evaluated *at each step*. A sampler is a policy for how often and how hard the sentence gets to speak. Fast samplers that skip can skip the moment where a small object would have appeared. Slow samplers can overcook a CFG scale. The joint is not only a cross-attention layer. The joint is a clock.

There is also a training-time schedule story: which ruin levels are hard. Too little noise, the model cheats. Too much, the picture is gone and the condition is a rumor. Improved DDPM and later work fiddle this. Latent diffusion fiddles it in a compressed space, which changes what “too much” means. I will not write a tutorial. I will write the historical claim: **a lot of “this model is better at text” was sometimes “this clock spends more time in the band where text is decided.”** That claim is a hypothesis you can find in public threads. Treat it as a hypothesis.

The human part. Schedules are where a field hides its craft when the architecture diagram is already on the marketing site. GANs hid craft in learning rates and augmentation pipelines (Karras’s ADA is a public cousin of this instinct). Diffusion hid craft in clocks. Open-source made the hiding impossible. The dropdown was a confession.

If you are a later reader and you do not want to care: care once. Know that “a diffusion model” is not one object. It is a trained score plus a clock plus a guidance rule plus a step budget. Two products can share a weight and not share a picture, if the clocks differ. That fact broke a lot of naive reproduction. It also made art direction possible. Photographers already knew that development time is part of the picture. We relearned it with a softmax on the time embedding.

Next: the first time a major lab put a *sentence* on this clock in a paper you could read — GLIDE — and said, out loud, that they were filtering the data.
