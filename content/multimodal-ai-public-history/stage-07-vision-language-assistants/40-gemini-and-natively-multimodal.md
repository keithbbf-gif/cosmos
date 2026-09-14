---
id: "40"
slug: gemini-and-natively-multimodal
title: Gemini and “natively multimodal”
stage: 07-vision-language-assistants
stage_title: Vision–language assistants
status: draft
voice: human
novelty_safe: true
public_record_only: true
primary_public_sources:
  - "Gemini Team, Gemini: A Family of Highly Capable Multimodal Models, arXiv:2312.11805 (Dec 2023)"
  - "Google / DeepMind Gemini launch materials, 6 December 2023"
does_not_claim:
  - "unpublished training recipes"
  - "that 'native' has one engineering meaning"
last_reviewed: 2026-09-14
---

# Gemini and “natively multimodal”

December 6, 2023. Google DeepMind launches Gemini and, with the family, a technical report that wants to be read as a paper. Ultra, Pro, Nano. Text, images, audio, video in the public description. A claim that repeats until it becomes a slogan: **natively multimodal**.

I want the slogan unpacked, because this series has been unpacking “multimodal” since draft 01.

In the report’s own telling, Gemini models are trained to take interleaved text and a wide variety of visual (and other) inputs from the beginning, and they can, in the story, emit images via discrete image tokens as well as text. The visual encoding is described as *inspired by* Flamingo, CoCa, PaLI — named debts — with the distinction that the model is multimodal from the start rather than a language model with a tower bolted on. That last clause is the slogan in methods clothing.

What can a public reader actually hold?

We can hold a report with tables, including video and chart and reasoning benches, and a comparison culture that now includes GPT-4V. We can hold a product that, over the following months, did and did not match the report’s atmosphere depending on which Gemini you got. We can hold the architectural *sentence*, not the code. Native, here, is a **training-data and training-time claim** more than a diagram we can inspect. Mixed modalities in the mix from the start. Not “train LLM, freeze, project CLIP, instruct.”

That is a real fork from LLaVA. It is a claimed fork from GPT-4V, whose method we also cannot inspect — so the fork might be narrower than the slogan. Novelty-safe practice: **two illegible objects cannot prove they differ in the way their blogs say.** They can differ in behavior. Behavior is what we have.

The discrete image token output is the DALL·E 1 school waving from inside an assistant. I said this would return. If you generate images as tokens from the same model that talks, you do not need a separate diffusion product *in principle*. In practice, products kept diffusion (or diffusion-like) stacks around for a long time because pretty is a specialist job. The report’s principle still matters for historiography. Unification-of-block plus unification-of-objective is the ambition. Draft 08 warned that unification-of-meaning does not come free. I am not walking that warning back because the report is long.

Audio and video in the *family* description are the stage-08 hunger arriving early. A natively multimodal model that only ever sees still JPEGs is just a VLM with a bigger marketing budget. Gemini’s public story refuses that. Whether every shipped variant lives up to the refusal is a product-by-product question. The story is still a 2023 event.

I want one more Flamingo echo. Interleaving. The strip. Gemini’s report cares about screenshots, PDFs, charts — the leftover channel — and about video as more than a bag of stills. PaLI’s multilingual hunger is in the family too, at least as a claim. If you have read this series in order, the report should sound like a chorus of earlier papers, not like a new physics. That is not an insult. Choruses are how labs talk when they have been paying attention.

A human flinch. “Native” is a word that flatters the speaker. Adopted children of CLIP+LLM are not lesser; they are the reason City B exists. A native model that you cannot download does not make the adopted children obsolete. It makes a City A ceiling. Ceilings move. Floors, since August 2022, have a habit of moving too, later, when someone releases a cousin.

Stage 07 ends with the assistant that looks, in two illegible forms and a pile of open bolts. Stage 08 leaves the still picture as the center of the room. Sound. Moving pictures. A joint space that wants more than two senses. The leftover channels become first-class, or try to.
