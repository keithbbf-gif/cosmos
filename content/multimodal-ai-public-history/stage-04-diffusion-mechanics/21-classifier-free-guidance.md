---
id: "21"
slug: classifier-free-guidance
title: Classifier-free guidance
stage: 04-diffusion-mechanics
stage_title: Diffusion mechanics
status: draft
voice: human
novelty_safe: true
public_record_only: true
primary_public_sources:
  - "Ho and Salimans, Classifier-Free Diffusion Guidance, NeurIPS 2021 workshop; later arXiv versions"
  - "Dhariwal and Nichol, ADM (classifier guidance as the named predecessor)"
  - "Public Stable Diffusion / Imagen / GLIDE papers noting CFG as a sampling knob"
does_not_claim:
  - "undisclosed industrial guidance recipes"
  - "that CFG is the only reason pictures got pretty"
last_reviewed: 2026-09-14
---

# Classifier-free guidance

If I had to pick one technical object that civilians used without naming, it would be this.

Classifier-free guidance, Ho and Salimans, public in the 2021 workshop window and then as a paper people actually cited: you train a diffusion model to denoise **with** a condition and **without** it. At sampling time you run both, and you extrapolate. You take the unconditional direction and you step past the conditional one, by a scale. The scale is a number. In user interfaces it became “guidance” or “CFG” or a slider that said nothing.

The predecessor is classifier guidance in ADM: train a separate classifier on noisy images, use its gradient to push the sample toward a class. That works. It also means you maintain a classifier that must live at every noise level. Classifier-*free* says: drop the extra net. The generative model can *be* its own classifier if you sometimes hide the condition during training. Hide the text. Hide the class. The model learns a fork. Sampling is a walk that leans on the fork.

I think this is the hinge of the pretty-picture year, and I will label that as a reading. You can get images out of a diffusion model without it. They are often duller, more generic, more willing to ignore your sentence. You turn the scale up and the sentence bites. You turn it up too far and you get the fried look: oversaturated, extra limbs, a prompt followed so hard it breaks anatomy. Every public UI taught this folklore in a week, usually without citing Ho and Salimans.

Why “classifier-free” as a name? Because it is defined against ADM’s classifier. The name is for researchers. Users needed a feeling: *more like what I said*. That feeling is not fidelity to the world. It is fidelity to a **condition**. Those diverge. A model can be very faithful to “a red cube on a blue sphere” and still invent a cube that could not sit. CFG does not know the difference. It knows the score.

Imagen’s public paper talks about the scale. GLIDE’s paper talks about guidance. Stable Diffusion’s community made `scale=7.5` a kind of folk constant, then argued about it every month. I will not bless 7.5. I will say that **a single scalar becoming a folk constant** is a sign you are looking at a real interface, not only a real paper.

There is a philosophical smallness here that I like. The model is not “more creative” at high guidance. It is more *obedient to a difference*. The difference is “what I do when I hear the prompt” minus “what I do when I hear nothing.” Obedience to a difference is a good description of a lot of multimodal steering. CLIP guidance was obedience to a cosine. CFG is obedience to a pair of scores. Same social demand: make the picture *more like the words*.

A novelty-safe limit. I do not have the industrial recipes that mix CFG with other guidances, with dynamic scales, with negative prompts (the community trick of guiding *away* from a second sentence). Negative prompts are public folklore from 2022 onward; I will not pin a first tweet. They are CFG’s folk child: if a difference can be extrapolated, a second text can be a thing you subtract.

When later drafts say a 2022 picture “looks like 2022,” they often mean a CFG look without meaning to. Punchy. A little too matching. The avocado armchair of 2021 was a different look — discrete, surprising, sometimes broken in a transformer way. The 2022 look is a denoiser leaning on a sentence. Once you see the lean, you cannot unsee it.

Next: the unglamorous hinge inside the lean — noise schedules, samplers, the stuff nobody wanted to think about and everybody shipped.
