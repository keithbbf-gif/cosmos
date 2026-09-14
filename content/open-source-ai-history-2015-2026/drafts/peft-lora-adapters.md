---
title: PEFT, LoRA, and the adapter
slug: peft-lora-adapters
series: open-source-ai-history-2015-2026
status: draft
voice_check: human
reading_order: 23
word_target: 600-1800
era: "2021–2025"
stack:
  - huggingface
  - peft
---

# PEFT, LoRA, and the adapter

Hu et al., “LoRA: Low-Rank Adaptation of Large Language Models” (arXiv:2106.09685, 2021), proposed freezing a pretrained net and training a pair of low-rank matrices beside selected weights. Dettmers et al., “QLoRA” (arXiv:2305.14314, 2023), put that idea on a quantized base so a single consumer GPU could fine-tune a 7B or 13B. Hugging Face’s `peft` library made both a config you pass to `get_peft_model`. The adapter file — a few dozen megabytes — became the thing people uploaded.

This is the mechanical reason the 2023 weekend fine-tunes (`alpaca-vicuna-weekend-finetunes`) were weekends.

## What an adapter is

It is not a whole model. It is a delta, or a set of extra tensors, that you load onto a base. Distribution now has two crates: the base (gated, large, licensed) and the adapter (often Apache, small, someone’s hobby). Mixing them is a license convolution. People mix them anyway.

`peft` supports LoRA, prefix tuning, IA3, and a list that grew. LoRA won the noun. A 2026 Hub search for “LoRA” returns language and image adapters in the same social graph. The library is the reason the noun is a file format people expect.

## QLoRA and the hardware door

4-bit quantization of the base plus LoRA on top is a hardware door. A 24 GB card became a fine-tune machine for models that had been a cluster job. Papers will argue about quality. Shops noticed the door. Unsloth and later trainers optimized the door. The historical fact is the door, not the leaderboard.

BitsAndBytes as a quantization library is part of that door. So is the later migration to other 4-bit schemes. This chapter will not pick a kernel. It will say: the adapter era is a quantization era.

## Why this belongs next to Hugging Face, not only next to Llama

Because `peft` is a Hub-native object. `PeftModel.from_pretrained` expects a card. TRL (transformer reinforcement learning, Hugging Face) expects PEFT. The adapter is how the Hub stayed relevant when bases became 70B. You do not upload a 70B remix every Saturday. You upload 80 MB and a README that names the base.

## Legal and practical failure modes

An adapter trained on Llama 2 is, in spirit and often in law, a Llama 2 derivative. Uploading it as Apache 2.0 without naming the base is a card failure. Loading it on the wrong base is a silent quality failure. Sharing only the adapter does not share the ability to run if the base is gated.

QLoRA’s paper is a methods paper. It is not a license opinion. The community treated it as permission to fine-tune anything they could download. That treatment is a social fact. It is not legal advice. This series does not give legal advice.

## 2026 look

Open a fine-tune repo. If you see `LoraConfig` and `bitsandbytes`, you are in 2023–2024. If you see a full-parameter FSDP job, you are in a lab with a cluster. If you see an adapter merged into a single `safetensors` for vLLM, you are in production. Merging is how adapters become a new base. The merge inherits the stricter license. People forget.

Hu et al. and Dettmers et al. are the papers. `peft`’s docs are the shop manual. Read both. The paper will not tell you the Hub card fields. The docs will not tell you why rank 8 on `q_proj` and `v_proj` became a folklore default.

## Rank, targets, and folklore

`r=8` or `r=16` on `q_proj` and `v_proj` became a default the way `2e-5` became a BERT default: it worked enough and the tutorial said so. People who adapt MLP lines or all linear layers are doing a different job. The card should say the target modules. Many say “LoRA” and stop.

Merging (`merge_and_unload`) is how an adapter becomes a new base for vLLM. Merging is a one-way street for the license: the stricter parent wins. People upload merged models as Apache. That is a card failure this series will keep naming.

## QLoRA’s hardware door, 2026 version

New quants (FP8, NVFP4, whatever the vendor shipped this quarter) change the door’s size. The door’s idea does not: freeze a cheap base, train a small delta, upload the delta. Unsloth and friends made the door faster. The historical object is still Dettmers et al. 2023 plus `peft`.

## Adapters on the image side and the language side are the same noun

A style LoRA for SDXL and an instruction LoRA for Llama 3 share a social graph and a mental model. They do not share a license parent. The Hub search box does not care. You must care.

## Multi-adapter serving as a 2025–2026 job

vLLM and friends grew the ability to load many LoRAs on one base. That is a product: one 70B, many customers’ deltas. The license convolution multiplies. The ops story multiplies. The 2021 paper did not describe this product. The Hub made it inevitable. Name the base once per process. Name each delta’s parent.

## Sources

Hu et al., LoRA, arXiv:2106.09685. Dettmers et al., QLoRA, arXiv:2305.14314. Hugging Face `peft` and TRL documentation.

See: `alpaca-vicuna-weekend-finetunes`, `hub-as-distribution`, `lightning-fastai-wrappers`, `what-a-license-actually-permits`.
