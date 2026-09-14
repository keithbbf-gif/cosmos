---
id: "46"
slug: gato-and-the-everything-is-tokens-aesthetic
title: Gato and the everything-is-tokens aesthetic
stage: 09-aftermath
stage_title: Aftermath and historiography
status: draft
voice: human
novelty_safe: true
public_record_only: true
primary_public_sources:
  - "Reed et al., A Generalist Agent (Gato), DeepMind, 2022"
  - "Related public neighbors: Perceiver / Perceiver IO; later 'generalist' papers as a class"
does_not_claim:
  - "that Gato is the hidden architecture of any later product"
  - "unpublished DeepMind agent stacks"
last_reviewed: 2026-09-14
---

# Gato and the everything-is-tokens aesthetic

Gato (Reed et al., DeepMind, 2022) is not a pretty-picture paper and not a chat paper. It is a **mood**. One transformer, many tasks: caption a picture, play Atari, stack a block with a robot arm, chat a little. Tokenize the observations and actions until they look like a language. Train. The public object is a generalist agent that is not, in the tables, the best specialist at most of the jobs. The point was the single body.

I put this in aftermath because it is a historiographic temptation. Once you have seen Gato, you can rewrite 2021–2024 as a march toward one sequence model that eats every sense and emits every verb. Gemini’s native slogan likes that rewrite. PaLM-E likes a piece of it. Discrete image tokens like a piece of it. A careful reader should resist the march. Marches are how you erase the joints that actually shipped.

What Gato got right, in public: **tokenization is a diplomatic act**. A button press, a joint angle, a patch, a word — if you can emit them from one softmax, you can share a memory. That is a real research aesthetic. It is the autoregressive-picture bet generalized until it becomes a worldview. Worldviews are allowed in papers. They become dangerous in histories when they turn into destiny.

What the product path actually did, in public, was **stack specialists with glue**. CLIP is a specialist space. A UNet is a specialist denoiser. A LoRA is a specialist delta. A ControlNet is a specialist spine. An LLM is a specialist speaker. LLaVA is glue. City B is a junk drawer of specialists. City A hides the junk drawer behind an API. Neither is Gato. Both sometimes *talk* like Gato in keynotes.

Why the mood did not win 2022’s consumer war: because a 1.2B-class generalist (the ballpark the paper discusses; I will not pretend a precise count is the point) that is okay at many things loses to a specialist that is stunning at one thing people will pay for or screenshot. Midjourney is not a generalist agent. It is a taste. Stable Diffusion is not a robot policy. It is a file. The aesthetic of one body is a researcher luxury until the body is huge and the data is mixed with more care than a 2022 agent paper could afford in public.

2024–2026 products will keep rhyming with Gato anyway. A single assistant that looks, hears, writes, sometimes makes a picture, sometimes calls a tool — that is a *product* generalist. Under the product, there may be one model or five. We often cannot see. So Gato’s historical role is not “ancestor of the stack.” It is **ancestor of the sentence we use when we cannot see the stack**. “It’s all tokens.” Sometimes it is. Sometimes it is a diffusion model in the next room.

Perceiver and Perceiver IO, and Flamingo’s resampler, belong in this mood’s family: collapse a messy input into a fixed token budget. The family is about **interfaces**, not about one loss. I would rather a history of interfaces (prefix, xattn, space, clock, hub) than a history of a destiny.

A labeled reading: Gato is the paper I reread when I catch myself writing “then multimodal was solved by scale.” It was not. A generalist that shares weights across a robot and a captioner is a *bet about transfer*. Some transfer happens. A lot of the 2022–2024 transfer that mattered was cruder: take the CLIP tower, don’t train it, spend your compute on glue. Crude transfer moved the floor. Elegant generalism moved the talk.

If a later editor wants to cut one draft from this series to save a reader time, do not cut this one. Cut a precursor if you must. This is the warning about a clean story.

Last draft: the warning about the whole folder. We are writing too early. Here is what we cannot know, and a reading list that stays on the public record.
