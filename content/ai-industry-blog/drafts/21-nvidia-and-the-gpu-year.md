---
title: "NVIDIA and the GPU year"
slug: nvidia-and-the-gpu-year
meta_description: "H100s, 2023–24 allocations, and why a power-law paper turned into a chip-foundry story."
tags: [nvidia, h100, compute, 2023, 2024]
era_start: 2022-03
citations:
  - "KAPLAN2020 https://arxiv.org/abs/2001.08361"
  - "NVIDIA_H100 https://nvidianews.nvidia.com/news/nvidia-announces-hopper-architecture-the-next-generation-of-accelerated-computing"
  - "HOFFMANN2022 https://arxiv.org/abs/2203.15556"
status: draft
voice_check: human
---

On 22 March 2022, NVIDIA announced the Hopper architecture and the H100. Training-scale buyers did not get piles of them that spring. They got waitlists, and then, through 2023, a market where "we have H100 allocation" was a Series B slide. Kaplan's January 2020 power law had predicted that dollars of compute would keep buying loss. It had not predicted that one company's SKU would become the unit of strategy.

This is not a stock tip. It is a systems story. The models in this pack — GPT-4, Llama 3, Gemini, DeepSeek-V3 — all sat on some mix of NVIDIA (and, at Google, TPU) iron. The 2023–24 "AI boom" that CFOs felt was often a capex boom with a model name on the press release.

## What the H100 changed, technically

Hopper's useful features for this industry were not the keynote adjectives. They were transformer-engine paths (FP8), NVLink / NVSwitch topologies that made 256-GPU islands less stupid, and a software stack (CUDA, NCCL, later Megatron-LM and DeepSpeed recipes) that the staff already knew. Switching a lab to something else is not a purchase order. It is a two-year compiler and collective-comms project.

Google's TPU v4/v5 story is the existence proof that you can train frontier models off NVIDIA if you already have the compiler people. Amazon's Trainium, Microsoft's Maia, Groq's LPU, Cerebras, the 2024–26 custom-silicon announcements — most of these are inference bets or captive-cloud bets. `[CITE NEEDED]` on any specific 2026 FLOPs/watt comparison; vendor slides are not a bake-off.

Export controls (US rules tightening around advanced accelerators to China, 2022–23 onward) made a second SKU, the "not quite H100," a geopolitical object. DeepSeek's later efficiency claims (V3/R1, 2024–25) were read, fairly or not, as a response to that constraint. The public papers do not give you a full cluster bill of materials. Treat "they did it with fewer H100s" as a reported claim, not an audit.

## Allocation as industrial policy

Clouds (Azure, GCP, AWS, CoreWeave and the GPU specialists) sat between labs and NVIDIA. Microsoft's OpenAI relationship was, among other things, a power-and-cluster relationship. Meta published that it was building toward hundreds of thousands of GPUs for Llama 3-class training. Those numbers move and get restated. The shape does not: a handful of buyers soaked the 2023–24 supply.

Startups that needed 64 GPUs for a finetune discovered they were not in that handful. They rented, they queued, they distilled, they waited for 2025 inference prices. The "GPU rich / GPU poor" split is more explanatory of 2024 product quality than most architecture blogs.

A side market grew: GPU-backed funds, sale-leasebacks, data-center shells in places with power contracts. This pack will not do municipal politics. Note the input. A scaling law that assumes you can always buy 4× compute meets a substation that does not exist yet.

## The 2023 earnings-call year

NVIDIA's FY2024 quarters are public. Data-center revenue jumped in a way that did not look like a video-game cycle. This pack will not reprint a stock chart. The qualitative fact: a single supplier's conference call became a proxy for "is the AI boom real." That is a fragile proxy. It measures capex, not completed work. A bought H100 can sit in a crate behind a missing transformer (the electrical kind). Several 2024 journalistic tours of half-empty halls exist; treat them as reporting.

CUDA lock-in is the other half. A kernel ecosystem (cuDNN, NCCL, FlashAttention ports, the Megatron family) is why "we will switch to vendor B next year" is usually a three-year sentence. ROCm and the various CUDA-translation layers improved through 2024–26. They are still the second language. Builders who need one stack should admit it in the design doc instead of promising a mythical portable IR.

## Inference, the quieter squeeze

Training is a spike. Inference is a rent. 2024–26 is when CFOs noticed the rent. Batching, KV-cache paging (vLLM, 2023), quantization, speculative decoding, and "don't send the easy tokens to the frontier model" are the actual cost-control stack. NVIDIA's inference story (TensorRT-LLM, then whatever the current name is) and the open serving stack fought over the same kernels.

When token prices fell (GPT-4 Turbo in November 2023, then 4o, then a pile of 2025 cuts), it was not charity. It was utilization, smaller models on the path, and competition from labs that would sell a 70B cheap. See the token-economics piece in this pack.

## What to ask a vendor

Not "do you use NVIDIA." Almost everyone does, or did last year. Ask: train or inference? Owned or rented? What's the interconnect, and who owns the power contract? If they cannot answer, they are renting a vibe.

## Opinion

The compute race in the scaling-laws draft is an equation. This draft is the store that sold the variables. 2023–24 made that store a bottleneck. 2025–26 is a messy attempt to route around it — custom silicon, better utilization, smaller models, Chinese labs under export rules.

If your 2026 architecture assumes infinite H100s at 2022 list prices, you are writing fiction. Write the queue.
