---
title: "Open weights versus closed"
slug: open-weights-versus-closed
meta_description: "Llama in February 2023, Llama 2 in July, Mistral 7B in September: the split is about licenses and meters, not a morality play."
tags: [llama, mistral, open-weights, 2023, 2025]
era_start: 2023-02
citations:
  - "TOUVRON2023 https://arxiv.org/abs/2302.13971"
  - "TOUVRON2023B https://arxiv.org/abs/2307.09288"
  - "LLAMA3 https://ai.meta.com/blog/meta-llama-3/"
  - "MISTRAL7B https://mistral.ai/news/announcing-mistral-7b/"
  - "MIXTRAL https://mistral.ai/news/mixtral-of-experts/"
  - "DEEPSEEK2025 https://arxiv.org/abs/2501.12948"
status: draft
voice_check: edited
---

On 24 February 2023, Meta began issuing LLaMA weights to researchers. The paper (Touvron et al., arXiv 27 February) described 7B–65B models trained on public data, competitive with much larger closed systems on a slice of academic checks. Within days the weights were on BitTorrent. Meta's "research access" posture lasted about as long as a polite email.

That leak — and Meta's later choice to lean into it — is the start of the modern open-weight market. Not "open source" in the OSI sense, not always. Open *weight*: you can run the file. The license may still ban your use case, your user count, or your politics.

## The year the file came back

Llama 2 landed on 18 July 2023 with a commercial-friendly community license, 7B/13B/70B, and chat variants. Acceptable-use rules still applied. For most startups that was enough. Suddenly the alternative to an OpenAI invoice was a GPU and a Hugging Face repo.

Mistral 7B (27 September 2023) made the small model respectable. Apache 2.0, strong for its size, easy to fine-tune. Mixtral 8×7B (11 December 2023) popularized sparse mixture-of-experts for people who did not work at Google: 47B total parameters, a fraction active per token, a MoE you could actually serve. France had a frontier lab that shipped files, not just essays.

Then the rest of the catalog arrived in a heap. Qwen (Alibaba, from August 2023). Phi (Microsoft, small and heavily curated). Gemma (Google, 21 February 2024). Llama 3 (18 April 2024, 8B and 70B, ~15T tokens). Llama 3.1 (23 July 2024) put a 405B on the table. Llama 3.2 (25 September 2024) put 1B/3B on the edge. DeepSeek-V3 and R1 (late 2024 / 20 January 2025) showed a Chinese lab matching closed reasoning scores with a published recipe and weights. Llama 4 Scout and Maverick (5 April 2025) went MoE and multimodal; Meta's own wording shifted toward "open-weight." `[CITE NEEDED]` on Behemoth — previewed, not a public file as of this draft's check.

OpenAI stayed closed at the frontier for most of this window. Smaller later exceptions, if any, should be taken from the current model card — names in this category get announced and retired faster than a bibliography can track. Anthropic stayed closed. Google split the difference: Gemma on one table, Gemini on the other.

## What the fight is actually about

**Money.** Closed APIs meter quality and bundle safety. Open weights meter hardware. If you have traffic and a competent inference team, the file wins on margin. If you have a prototype and no SRE, the API wins on time.

**Control.** A file can be fine-tuned on your tickets, air-gapped, and still running when a vendor retires a model name. It can also be fine-tuned into a scammer. Closed vendors sell the fact that they will take the abuse mailbox. Sometimes they even do.

**License reality.** Llama's community licenses are not MIT. They have user-scale clauses and use bans. "Open" in a launch tweet is not a warranty. Lawyers who treat Hugging Face as public domain will meet a cease-and-desist that was always in the README.

**Data opacity.** Open weights are not open science. Most releases still hide the crawl, the filter, and the instruction mix. DeepSeek-R1's January 2025 write-up was unusually specific about the RL stage and still did not give you the dataset. Replicators (Hugging Face's Open-R1 effort, 28 January 2025 post) had to rebuild around the missing pieces.

## The Stanford weekend

Alpaca (Stanford, 13 March 2023) fine-tuned Llama 7B on 52k instruction traces for a claimed few-hundred dollars. Vicuna (LMSYS, 30 March 2023) used ShareGPT chats. Both were research artifacts with license problems (Llama 1 was not commercial; the instruction data was a mess). Both proved that once the base file exists, the chat layer is a weekend. That is the threat closed labs actually felt. Not a 65B from a university. A culture that could take *their* alignment work and paste it on *Meta's* base.

Hugging Face became the distribution channel the way PyPI is for Python. A model card, a license string, a quantized GGUF someone else uploaded. The quality of those cards varies from "reproducible science" to "a selfie." The channel is still how most people meet weights.

## How the split settled, 2025–26

A working truce, not a peace treaty:

- Frontier chat and the safest "talk to the public" surfaces stay mostly closed, or open with a lag.
- Batch, RAG backends, on-prem, and edge go open-weight or small closed SKUs.
- Governments and banks ask for weights *or* contractual audit, and then accept a VPC endpoint when the audit never quite happens.
- China-origin models are excellent and politically complicated in US/EU procurement. That sentence will date. It is true at the time of writing.

The truce breaks whenever a lab drops a file that is "too close" to a closed model's behavior. Then you get a week of accusations about distillation and a shrug from everyone who needed a cheaper teacher model. Distillation fights are also how you can tell the file still matters: nobody sues over a wrapper.

## Opinion

This was never a purity contest. It is a fight about who holds the file and who holds the meter. Llama 2 made the file a default option. Mistral made it tasteful. DeepSeek-R1 made it embarrassing to claim that reasoning required a closed stack.

If you are choosing in 2026, write down what you must control (data residency, fine-tune, spend, liability). Then pick the license and the meter that match. Do not pick a mascot.
