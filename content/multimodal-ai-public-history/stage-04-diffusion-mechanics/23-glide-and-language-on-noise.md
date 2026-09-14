---
id: "23"
slug: glide-and-language-on-noise
title: GLIDE, and language on the noise
stage: 04-diffusion-mechanics
stage_title: Diffusion mechanics
status: draft
voice: human
novelty_safe: true
public_record_only: true
primary_public_sources:
  - "Nichol et al., GLIDE: Towards Photorealistic Image Generation and Editing with Text-Guided Diffusion Models, arXiv:2112.10741"
  - "OpenAI GLIDE blog / filtered model release notes (public 2021–2022)"
does_not_claim:
  - "the unreleased unfiltered GLIDE"
  - "identity with DALL·E 2"
last_reviewed: 2026-09-14
---

# GLIDE, and language on the noise

GLIDE is the paper where OpenAI, in public, puts a **text condition on a diffusion model** and shows photorealistic generation and inpainting. December 2021 on arXiv. Authors overlapping the ADM world. The title is doing a lot of work: *towards* photorealistic, *text-guided*, *editing*. Not a brand. A direction.

The public method, said roughly: a diffusion model that can hear tokens. They compare CLIP guidance (use a CLIP to steer samples) with classifier-free guidance on a text-conditional diffusion model, and they report that the latter can look better in their evaluations. I will not restage the table. I will restage the fork. CLIP-as-critic, which the community already loved, versus a denoiser that was *trained* to hear the sentence. The second object is the one that will eat 2022.

They also talk about **editing**: inpaint a region, use the text to fill. That is a different social object from “make me an avocado chair.” It is “change this poster in my photograph.” The later product fights about likeness and about photos of real people are already implied. A model that can edit is a model that can be asked to lie about a particular picture, not only about a particular noun.

The release story is part of the history. OpenAI released a **filtered** smaller GLIDE, and wrote about not releasing the largest, least-filtered thing. The filter is a public decision: they did not want a photorealistic, freely downloadable generator of certain categories of harm. You can agree or not. You cannot say the decision was hidden. 2022 will make the opposite decision in a different lab (Stability, CompVis, Runway, the LAION stack) and the decade will argue about both. I am not the argument. I am the reminder that **GLIDE’s paper is already an ethics paper** in its release section, before Twitter made it a war.

GLIDE is also, in retrospect, a stepping stone the authors almost tell you is a stepping stone. DALL·E 2 arrives a few months later with CLIP latents and a different diagram. People who only remember DALL·E 2 treat GLIDE as an internal draft. It was not. It was a public preprint with a filtered weight. Historians of open-source will care that the filtered weight existed: it was one of the first *official* text-to-image diffusion artifacts you could poke, even if it was not the pretty one.

Photorealism as a goal is worth a flinch. ADM had already made ordinary-looking ImageNet objects. GLIDE wants ordinary-looking *prompted* objects. Ordinary-plus-prompt is how you get both the wonder and the scam. A drawing model can be dismissed as style. A photograph model has to be argued with. GLIDE’s authors knew that; the filter is the evidence.

I want a small architectural honesty. “Text-guided diffusion” can mean cross-attention, or it can mean a pooled embedding injected like a class label, or it can mean CLIP guidance at sample time. The GLIDE paper discusses more than one. Later open models made **cross-attention over token embeddings** the folk default (the LDM paper’s conditioning story). If you flatten all of that into “they added text,” you will not understand why some models spell and others don’t, why some follow word order and others follow a bag of nouns.

GLIDE did not, by itself, make the 2022 look. It made the 2022 *research object* legitimate: a denoiser that listens. Imagen will listen through a frozen language model. Stable Diffusion will listen in a latent space. DALL·E 2 will listen through CLIP. All of those are dialects of the same permission. This paper is the permission slip with an OpenAI letterhead.

Next: the dialect that made a consumer GPU relevant — do not denoise in pixel space. Denoise in a smaller room.
