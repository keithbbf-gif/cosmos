---
title: "DeepSeek, Qwen, and the China labs"
slug: deepseek-qwen-and-the-china-labs
meta_description: "Qwen from August 2023, DeepSeek-V3/R1 in 2024–25: open-weight quality under export rules, without a morality play."
tags: [deepseek, qwen, china, open-weights, 2025]
era_start: 2023-08
citations:
  - "DEEPSEEK2025 https://arxiv.org/abs/2501.12948"
  - "QWEN https://arxiv.org/abs/2309.16609"
  - "HOFFMANN2022 https://arxiv.org/abs/2203.15556"
status: draft
voice_check: human
---

In August 2023, Alibaba's Qwen team put 7B-class weights on the public internet (paper trail: Bai et al., *Qwen Technical Report*, September 2023). The models were good. The Western press mostly missed them because Llama 2 had already soaked the narrative. Through 2024–25 the Qwen line (2, 2.5, later 3-class releases — check the card) became a default teacher for a lot of fine-tunes you have already downloaded without reading the model card.

On 20 January 2025, DeepSeek-R1 did not get missed. A 671B-class MoE stack (V3 as the base, R1 as the reasoner), a paper that named GRPO, a reported train bill that made Western CFOs twitch, and weights you could pull. Hugging Face's Open-R1 post (28 January) is a decent primary-adjacent chronicle of what was and was not released (weights yes; full data and code no).

This piece is not a geopolitical pamphlet. It is a catalog and a constraint.

## The catalog, named

**Qwen (Alibaba).** Dense and MoE, chat and coder, increasingly multimodal. Apache-ish licenses on many cards, with the usual use bans — read the file. Quality per parameter has been competitive with Western open weights at several size points. If your 2025 RAG backend is "a 32B we grabbed," there is a decent chance it is Qwen-descended.

**DeepSeek.** V2 and V3 as efficient MoE bases (MLA attention, multi-token prediction, in their write-ups). R1 as the reasoning event. Coder variants. The $5.5M-class training figure circulated with V3; treat the integer as *their reported* number, not an audited COGS.

**Others, shorter.** 01.AI's Yi. Zhipu's GLM. Moonshot's Kimi (long context as a brand). Baichuan, internLM, Stepfun. ByteDance's Doubao as a closed consumer hit inside China. The list will be stale by the time an editor ships this. The pattern will not: several Chinese labs ship files that are good enough to change Western pricing.

**Export controls.** US rules on advanced accelerators (2022–23 onward, with updates) are the constraint everyone wants to narrate. We do not have DeepSeek's cluster purchase orders. We have a public recipe that looks like "clever systems plus enough chips." Do not invent a smuggling story. Do not invent a "sanctions don't work" story. Both are beyond this pack.

## Licenses and apps, the unglamorous gate

A weight that is "fine on Hugging Face" can still be banned by a US agency buyer, a bank's third-country list, or an App Store rule. None of those lists are this pack's to reprint; they change. Write down *who* in your company owns the list. If the answer is "the intern who picked Qwen-32B because it won a tweet," you do not have a policy.

Censorship evals (refusals on political prompts) are a real behavioral difference on some China-origin chat finetunes. They are also a difference on US models, in another direction. Measure the class you care about. Do not assume a geography is a moral guarantee.

## What Western buyers actually did

They downloaded the file, quantized it, and compared it to Llama 3.1 70B on their private set. Sometimes it won. Then legal asked about data residency, about whether a China-origin weight was acceptable to a US bank, about the license, about whether distillation from a US API had been part of the soup (a recurring accusation; evidence in public is messy; mark `[CITE NEEDED]` before you print a specific charge).

Procurement split. Some governments and primes banned the weights. Some startups standardized on them because the price/quality ratio was the product. Closed US/EU APIs dropped prices the same quarter. That last sentence is the tell. Competition does not require a landing on a beach. It requires a Hugging Face repo.

## What the papers changed

R1's RL write-up pulled "you need a closed o1" off the table as a talking point. Qwen's volume pulled "Meta is the only open teacher" off the table. Neither pulled "open science" onto the table. The crawls remain unpublished. The instruction mixes remain unpublished. Open *weight* is not open *data*. That distinction is in the open-weights piece; it is sharper here because the political overlay makes people forget it.

## How to write this without being a fool

Name versions and dates. Quote the arXiv. Do not psychoanalyze a ministry. Do not pretend a model card is a sanctions-compliance program. If you serve these weights, you still owe the same evals, the same logging, and the same refusal tests you owe Llama. Geography is not a safety property.

## Opinion

The 2025 shock was not "China has GPUs." It was "the open catalog's quality ceiling moved, and it did not move in California." If your 2026 vendor matrix has no Qwen or DeepSeek row — even as a rejected row with a written reason — you are not doing procurement. You are doing branding.
