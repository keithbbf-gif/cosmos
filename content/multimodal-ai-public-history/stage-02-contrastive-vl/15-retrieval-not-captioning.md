---
id: "15"
slug: retrieval-not-captioning
title: Retrieval, not captioning
stage: 02-contrastive-vl
stage_title: Contrastive vision–language
status: draft
voice: human
novelty_safe: true
public_record_only: true
primary_public_sources:
  - "CLIP paper (contrastive retrieval objective)"
  - "Public CLIP-guided generation notes: VQGAN-CLIP (Crowson et al., community), later unCLIP / DALL·E 2 paper"
  - "Radford et al. / Ramesh et al. public statements that CLIP can rank images"
does_not_claim:
  - "that any one community trick is official OpenAI method"
  - "unpublished ranking pipelines"
last_reviewed: 2026-09-14
---

# Retrieval, not captioning

CLIP does not write. I keep repeating that because the culture around CLIP kept trying to make it write.

What it does, if you take the paper at its word, is **retrieve and score**. Give it an image and a pile of strings; it will sort the strings. Give it a string and a pile of images; it will sort the images. The pile can be a dataset. The pile can be a batch of samples from a generator. The pile can be “every frame in this video.” Same joint, different furniture.

This is a different job from Show and Tell. A captioner must commit to words. A retriever must commit to a comparison. Comparisons can be cheap and surprisingly deep. “Which of these 32,768 sentences is the one that belongs?” is a ridiculous-sounding exam that a contrastive model is literally trained to sit. OpenAI’s own DALL·E writeups described using CLIP to rank DALL·E’s generations. That is the official public version of a habit the rest of the internet then made into a folk art.

The folk art, in 2021, had a name people still say with a little affection: **VQGAN-CLIP** and its cousins. Take a generator that can be optimized. Take a CLIP text embedding. Push the image until CLIP says yes. Katherine Crowson and a wider community did this in public, in notebooks, before latent diffusion made the pretty path default. I will not recap every repo. I will say the historical thing: **CLIP became a critic before most people had a decent generator.** The critic was the released object. The generators were whatever you could find.

That inversion explains a year of aesthetics. Early CLIP-guided pictures have a look — saturated, extra eyes if you were unlucky, a kind of over-eager match to every word in the prompt. The look is not “what CLIP sees.” It is what an optimizer does when a cosine similarity is the only teacher. People learned to write prompts that the critic liked. Promptcraft starts here, not in Midjourney, even if Midjourney is where it became a product. Draft 29 will pick that up.

DALL·E 2, in 2022, will make the critic into architecture. unCLIP is a generator that *lives in CLIP image space*: a prior maps text to a CLIP image embedding, a decoder maps that embedding to pixels. I am not stealing that draft. I am pointing at the continuity. Once you believe a CLIP vector is a useful handle on “what the picture is,” you can retrieve with it, rank with it, or decode from it. Three public objects. One joint.

There is a humility in retrieval that generation does not have. A retriever can fail closed: nothing in the pile matches, and you can see the scores sitting in the middle. A generator will still give you pixels. In 2022 the world chose pixels. I do not blame it. I do want the record to show that the 2021 object, the one you could actually download in January, was the one that could say “this, not that.”

Researchers also used CLIP the way they had used ImageNet backbones: freeze it, attach a head, do a downstream task. Linear probes. Fine-tunes. CLIP as a feature. That is retrieval’s quieter cousin — the space as a commodity. It is how a lot of academic work absorbed the paper without absorbing the zero-shot religion. Both absorptions are real. The commodity path is how CLIP entered detectors and video models and, later, the visual tower of almost every open assistant.

A personal prejudice, labeled: I miss the year when the interesting demo was a sorted list. Sorted lists are honest. They show you the runner-up. Generators hide the runner-up in the last step you did not take. When we get to metrics that lie (draft 45), part of the lie will be that we scored generators with a retriever (CLIPScore) and then congratulated ourselves for closing a loop.

Stage 02 closes here. We have a joint space, a silent corpus, open rhymes, industrial twins, and a critic that wants to be a poet. Stage 03 is the other January 2021 object: a model that *does* write pictures, using a vocabulary of image tokens, and is not a diffusion model no matter how many retrospectives smear the decade into one slurry.
