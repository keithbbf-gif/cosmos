---
title: Mixtral and the open MoE
slug: mixtral-open-moe
series: open-source-ai-history-2015-2026
status: draft
voice_check: edited
reading_order: 34
word_target: 600-1800
era: "2023–2024"
stack:
  - mistral
---

# Mixtral and the open MoE

On 11 December 2023 Mistral released Mixtral 8x7B: a sparse mixture of experts, eight feedforward experts per layer, two experts chosen per token, about 47B total and 13B active in the paper’s rounding, 32K context, Apache 2.0. The news post said it beat Llama 2 70B on most of their benches at a fraction of the active cost. The paper (Jiang et al., arXiv:2401.04088, January 2024) is the object you should cite. The serving folklore — “it’s 13B that thinks it’s 47B” — is the object shops actually used.

Open-weight MoE was not invented that day. Switch Transformers and a pile of research MoEs sat in papers. Mixtral is the day a sparse MoE became a default download with a license a lawyer already had on file. Distribution followed the 7B habit (`mistral-7b-apache`): a magnet-style drop, then official Hub cards, no community user cap. The 7B’s sliding-window attention is still in the family; the December card’s 32K window is the number shops wrote on the ops sheet. A 2026 reader who meets a 128K or 1M MoE should not back-apply those lengths to this file.

## What the router changed

A dense 47B is a memory bill. A 13B-active MoE is a different bill: you still store the experts, you run two. Disk and RAM care about eight feedforwards. FLOPs care about two. People who bought a GPU for a 13B dense model and then loaded Mixtral learned the first sentence. vLLM and friends had to grow routers (`vllm-paged-attention`). GGUF had to grow expert offload. Load-balancing the router is a training problem. Serving a cold expert is a systems problem. If your 2026 MoE is slow, the ancestor is this card.

Quality, on the post’s tables, was a 70B-class English and multilingual story with a 13B-class invoice for compute-per-token. That ratio is why every later “efficient frontier” slide has an MoE on it: DeepSeek-V2/V3, Llama 4, Qwen3, Mistral Large 3. Do not convert “equivalent size” marketing — including this vendor’s — into a parameter count.

## Instruct, DPO, and the 8x22B scale-up

8x7B Instruct, SFT plus DPO, MT-Bench 8.30 in the December post, is the chat object. Base and instruct are different cards. Shops that fine-tuned the base and compared to the instruct were comparing two recipes. Preference training as a public recipe on an Apache MoE is a 2023 object. Later preference stacks (TRL, vendor stews) are children. If you cite that MT-Bench number, cite the post’s date and the judge. Numbers without judges are vibes.

17 April 2024 — the same day as Llama 3 and OLMo 1.7 — Mistral shipped Mixtral 8x22B: Apache, 141B total / 39B active, 64K, function calling. “Cheaper, Better, Faster, Stronger,” they titled the post. The title is marketing. The license was still Apache. That pair — loud title, clean license — is Mistral’s 2023–2024 brand. The idea had already won. DeepSeek-V2 (6 May) and later V3 made a different MoE (MLA, finer experts) the quality story. Mixtral remains the teaching story. Teaching stories can be retired from production and still be true.

## Apache on an MoE

Lawyers who had blessed 7B could bless 8x7B without a new theory. That is why this card, not a research-licensed larger model, became the default experiment. License is a distribution technology. Mixtral used a technology the field already had. A 2026 reader who meets Llama 4’s community MoE or gpt-oss’s Apache-plus-policy MoE should start here for the architecture and then read the PDF in front of them for the crate.

## 2026 look

Mixtral 8x7B is no longer the quality default. It is the teaching default for “what is an open MoE.” If you are explaining Llama 4 or DeepSeek-V3 to someone who missed 2023, start here. The paper is short and clear. The license is the one lawyers already have on file.

Read arXiv:2401.04088 and the 11 December post. Ignore equivalent-size marketing from any vendor, including this one, unless you are writing a caption that says “vendor claim.”

## Sources

Mistral AI, “Mixtral of experts,” 11 December 2023. Jiang et al., arXiv:2401.04088. Mistral, “Cheaper, Better, Faster, Stronger” (8x22B), 17 April 2024.

See: `mistral-7b-apache`, `deepseek-r1-january-2025`, `llama-4-scout-maverick`, `vllm-paged-attention`.
