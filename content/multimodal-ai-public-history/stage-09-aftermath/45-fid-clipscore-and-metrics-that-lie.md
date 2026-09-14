---
id: "45"
slug: fid-clipscore-and-metrics-that-lie
title: FID, CLIPScore, and metrics that lie
stage: 09-aftermath
stage_title: Aftermath and historiography
status: draft
voice: human
novelty_safe: true
public_record_only: true
primary_public_sources:
  - "Heusel et al., FID (GANs trained by two time-scale update rule), 2017"
  - "Hessel et al., CLIPScore, 2021"
  - "Salimans et al., Inception Score (predecessor); later public critiques of FID"
  - "Human preference studies as reported in Imagen / DALL·E 2 / academic user studies"
does_not_claim:
  - "that any one metric should be banned"
  - "a new evaluation method"
last_reviewed: 2026-09-14
---

# FID, CLIPScore, and metrics that lie

A field that cannot score cannot choose. A field that scores badly will choose a look.

**FID** — Fréchet Inception Distance — is a GAN-era metric that survived into the diffusion years because everyone already had the script. Embed real images and fake images with an Inception network trained on ImageNet, fit a Gaussian to each cloud, measure a distance. Lower is “better.” The number licensed a lot of 2021–2022 claims, including claims I have already repeated as claims. I use it with gloves.

The gloves: Inception-ImageNet is a particular eye. It likes a certain spatial statistics, a certain kind of object-centered photograph. A model can learn to please that eye and look worse to a person, or look better to a person and lose the number. Text following is almost invisible to FID. You can match COCO’s *texture cloud* and ignore the caption. You can also overfit the COCO validation look. The metric was built to compare unconditional or class-conditional generators. We used it anyway, because the alternative was “look at the appendix.”

**Inception Score** is the older sibling, even ruder: it wants fakes that an ImageNet classifier is confident about, and diverse in class. Confidence is not truth. A fried CFG picture can be confident.

**CLIPScore** (Hessel et al., 2021) and the family of CLIP-based similarities are the multimodal correction: does the picture match the *sentence*? This is the right question. It is also a closed loop. We trained CLIP on web pairs. We train generators on web pairs (or on LAION, which is CLIP-filtered). We score the generator with CLIP. A model that copies the web’s pairing habits will look like a genius to CLIP. A model that obeys a human’s unusual sentence may look worse. And a model that learns to **adversarially please CLIP** — the 2021 VQGAN-CLIP look — can max a cosine and look like a fever.

I said in draft 15 that I missed sorted lists. CLIPScore is a sorted list collapsed into a brag. The runner-up is gone. The human is gone.

Human preference is the honest expensive thing. Imagen’s rater studies, DALL·E’s, academic pairwise tests, later arena-style leaderboards for pictures and for VLMs. Labor. Disagreement. Instructions that leak. A rater who prefers pretty to prompt-true will invent a pretty field. A rater who prefers prompt-true will invent a pedantic field. Both happened. I do not throw out human studies. I want their **instructions published**, which they sometimes are not.

VLM benches have their own lies. Short-answer VQA hides fluency. Long-answer “GPT-4 as judge” hides sycophancy. Contamination hides in the pretraining soup — and we cannot see the soup. A novelty-safe evaluation sentence in 2026 has to include: **we do not know if the exam was in the meal.**

Why this draft is aftermath, not methods: because the metrics *shaped the history*. ADM beat GANs on FID and the fashion moved. Imagen reported FID and preference and the press moved. Open models optimized for the look that won screenshots, which is a human metric with a like button. We do not get to pretend the science was elsewhere and the culture was decoration. The score *was* the culture.

A practice I will keep in this series, and that I want a later editor to keep: when I repeat a number, I name the **exam and the interested party**. “Authors report FID 7.27 on COCO” is a sentence. “Imagen is more photorealistic than DALL·E 2” is a different sentence. The first can be cited. The second needs raters, a protocol, and an opponent who was allowed to pick their own samples. If I slid between those sentences earlier, pull me back.

There is no clean replacement I am allowed to invent here. That would be original research. The historical claim is smaller: **the 2021–2024 boom ran on borrowed exams**, some from ImageNet, some from CLIP, some from a crowd on a Tuesday. Borrowed exams are how you get a fast decade. They are also how you get a look you cannot defend.

Next: a 2022 research mood that tried to throw out the borrowed exam and the separate model — everything is a token, one policy, Gato — and why that mood did not become the product path even when it became a slogan later.
