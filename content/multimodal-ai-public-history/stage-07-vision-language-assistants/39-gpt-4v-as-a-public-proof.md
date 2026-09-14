---
id: "39"
slug: gpt-4v-as-a-public-proof
title: GPT-4V as a public proof
stage: 07-vision-language-assistants
stage_title: Vision–language assistants
status: draft
voice: human
novelty_safe: true
public_record_only: true
primary_public_sources:
  - "OpenAI, GPT-4V system card, 25 September 2023"
  - "GPT-4 technical report (March 2023) as the language-side precursor"
  - "OpenAI product announcements for vision in ChatGPT / API"
does_not_claim:
  - "unpublished GPT-4V architecture"
  - "training data composition"
last_reviewed: 2026-09-14
---

# GPT-4V as a public proof

GPT-4, in March 2023, was already rumored to have seen images during some of its life. The public, for months, had a text box. On September 25, 2023, OpenAI put vision in the product and published a **system card** for GPT-4V. That pairing — a thing you could upload to, and a document about what they were afraid of — is the public object. There is no Flamingo-style architecture paper I can footnote. I will not invent a diagram.

So what kind of proof is this?

It is a proof of **demand and of competence in the messy middle**. People uploaded whiteboards, error messages, fridge contents, homework, skin, tickets, memes. The model read a lot of it. Not all. The demos that traveled were the ones where a screenshot of a program plus a question produced an answer that felt like a senior engineer in the room. The failures that traveled were counting, letters, invented details in a chart, medical confidence. Both traveling sets are true. A proof can be uneven.

The system card is the primary document I trust more than the ad. It talks about privacy, about people, about biometric fears, about what they blocked. It is a City A document: policy as architecture. I will not summarize it as if I were the safety team. I will say that **the card admits vision is a new harm surface**. A text model can be asked for a bad recipe. A vision model can be asked about a photograph of a real stranger. That is Flamingo’s interleaved interface plus a population.

Compared to LLaVA, the public difference is not only quality. It is **illegibility plus reach**. Nobody outside the lab can say whether GPT-4V is a frozen CLIP plus a projector or a natively mixed training mix or both. The Gemini report, later, will at least *say* native. OpenAI, here, says product. Researchers evaluated it as an oracle anyway. A lot of 2023–2024 papers have a table column that is “GPT-4V” the way older papers had “human.” That column is a historical fact and a methodological vice. Oracles that you pay for per token are not controls.

I remember the first month as a change in what people *bothered to photograph*. Not art. The corner of a manual. A serial number. A UI they could not name. Vision-as-assistant is a different verb from vision-as-generator. 2022 made pictures. 2023 looked at pictures you already had. The looking is closer to the 2015 captioner’s job and the 2015 VQA sport, except the answer can be a page, and the image can be a document, and the prior is the whole internet’s text.

Documents are the sleeper. A photograph of a page is language. GPT-4V’s public success on charts and slides (when it succeeded) is the leftover channel from draft 01 finally becoming a product feature. Multimodal, in the workshop sense, was always going to be about *text that had been printed*. The art models distracted us. The assistant brought it back.

A novelty-safe wall. I do not know the resolution they train at. I do not know if video was in the mix. I do not know the interconnection of the vision tower. When later writers say “GPT-4V proved native multimodality,” they are guessing a method from a behavior. This series does not guess that way. Behavior is public. Method, here, is not.

The proof stands anyway, at a different altitude: **by late 2023, a general assistant that accepts an image is a thing a civilian can have**. That sentence was not true in 2021. It was almost true in research in 2022. It was true as a product in 2023. Gemini’s December will try to take the sentence and add “from the start, and audio, and video.” We will read that next, as a claim.
