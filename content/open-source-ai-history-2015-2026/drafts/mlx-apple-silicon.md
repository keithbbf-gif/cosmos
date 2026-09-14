---
title: MLX and Apple silicon
slug: mlx-apple-silicon
series: open-source-ai-history-2015-2026
status: draft
voice_check: human
reading_order: 44
word_target: 600-1800
era: "2023–2026"
stack:
  - mlx
---

# MLX and Apple silicon

On 5 December 2023 Awni Hannun posted that Apple machine learning research was releasing MLX: an array framework for Apple silicon, “i.e. your laptop.” The GitHub org is `ml-explore`. The citation the repo asks for names four authors with equal contribution: Hannun, Jagrit Digani, Angelos Katharopoulos, and Ronan Collobert. The library license is MIT. The license on the weights you convert is whoever’s card you started from.

The first public examples were not a product landing page. They were a Llama v1 7B running on an M2 Ultra, a LoRA fine-tune loop, Mistral generation, Stable Diffusion, and Whisper. `mlx-lm` later became the language-model shelf: convert a Hub card, generate, quantize, fine-tune LoRA on a Mac. `mlx-community` on the Hub became the unofficial CDN of those converted files, the way GGUF orgs became a CDN for `llama.cpp`.

This is the other local box (`ollama-local-box`), with a different silicon vendor and a different aesthetic: not a C++ port of Llama, a framework that wants to be NumPy-and-PyTorch-shaped for M-series unified memory.

## Why a new framework, not just Metal in llama.cpp

`llama.cpp` already had Metal. The first `llama.cpp` commit is 10 March 2023 (`llama-cpp-gguf`). MLX is Apple writing the library they want researchers on Macs to use: composable, Pythonic, lazy, close to the unified memory model that makes a 128 GB M-series machine a strange little workstation. Arrays live where the GPU and the CPU can both see them. That is the hardware sentence. The software sentence is a NumPy-shaped API plus a compiler that fuses ops when you finally evaluate.

Apple’s interest is not charity. A framework that makes Macs good at local models makes Macs better at a job Windows laptops with NVIDIA cards already had. The public object is still MIT code. The conversion step from Hugging Face weights is the joint. When it works, it is pleasant. When a new architecture lands on a Tuesday, there is a lag until someone writes the MLX bits or waits for `mlx-lm` to grow them.

December 2023 was a crowded month: Mixtral 8x7B on the 11th (`mixtral-open-moe`), Keras 3, Phi-2 on the 12th (`gemma-phi-small-weights`), MLX on the 5th. Local inference was becoming a platform fight, not a single C++ repo. One winter, three answers to “I have a desk”: ggml, a new Apple array library, and a small MIT research model from Microsoft.

## What MLX is not

It is not a cluster trainer, though `mx.distributed` later let people pipeline a giant card across two Mac Studios. It is not vLLM. It is not Core ML, though models can end up in adjacent Apple runtimes. It is not a Hub. It is not permission to run Llama 3 without Llama 3’s license. It is not Ollama; Ollama is a named-model daemon that often sits on `llama.cpp`. MLX is a library you import.

People who say “I run everything in MLX now” are making a hardware statement. The statement is fine if they own the hardware. A shop that standardizes on CUDA and then buys a fleet of Macs for “the MLX story” has bought a second stack. Conversion is the tax. Plan the tax.

## Unified memory as the actual product

A 128 GB M-series box can hold a model that a 24 GB NVIDIA laptop cannot. MLX is written for that fact. `llama.cpp` can also use that fact. MLX wants you to write Python that feels like research — `import mlx.core as mx` — and to fine-tune a LoRA without leaving the machine (`peft-lora-adapters`). `llama.cpp` wants you to run a binary. Pick the joint that matches the job.

The Hub org `mlx-community` is a second landlord, same as an Ollama library name. Trust the conversion, or run the first-party convert script from official `safetensors` and keep the output. A random 4-bit MLX file is a random 4-bit MLX file. The parent license does not change because the array library is MIT.

## 2026 look

`mlx-lm` model lists track the same names as Ollama with a delay: Llama, Qwen, Mistral, Gemma, sometimes gpt-oss. Hannun’s later public notes about running a 4-bit Kimi-class trillion-parameter MoE across two 512 GB M3 Ultras are a 2025–2026 flex, not a 2023 laptop story. Both are real. Name the machine.

Read the `ml-explore/mlx` README, the December 2023 announcement thread, and the `llama.cpp` chapter next door. Two answers to “I have a laptop.” Different joints. Apple’s MIT is a library license. Llama’s community PDF is still in the crate if that is the card you converted. Write both on the whiteboard.

If you chase new cards, you will live in convert scripts. If you pin last quarter’s card, you will be happy. That sentence is the whole local-inference industry, restated for a different silicon vendor.

## Sources

Awni Hannun, MLX announcement thread, 5 December 2023. ml-explore/mlx README (authors; MIT). mlx-lm and mlx-community Hub documentation. llama.cpp Metal backend as the other Mac path.

See: `llama-cpp-gguf`, `ollama-local-box`, `pytorch-2016-define-by-run`, `peft-lora-adapters`.
