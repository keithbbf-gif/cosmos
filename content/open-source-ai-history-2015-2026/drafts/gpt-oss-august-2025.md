---
title: gpt-oss, 5 August 2025
slug: gpt-oss-august-2025
series: open-source-ai-history-2015-2026
status: draft
voice_check: edited
reading_order: 39
word_target: 600-1800
era: "2025"
stack:
  - gpt-oss
---

# gpt-oss, 5 August 2025

OpenAI’s “Introducing gpt-oss” post on 5 August 2025 released `gpt-oss-120b` and `gpt-oss-20b` under Apache 2.0, with a separate gpt-oss usage policy sitting next to the license file. The models are mixture-of-experts reasoners. The post and later card (arXiv:2508.10925) give the sizes shops actually pin: about 117B total / 5.1B active for the large one, 21B total / 3.6B active for the small one, 128K context, adjustable reasoning effort. AWS listed both on Bedrock and SageMaker JumpStart the same day. Hugging Face hosted the official cards. They were the first OpenAI open-weight language models since the GPT-2 era (`bert-gpt2-model-cards`) that a 2025 engineer would treat as current.

The company’s own help article is unusually careful with nouns. It says “open models or open-weight,” names Apache 2.0, and then names the usage policy in the same sentence. That is the crate. People who say “OpenAI open-sourced GPT” have collapsed three objects: a brand, a pair of checkpoints, and a closed API line that did not become downloadable.

## Why the date is a hinge

DeepSeek-R1 had been MIT and loud since January (`deepseek-r1-january-2025`). Qwen3 had been Apache since April (`qwen-alibaba-stack`). Meta had Scout and Maverick since April, community-licensed (`llama-4-scout-maverick`). OpenAI’s open-weight absence was itself a fact. 5 August closed that particular absence without closing the API business. The company can ship Apache weights and sell o-series calls. It did. The August post says so in as many words: gpt-oss is for people who want to fine-tune and host; the API models remain the multimodal, tool-batteries-included product.

People who wanted a morality play — OpenAI “forced” by R1 — can write that play elsewhere. The public objects are a blog post, two cards, an Apache file, a usage policy, a Harmony renderer, and an AWS listing.

## Harmony, MXFP4, and the objects you actually run

The GitHub README is blunt: both models were trained on the Harmony response format and “should only be used with this format; otherwise, they will not work correctly.” Harmony is not a chat-template footnote. It is a role-and-channel language (`analysis` for chain-of-thought, `commentary` for tool calls, `final` for the user-visible answer) designed to mimic the Responses API. OpenAI open-sourced a renderer in Python and Rust and a tokenizer they named `o200k_harmony`, a superset of the o4-mini / GPT-4o tokenizer. If you feed these weights a Llama-2 `[INST]` wrap, you are not evaluating gpt-oss. You are evaluating a broken prompt.

The other object in the crate is MXFP4. The post-training story quantizes the MoE projection weights — most of the parameter count — to a 4-bit microscaling format so the 120B-class model can sit on a single 80 GB GPU and the 20B-class model can sit in about 16 GB. Other tensors stay wider. Official evals, the card says, were run in that quantization. A GGUF mirror that requantizes again is a third object. Name which one you ran.

Adjustable reasoning effort is the product idea: spend more test-time compute when you want to. R1 and Qwen3’s thinking modes are neighbors. gpt-oss made the knob a documented feature in the system message. A bench that does not log low / medium / high is not a bench you can repeat.

## What Apache on an OpenAI weight means

It means a lawyer who already blessed Mistral 7B can recognize the SPDX string. It does not mean the training data is public. It does not mean GPT-4o is downloadable. It does not mean the safety policy of the API models is in the repo. It means these checkpoints have an OSI-shaped software license, plus a usage policy that OpenAI’s own help center treats as a second gate. This series keeps both files on the table (`licenses-that-are-not-open`). Apache is the license. The policy is the policy. Do not let a Hub badge eat the second PDF.

The models are text-only. The card says so. A shop that expected vision because “OpenAI” is a brand, not a file format, will be disappointed. Tool use — web search and Python in the post’s examples — is a Harmony-channel story, not a built-in browser in the weight file.

gpt-oss-safeguard (29 October 2025), also Apache, is a research-preview pair that reasons over a developer-supplied safety policy for classification. A sibling, not a replacement. October’s pair is how you know the line is a shelf, not a one-morning stunt.

## 20b and 120b are two products

3.6B active and 5.1B active, in the post’s figures, are workstation-class and server-class if the quants cooperate. People who say “we deployed gpt-oss” have said almost nothing. Say which. Say the reasoning effort. Say whether you used a GGUF community crate or the official MXFP4 card. AWS same-day listing is a distribution fact: OpenAI can ship Apache and a cloud SKU in one morning. The 2019 GPT-2 staged release was a different company mood. Both moods are in the record.

Reference implementations landed with the weights: a PyTorch path, a Metal path, Triton kernels for the MoE. Those are first-party runners. Ollama, vLLM, and `llama.cpp` grew Harmony support because the format is the joint (`ollama-local-box`, `vllm-paged-attention`). Compatibility with the Responses API is why a lot of tools could point at a self-hosted gpt-oss without inventing a third schema. The dialect of the closed API became, again, the dialect of the open server.

## How to correct the noun

Not “OpenAI open-sourced GPT.” Not “GPT-5 is downloadable.” `gpt-oss-20b` / `gpt-oss-120b`, 5 August 2025, Apache 2.0 plus the gpt-oss usage policy, MoE reasoners, Harmony required, MXFP4 on the official MoE weights. The correction is pedantic and is the job. Read the 5 August post, the model card, and the usage policy in the same hour. If a thread says the training mix is public, it is wrong. If a thread says the weights are not fetchable, it is also wrong.

## Sources

OpenAI, “Introducing gpt-oss,” 5 August 2025. OpenAI, gpt-oss model card / arXiv:2508.10925. openai/gpt-oss README (Harmony, MXFP4). OpenAI Help Center, “OpenAI open-weight models (gpt-oss).” AWS announcement the same day. OpenAI, gpt-oss-safeguard, 29 October 2025. GPT-2 release history as the last comparable OpenAI weight drop.

See: `bert-gpt2-model-cards`, `deepseek-r1-january-2025`, `open-weight-vs-open-source`, `twenty-twenty-six-the-stack`.
