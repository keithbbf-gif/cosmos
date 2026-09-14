---
title: Llama 3.1 405B
slug: llama-3-1-405b
series: open-source-ai-history-2015-2026
status: draft
voice_check: edited
reading_order: 31
word_target: 600-1800
era: "2024"
stack:
  - llama
---

# Llama 3.1 405B

On 23 July 2024 Meta released Llama 3.1 in 8B, 70B, and 405B, with 128K context and a language list the card names: English plus French, German, Hindi, Italian, Portuguese, Spanish, and Thai. The blog post called 405B the largest openly available foundation model, a “frontier-level” object, and said developers could use outputs — including 405B’s — to improve other models. Hugging Face’s same-day writeup is the clearest short note on the license edit: synthetic data generation and distillation are allowed, including onto models that are not Llama, with the usual “Llama” naming and “Built with Llama” duties still attached. The February 2023 research grant had feared exactly this kind of distillation. July 2024 invited it.

The herd paper (arXiv:2407.21783), posted days later, is the methods object for the whole 3.x line: 405B dense, 126 layers, trained on 15.6T tokens at an 8K window, then extended. Official FP8 checkpoints of the 405B — linear ops quantized, in the Hub writeup’s telling — are first-party objects, not a community requant. Serving folklore says eight 80 GB GPUs. Measure yours.

## Size as a public object

405B dense is a different serving problem from 70B. vLLM, tensor parallel, a lot of H100s — the pager chapter (`vllm-paged-attention`) becomes a budget. Community GGUF exists and is a different quality object. Meta’s claim was about the full model. Shops that serve a 4-bit 405B should say so.

The 8B and 70B upgrades in the same drop (multilingual, 128K, tool use on the Instruct cards) are what most people actually ran. 405B is the headline and the distillation teacher. A lot of later “small but good” cards are 405B’s grandchildren, named or not. AWS, NVIDIA, Databricks, Groq, and the rest of the partner list in the July post are distribution, not training credit. Cloud availability is how a 405B is an API for most people even when the weights are, in principle, a Hub id.

## Distillation as official policy

The Llama 2 license had been stingy about training on outputs. 3.1’s prose, and the updated Community License, opened a door the weekend fine-tunes (`alpaca-vicuna-weekend-finetunes`) had already kicked. Meta’s reason, as stated: synthetic data and distillation at this scale had not existed in open weights before. Agree with the reason or not, the sequence is: leak, unofficial distillation, official distillation.

Closed labs had been distilling themselves for years. 3.1 made a public teacher. Synthetic data from 405B to train 8B is how a family reproduces. Shops did it. Papers did it. The weekend of March 2023 did it without permission. July 2024 sold the permission as a feature.

Tool use on the Instruct siblings — search, image generation, code execution, math, plus a zero-shot tool story in the launch coverage — is why a lot of late-2024 agent demos said Llama. Whether the tools were reliable is a bench you should run. The historical fact is that Meta put tool use on the open-weight card, not only on an API. Agents that assume an API-only tool surface are living in 2023.

## “Open source” at 405B

Meta’s July prose is maximal: “first frontier-level open source AI model.” The license is still a community license. OSI’s definition does not grow with parameter count. A 405B community-licensed model is a magnificent open-weight object. It is not, by that definition, open source software. Both facts fit in one paragraph. Say 405B dense, 128K, community license, 23 July 2024. Do not say “frontier” unless you are quoting. Do not say “open source” unless you are quoting, and then correct the noun.

## Dense 405B as a monument

Llama 3.3 70B later claimed much of the 405B product quality at lower cost. Llama 4 moved the frontier story to MoE (`llama-4-scout-maverick`). DeepSeek went MoE. 405B dense is a 2024 monument: the year a frontier-sized dense net was a Hub id. Monuments are expensive to keep lit. Many shops keep the 70B lights on and visit 405B as an API, even when the API is their own vLLM.

Open weights do not mean a laptop. They mean the file is not behind an API *in principle*. In practice, 405B is an API for most people, even when the API is vLLM in your own VPC. Count the GPUs you do not have. That count is part of the history.

Read the 23 July post next to the 405B card and the official FP8 sibling. Then read the herd paper if you need the layer counts. The blog sells a class. The card sells a file.

## Sources

Meta AI, “Introducing Llama 3.1,” 23 July 2024. Llama 3.1 cards and Community License. Hugging Face, “Llama 3.1,” 23 July 2024 (distillation / FP8 notes). Grattafiori et al., arXiv:2407.21783.

See: `llama-3-april-2024`, `vllm-paged-attention`, `open-weight-vs-open-source`, `llama-4-scout-maverick`.
