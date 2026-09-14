---
title: "Scaling laws and the compute race"
slug: scaling-laws-and-the-compute-race
meta_description: "Kaplan 2020, Chinchilla 2022, and how a power-law chart turned into a multi-year GPU buying contest."
tags: [scaling-laws, compute, chinchilla, 2020, 2022]
era_start: 2020-01
citations:
  - "KAPLAN2020 https://arxiv.org/abs/2001.08361"
  - "HOFFMANN2022 https://arxiv.org/abs/2203.15556"
  - "BROWN2020 https://arxiv.org/abs/2005.14165"
status: draft
voice_check: edited
---

On 23 January 2020, Kaplan, McCandlish, and eight colleagues posted a paper that reads like condensed-matter physics wearing an LM badge. Cross-entropy loss, they said, falls as a power law with model size, dataset size, and training compute. Some of the fits ran over seven orders of magnitude. Width and depth, inside a wide band, barely mattered.

That is a stronger claim than "bigger is better." It says the next dollar of compute has a predictable return, and that most of the architectural fiddling of 2018–19 was inside the noise. Labs that believed it started shopping for clusters. Labs that did not still ended up shopping, because the believers published GPT-3 five months later.

## What the Kaplan fit actually said

The useful equations are about allocation. If you hold FLOPs fixed, there is a best split between parameter count and tokens seen. Kaplan's group argued that larger models are more sample-efficient, so the compute-optimal point is a big model trained on a *relatively* modest corpus, stopped before the loss fully flattens. That last clause got ignored in a lot of slide decks. People heard "make it huge."

They also said overfitting has a simple dependence on the ratio of model size to data, and that training speed has a simple dependence on model size. Those are engineering statements. They let a lab sketch a 10× run before buying the GPUs. They do not tell you what the model will *do* for a user. Loss is not a product.

A limit, stated in the paper and then forgotten: the laws were fit on decoder-only transformers, on English-heavy web text, on the hardware and precision of 2019. Extrapolating them to mixture-of-experts, to multimodal tokens, or to 2025-scale runs is a judgment call. Sometimes it held. Sometimes a later paper had to redo the fit.

## Chinchilla, two years later

In March 2022, Hoffmann et al. at DeepMind posted *Training Compute-Optimal Large Language Models*. Same family of question, different recommended split. For a given compute budget, they said, Kaplan-style runs had been *undertrained*: too many parameters, not enough tokens. Their 70B Chinchilla model, trained on more data, beat a much larger Gopher-style model on a slice of downstream checks.

The industry translated this into a slogan — "20 tokens per parameter" — and then argued about the constant. The constant is not the point. The point is that "compute-optimal" is a moving target. It depends on your loss, your tokenizer, your data quality, and whether you care about the pretrain loss or about a chat eval you will run after RLHF. Teams that treated Chinchilla as scripture over-corrected. Teams that treated it as a second data point started measuring tokens as carefully as they measured parameters.

By 2024–25 the public recipes (Llama 3's 15T tokens for an 8B/70B pair; whatever DeepSeek published for V3/R1) looked more Chinchilla-than-Kaplan at the small end and more "we have the data, keep going" at the large end. Overtraining a small model for inference price can be rational even if it is not compute-optimal at train time. The 2020 paper did not have an inference-cost chapter. Production did.

## The race those charts authorized

Once a lab believes loss is a function of dollars, the scarce input is not an idea. It is NVIDIA's allocation, power, and the staff who can keep a 10k-GPU job alive. Microsoft's Azure relationship with OpenAI, Google's TPU fleet, Meta's build-out, the 2023–24 wave of GPU-backed funds — these are what a power law looks like on a balance sheet.

Two side effects.

Training runs became strategic secrets. Papers still listed parameter counts. They stopped listing the parts that would let you reproduce the loss: exact mix, exact decay, exact failure rate on the cluster. "We trained a model" turned into a press release.

Second, the academic unit of progress — a new layer type — lost status. Mixture-of-experts, longer context, better data filters: those still moved the needle. A clever block that saved 5% FLOPs lost to a rival who had 3× the GPUs and a cleaner crawl. That is ugly. It is also what the 2020 fit predicted.

## The public cluster, 2020–24

A few named runs became folklore, with numbers that should be treated as *reported*, not audited. GPT-3's 175B. Gopher 280B (DeepMind, December 2021). PaLM 540B (Google, April 2022). Megatron-Turing NLG 530B (Microsoft/NVIDIA, 2021). Then the public conversation shifted from parameter count to "we will not tell you," which is what GPT-4's March 2023 card did. The compute race did not stop. The press releases got shyer.

Chip supply set the tempo. NVIDIA's A100 then H100 allocations, export-control theater around China, and the 2023–24 wave of GPU-backed special-purpose vehicles were the actual scaling law. A lab that "believed in data" still needed the same SKU as a lab that believed in parameters. The power-law chart does not list a lead time.

## What the laws do not cover

Post-training. A 2024 reasoning model (OpenAI's o1-preview, 12 September 2024; DeepSeek-R1, January 2025) spends a lot of its published story on reinforcement learning after the pretrain. Scaling laws for *that* are thinner. People will show you charts. Ask what was held constant.

Also: data is not a scalar. "Tokens" in 2020 meant web text. In 2025 it meant a stew of licensed books, synthetic traces, code, and whatever survived a filter. Two runs with the same token count are not the same experiment. Kaplan's x-axis assumed they were close enough. For pretrain loss on English, maybe. For "does this thing refuse the right medical question," no.

And hardware is not a smooth curve. A law that assumes you can always buy the next 4× of compute meets export controls, fab queues, and a data-center interconnect that does not exist yet. The 2022–26 "race" has been as much about networking and power contracts as about exponents.

## Opinion

The scaling papers earned their influence because they were more honest than the architecture wars they replaced. They also licensed a kind of managerial fatalism: if the chart is right, the only strategy is to raise. That is true until it is not — until inference price, data lawsuits, or a better post-train recipe dominate the user's experience.

We still use the 2020 question every time a lab announces a number. How many tokens? Held-out loss or a contaminated bench? Train-optimal or serve-optimal? If they cannot answer, they are selling the vibe of a power law, not the result.
