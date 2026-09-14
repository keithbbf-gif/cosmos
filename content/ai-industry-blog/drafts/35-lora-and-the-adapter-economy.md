---
title: "LoRA and the adapter economy"
slug: lora-and-the-adapter-economy
meta_description: "Hu et al. 17 June 2021: low-rank adapters. QLoRA 2023. Why a 7B plus a 50MB file ate the fine-tune market."
tags: [lora, qlora, finetune, peft, 2021, 2023]
era_start: 2021-06
citations:
  - "LORA https://arxiv.org/abs/2106.09685"
  - "QLORA https://arxiv.org/abs/2305.14314"
  - "TOUVRON2023B https://arxiv.org/abs/2307.09288"
status: draft
voice_check: edited
---

On 17 June 2021, Hu et al. posted *LoRA: Low-Rank Adaptation of Large Language Models*. Freeze the base. Train two small matrices whose product is a rank-r update to selected weights (usually attention projections). At serve time, merge them or keep them as a hot-swappable add-on. The paper's GPT-3 experiments were the point: you do not need to store a second 175B. You need a few megabytes and a recipe.

In May 2023, Dettmers et al. posted QLoRA: 4-bit frozen bases plus LoRA, a 65B-class finetune on a single 48GB GPU in their telling. Combined with Llama (February) and Llama 2 (July), that paper is why every 2023 Discord had a "train your own boyfriend model" era, and why a few companies had a real on-tenant adaptation story.

## What adapters actually are

A patch. They are not a new foundation model. They cannot teach the base a language it never saw as well as a pretrain can. They can move taste: your tickets, your tone, your JSON schema, your refusal extras, your medical note format (with all the liability that implies).

PEFT as a library (Hugging Face) made the paper a `get_peft_model` call. DoRA, AdaLoRA, (IA)³, prefix-tuning — the 2022–24 family. Most production use is still LoRA/QLoRA on attention, r=8 to 64, a weekend of A100-hours. The rest is a paper.

Merging (add the update back into the base) is how you ship one file. Stacking (several LoRAs at once) is how you ship a mess. One adapter per task, a router, an eval per adapter, is the adult pattern. A "style pack" zoo with no tests is the Civitai pattern. Both exist. Only one belongs in a bank.

## How people actually train one

A typical 2024 run: pick Llama 3 8B Instruct, r=16 on q/k/v/o, 1–3 epochs, a few thousand curated pairs (not a million scraped chats), a holdout of your real tickets, a refusal mix so you do not wipe the base's manners. QLoRA if you have one 24GB card. Merge if you want a single GGUF. Serve on vLLM with the adapter loaded if you want to swap tenants without a rebuild.

The failure I keep seeing: 200k noisy ShareGPT clones, two epochs, no holdout, then a claim of "our model." That is a style transfer onto internet sludge. It will demo. It will rot.

## Why this ate full fine-tunes

Cost. A full 70B update is a cluster and a forgetting risk (the model loses the pretrain's generality). LoRA is a GPU and a smaller forgetting risk, not zero. People who LoRA on a tiny, peaked dataset still wreck the base's manners.

Distribution. A 50MB adapter can travel. The base stays put (and licensed). That is a product: sell the adapter, not the 140GB. Image people learned this first (DreamBooth 2022, then LoRA on Stable Diffusion). Text people copied it in 2023.

Privacy theater vs privacy. If you train the adapter on tenant data *in the tenant*, you have a story. If you upload the tickets to a vendor's finetune API, you have a DPA. Both get called "custom models" on slides. They are not the same object.

## Defects specific to adapters

**Eval mismatch.** You measured the base, shipped the adapter, and the adapter taught the model to say "as a senior DevOps" on every ticket.

**License.** Llama's community license still applies to the merged file. A LoRA does not launder it.

**Composition.** Two adapters that each look fine can fight. There is no general algebra. Test the pair.

**Forgetting and safety.** A customer-service LoRA that was not shown the refusal set will undo a year of RLHF on that class. Include the refusals in the train mix, or keep a separate policy layer that the adapter cannot edit.

## 2025–26

On-device LoRA (phones, laptops) is how personalization happens without shipping raw user text to a frontier API — when the vendor actually keeps the update local. Apple's and Google's on-device stories belong next to the small-models draft. Server-side, every cloud now sells "finetune this base." The differentiator is whether you can export the adapter and run it on vLLM yourself.

## Opinion

LoRA is the most important boring paper after InstructGPT. It turned "our model" from a $4M run into a file you can email (the adapter, not the base).

If you cannot name the base, the rank, the data, and the eval, you do not have a custom model. You have a vibe. Write those four down. Then decide if you needed a LoRA at all, or just a better prompt and three retrieved passages.
