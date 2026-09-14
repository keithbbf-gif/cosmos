---
title: The stack as of September 2026
slug: twenty-twenty-six-the-stack
series: open-source-ai-history-2015-2026
status: draft
voice_check: human
reading_order: 45
word_target: 600-1800
era: "2026"
stack:
  - tensorflow
  - pytorch
  - huggingface
  - llama
---

# The stack as of September 2026

![Four public layers: framework, hub, weights, and the engine you run.](../assets/four-stacks/layers.svg)

*Figure 2. The layers a 2026 shop actually mixes.*

A workstation this month still `import torch`s. It still talks to the Hub. It still has a GGUF cache and, if it serves, a vLLM container. The weight file on the card might be Llama 4 Maverick, Qwen3.6, DeepSeek-V4-Flash, Gemma 4, Mistral Small 4, or gpt-oss-20b. The license file is the part that changed most since 2023, and the part people still skip.

This chapter is a look, not a leaderboard. Dates after April 2026 that are not in the first-party posts already cited are marked `[CITE NEEDED]` rather than invented. Later summer 2026 cards may exist that this pack does not name. Do not invent a September surprise to make the chapter feel current. Current is the pin you have.

## Frameworks

PyTorch 2.x plus `torch.compile` is the trainer default. JAX is the other Google. Keras 3 sits on both plus TensorFlow. TensorFlow 1 graphs are museums that still pay bills. ONNX is a vision joint (`onnx-export-problem`). Nobody serious starts a new LLM trainer in TF 1. Plenty of serious people still start a ranking model in `tf.keras`.

That sentence would have sounded like science fiction in 2016, when the argument was whether a static graph was a grown-up choice (`tensorflow-vs-pytorch-2017-2019`). The argument ended. The graphs did not all die.

## Hub and adapters

`transformers`, `peft`, `safetensors`, a gated click. The Hub is the CDN. A shop that does not mirror its pins is a shop that has not had the outage yet. LoRA is still how a Saturday becomes a card. Full-parameter SFT is how a lab with a cluster becomes a card. `mlx-community` and `ollama pull` are second landlords with the same verb (`mlx-apple-silicon`, `ollama-local-box`).

## Weights

Meta: Llama 4 Scout / Maverick public; Behemoth not. 3.x still served. Mistral: Small 4 (16 March 2026, Apache) and the Mistral 3 family (December 2025) as the open shelf’s current heads, with Premier still API. Qwen: 3.5 (February) and 3.6 (April) on Apache, per QwenLM logs. DeepSeek: V4 Preview (24 April), R1 distillations still everywhere. Google: Gemma 4 (2 April, Apache). OpenAI: gpt-oss (5 August 2025), Apache plus a usage policy. Phi still MIT and quiet.

The honest noun edits of the year: Meta saying “open-weight” on Llama 4, Google putting Apache on Gemma 4. The rest is more cards.

## Runners

`llama.cpp` / Ollama / MLX on the desk. vLLM / TGI / a vendor engine on the server. The 2023 split held (`llama-cpp-gguf`, `vllm-paged-attention`). Context lengths of 256K–1M are a serving problem more than a training-blog problem. Harmony on gpt-oss and routers on every new MoE are why “we run vLLM” is not a pin without a version and a model class.

## What did not happen

A single “winner” model. A single license. A single definition of open source AI. DistBelief’s ghost — a great system you cannot share — did not return as the only option; it returned as the API-only half of every vendor that also dumps some weights.

The open-data bet (`redpajama-dolma-open-data`) did not become the default pretrain. It became the conscience and the ablation. Production fine-tunes still sit on vendor bases plus private instruction data.

## How to look at a 2026 card

Org, name, commit, license file, extra policy PDF, gate, architecture (dense / MoE, active params), context, files (`safetensors` vs GGUF vs MXFP4), whether the README’s “open source” matches the file. Then pin. Then mirror.

A license spreadsheet with those columns is a grown-up object. A Slack pin of a Hub URL is not. The eleven years produced enough PDFs that memory is a bad store. The last chapter is the table’s user manual.

A boring shop this month: PyTorch 2.x trainer, Hub pin, LoRA, `safetensors`, a mirror in object storage, vLLM in one cluster, Ollama on the laptops, a spreadsheet that actually lists PDFs. That shop is not behind. It is what the eleven years produced. A shop that still says “we use Llama” with no minor, no size, and no license file is behind. A shop that calls everything open source is behind. A shop that has no mirror is one outage behind.

Figure 1 in the intro is the corridor that got you here. Figure 2 is the room. The four layers still hold: framework, hub, weights, runner. Licenses cut across all four. The rooms got more furniture. The walls did not move.

## Sources

First-party posts already cited: Llama 4 (5 April 2025); Mistral Small 4 (16 March 2026); Qwen3.5/3.6 logs (2026); DeepSeek-V4 (24 April 2026); Gemma 4 (2 April 2026); gpt-oss (5 August 2025). Framework docs as of 2026-09.

See: `intro-the-open-stack`, `llama-4-scout-maverick`, `what-a-license-actually-permits`, `open-weight-vs-open-source`.
