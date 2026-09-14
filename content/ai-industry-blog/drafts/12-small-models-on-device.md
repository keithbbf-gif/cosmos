---
title: "Small models and on-device"
slug: small-models-on-device
meta_description: "Phi-3 (April 2024), Gemma, Llama 3.2's 1B/3B (September 2024), and why the interesting efficiency story is not a smaller press release."
tags: [small-models, on-device, phi, gemma, llama, 2024]
era_start: 2023-12
citations:
  - "ABDIN2024 https://arxiv.org/abs/2404.14219"
  - "PHI3 https://azure.microsoft.com/en-us/blog/introducing-phi-3-redefining-whats-possible-with-slms/"
  - "GEMMA https://blog.google/technology/developers/gemma-open-models/"
  - "LLAMA32 https://ai.meta.com/blog/llama-3-2-connect-2024-vision-edge-mobile-devices/"
status: draft
voice_check: human
figures:
  - topology-open-vs-closed-deployment
  - infographic-moe-routing
---

On 23 April 2024, Microsoft posted Phi-3. The 3.8B "mini" was the headline: enough quality, they said, to challenge models twice the size on a slice of academic and internal checks. The technical report (Abdin et al., 22 April 2024) is the part to read. The trick was not a new layer. It was data — heavily filtered, heavily synthesized, obsessively taught — plus the admission that a 3B model will never be a 70B model on the long tail.

A month earlier, Google had released Gemma (21 February 2024), a 2B/7B pair from the Gemini research line. In September, Meta's Llama 3.2 put 1B and 3B on the edge and 11B/90B vision models next to them (25 September 2024). Apple spent WWDC 2024 and the following year talking about on-device foundation models for Apple Intelligence, with the larger jobs bouncing to private cloud. The center of gravity moved.

Not because people stopped buying H100s. Because most tokens a human wants are cheap tokens: classify this, rewrite that, summarize the thread, run a grammar pass, draft the reply I will edit.

<!-- ai-blog-figures:begin -->
<figure class="blog-figure">
  <img src="../assets/topology-open-vs-closed-deployment/infographic-topology.svg" alt="Open-weight file deployment versus closed API topology" width="1200" loading="lazy" />
  <figcaption><strong>Figure 1.</strong> Open weights shift spend to your hardware; closed APIs shift it to vendor meters — controls can be shared.</figcaption>
</figure>

<figure class="blog-figure">
  <img src="../assets/infographic-moe-routing/infographic-moe.svg" alt="Schematic mixture-of-experts router activating a subset of experts per token" width="1200" loading="lazy" />
  <figcaption><strong>Figure 2.</strong> MoE models activate a fraction of parameters per token; serving needs expert-aware infrastructure.</figcaption>
</figure>

<!-- ai-blog-figures:end -->
## Why small got good enough

Three stacked improvements, 2022–25.

**Data per parameter.** Chinchilla already said small models want more tokens. The Phi line pushed quality: textbooks, synthetic exercises, decontaminated benches. You can argue about how far synthetic data goes (see the copyright piece). You cannot argue that a 2018 scrape is the only way to train a 3B.

**Inference software.** llama.cpp, ggml/gguf, vLLM, MLX on Apple silicon, ExecuTorch, ONNX, vendor NPUs. A 7B 4-bit model on a laptop was a party trick in 2023 and a default local assistant in 2025. The heroes here are quantization and kernels, not a keynote.

**Routing.** A 2026 app that sends every keystroke to a frontier model is either rich or careless. Cheap local / small-cloud for the obvious cases, expensive model for the rest, is the architecture that matches the price curve. "Mixture of models" is an ops problem. It is also how you stay solvent.

## What on-device actually buys

Latency you can feel. A keystroke completion that waits on a transatlantic round trip feels broken. A 1B–3B on the NPU does not.

Privacy you can *claim* without lying, if the weights and the activations stay on the machine. As soon as you "helpfully" spill to the cloud for hard queries, you are back in privacy policy land. Apple's split (on-device first, then a sealed cloud) is one design. Android's vendor-specific NPUs plus Gemini Nano is another. Both are products, not proofs.

Offline. Planes, plants, SCIF-adjacent work, the factory floor. If your buyer cannot tolerate a WAN, the file has to fit.

What on-device does not buy: frontier reasoning, fresh world knowledge, or a free pass on safety. A local model can still exfiltrate via the features you gave it. A local model can still be fine-tuned into a nuisance. Air-gap is a network property, not a virtue property.

## The local runtime that actually shipped

llama.cpp (Georgi Gerganov, March 2023, exploding through that year) made 4-bit and 5-bit Llama-class models a Mac and a Linux box problem, not a CUDA problem. Ollama wrapped it for people who did not want to read a flag list. Apple's MLX (late 2023–2024) did the same on Apple silicon with a research-friendly Python. These are not models. They are why "on-device" stopped meaning "a keyword-spotting chip."

Apple Intelligence (WWDC, 10 June 2024) is the consumer version of the split: a small on-device model for the obvious; a larger "Private Cloud Compute" path for the rest, with Apple's promised attestations. Feature delays through 2025 taught a useful lesson. Shipping an on-device stack is a hardware-plus-OS problem. A Hugging Face demo is not an OS.

Android's Gemini Nano and the various OEM NPUs (Qualcomm, MediaTek, Samsung) are the other half of the phone market. Quality varies by device year. If you write "on-device Android" in a spec, name the chip generation or you are writing fiction.

## The catch on "small"

Small models fail less gracefully. They are more prompt-brittle. They collapse on long-horizon tool use. They memorize less of the long tail, which is good for some privacy stories and bad for "just know this obscure API." Distillation from a teacher can copy the teacher's refusals *and* the teacher's leaked style. If your teacher is a closed API, you may also be copying a terms-of-service fight.

Energy math is local. Serving a 70B at 10 QPS in a region is a data-center problem. Serving a 3B a billion times on phones is a battery and thermals problem. Neither is free. "Green AI" decks that only count training FLOPs are doing branding.

## 2025–26, without the brochure

Llama 4's edge story, Mistral's Ministral line, Qwen's small variants, Google's Gemma 3-class releases, and a pile of 1B–8B finetunes are the working set. `[CITE NEEDED]` for any specific 2026 LMSYS Elo on a 27B — those numbers move weekly; do not freeze them in a blog without a date stamp and a link.

The interesting systems are not "a 3B that beats GPT-4." That sentence is always a lie in the limit. The interesting systems are "a 3B that handles 80% of our routing cheaply, with a log of the 20% we escalated."

Quantization is a product decision dressed as a flag. 4-bit is how the laptop demo works. It also changes refusal behavior and arithmetic. If you eval the bf16 checkpoint and ship the GGUF, you eval'd a different model. Run the canary on the file you actually serve.

## Opinion

Efficiency is the first grown-up metric of the API era. Kaplan's 2020 charts licensed excess. Phi, Gemma, and Llama's tiny variants licensed *enough*.

If your 2026 architecture has one model name in it, you are either at prototype stage or you like invoices. Put a small model on the path that does not need a genius. Keep the genius for the path that does. Measure both.
