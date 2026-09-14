---
title: Mistral 7B, Apache 2.0
slug: mistral-7b-apache
series: open-source-ai-history-2015-2026
status: draft
voice_check: edited
reading_order: 33
word_target: 600-1800
era: "2023–2026"
stack:
  - mistral
---

# Mistral 7B, Apache 2.0

Mistral AI’s 27 September 2023 post released Mistral 7B, a 7.3B dense model with sliding-window attention and grouped-query attention, under Apache 2.0. The claim, re-evaled in their pipeline, was that it beat Llama 2 13B on the benches they showed. Weights on a torrent and then on the Hub. No community user cap. No research-only form. A French lab eight months old had shipped the cleanest popular crate since TensorFlow.

The paper (Jiang et al., arXiv:2310.06825) is the methods object. The license is the historical object.

## Why Apache mattered in 2023

Llama 2 was the quality default and a PDF. Lawyers who had blessed Apache 2.0 for a decade could bless Mistral 7B in an afternoon. Startups that did not want to read an acceptable-use policy had a model. This is not a quality ranking. It is a procurement fact.

GQA and sliding window were the technical reasons a 7B felt faster than its neighbors. They are real. They are also the kind of thing a 2026 reader treats as ordinary. The 2023 reader did not.

Mistral 7B Instruct, fine-tuned on public Hugging Face instruction sets per the post, was the usable chat object. No tricks, they wrote. The internet always hears “no tricks” as a dare.

## A company with two shelves

Mistral later split its catalog into Open (Apache or similarly permissive weights) and Premier (API-only). Codestral (22B, 29 May 2024) sat under a Non-Production License. Mistral Large 2 (123B, 24 July 2024) sat under a Research License for self-host. Magistral Medium was API-only; Magistral Small (10 June 2025) was Apache. The 7B post is the open shelf’s founding. The later catalog is a business.

Mistral NeMo (12B, 18 July 2024, with NVIDIA, Apache, 128K, Tekken tokenizer) was the drop-in upgrade path from 7B. Pixtral 12B (17 September 2024, Apache) was the multimodal open sibling. Ministral 3B/8B (16 October 2024) were the edge pair. The 7B idea — small, Apache, ship — kept growing names.

## 2025–2026 aftershocks

Mistral Small 3 (24B, 30 January 2025, Apache). Devstral Small (21 May 2025, Apache, with All Hands AI). Magistral Small (June 2025). Mistral 3 / Large 3 (2 December 2025, 675B total / 41B active, Apache, per Mistral’s post). Mistral Small 4 (16 March 2026, Apache MoE, 256K, reasoning + multimodal + coding in one card). Each of those is a later object. This chapter keeps 27 September 2023 as the door.

## 2026 look

If a lawyer asks for “an open model,” Mistral 7B and its Apache descendants are still the easy answer. If an engineer asks for “a good 7B,” the answer moved every six months. Read the 27 September post and the Apache file. Then read the current card you are actually pinning. The brand is not the license.

Arthur Mensch’s lab is a company, not a commons. Apache on a weight file is still a stronger crate label than a community PDF. That sentence is this chapter’s only ranking.

## Sliding window and GQA as 2023 news

Grouped-query attention is now a default in many cards. Sliding window is a design some later models dropped. In September 2023 they were why a 7.3B felt cheap to run. Read the paper’s diagrams if you want the mechanism. Read the post’s tables if you want the vendor claim. Do not convert “equivalent size” into a parameter count.

The Instruct recipe — public Hub instruction sets, per the post — is a 2023 honesty. Later instruct models are often a stew of private SFT and preference data. 7B Instruct is an ancestor of the stew and a simpler object.

## Open versus Premier as a catalog habit

A company that ships Apache 7B and later sells a Premier API is not a hypocrite. It is a company. The catalog split is how you read a 2026 Mistral sentence: is this card Apache, research-licensed, or API-only? Codestral and Large 2 taught people to ask. Small 4 (March 2026) put a lot of jobs back on Apache. Ask every time.

## French lab, global Hub

Mistral’s papers and posts are English. The company is Paris-shaped. The files live on the Hub next to Meta and Alibaba. National narratives that need a European open champion can use 27 September 2023 as a date. This series uses it as a license date. Both readings fit. The Apache file is the one that ships in the crate.

## A torrent and then a Hub card

The September 2023 distribution included a magnet-style drop and then official cards. That sequence is a 2023 habit (see also Mixtral). Apache does not require a gate. The absence of a gate is part of the crate. A 2026 Mistral card that is gated is a different product even if the brand matches. Look.

## Sources

Mistral AI, “Announcing Mistral 7B,” 27 September 2023. Jiang et al., arXiv:2310.06825. Later Mistral news posts: NeMo, Pixtral, Magistral, Mistral 3, Small 4.

See: `mixtral-open-moe`, `llama-2-july-2023`, `open-weight-vs-open-source`, `twenty-twenty-six-the-stack`.
