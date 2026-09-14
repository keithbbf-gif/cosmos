---
title: vLLM and PagedAttention
slug: vllm-paged-attention
series: open-source-ai-history-2015-2026
status: draft
voice_check: human
reading_order: 29
word_target: 600-1800
era: "2023–2026"
stack:
  - vllm
---

# vLLM and PagedAttention

On 20 June 2023 Woosuk Kwon, Zhuohan Li, and colleagues at UC Berkeley’s Sky Computing Lab published a blog post: “vLLM: Easy, Fast, and Cheap LLM Serving with PagedAttention.” The library had already been running Chatbot Arena and the Vicuna demo for about two months. LMSYS, a small research team, was serving a popular chat model without a hyperscaler’s serving stack. That deployment is the historical object as much as the later SOSP paper.

The idea is ordinary if you have seen an operating system: the KV cache is virtual memory. You allocate pages as sequences grow, you free them when a request ends, you stop reserving a giant contiguous slab for the worst-case length. Fragmentation drops. Concurrency rises. The June post’s vendor-shaped number — “up to 24× higher throughput than Hugging Face Transformers” — is a blog number. Treat it as a blog number. The paper (arXiv:2309.06180; SOSP, Koblenz, 23–26 October 2023) compares against FasterTransformer and Orca and talks 2–4× at matched latency. Ask “than what, at what concurrency, at what precision” before you reprint either figure.

![Two engines: llama.cpp versus vLLM.](../assets/local-vs-serve/engines.svg)

*Figure 4. Two jobs. This chapter is the right box.*

## Serving is not generating one token for yourself

`llama.cpp` is a good single-user engine. A product that has fifty people talking at once is a different program. Continuous batching — inserting new requests when old ones finish, without restarting the world — is the other half of vLLM’s story. PagedAttention makes that batching memory-safe. A naive KV reservation for max length times batch is how you run out of memory with the GPU half empty. The paper’s claim is that waste drops toward a few percent. Your model and your length distribution have other numbers. Benchmark your queue.

The library is Python-facing and GPU-first. It speaks Hugging Face model names. It grew tensor parallel, a zoo of quants, prefix caching, speculative decoding, and an OpenAI-shaped API. It became the default sentence for “we self-host a 70B.” Comparing vLLM throughput to `llama.cpp` tokens-per-second on a single prompt is a category error. The first is a queue. The second is a desk.

## Why this is an open-stack chapter

Because the paper is public, the code is public, and the engine is how Llama 3.1 405B and later open MoEs became something a company could offer without sending every token to a closed API. Training can be PyTorch. Serving, increasingly, is not your training loop. TensorFlow Serving said this in 2016 (`tensorflow-serving-and-tflite`). vLLM said it for autoregressive transformers.

vLLM is not the only server (TGI, TensorRT-LLM, lmdeploy, SGLang). It is the one whose paper named the pager metaphor the field kept, and the one whose June 2023 blog is dated to the same summer as Llama 2 and Ollama. The serving split of 2023 — desk versus rack — is this chapter and the two before it.

The OpenAI-shaped API is why it replaced a lot of custom FastAPI wrappers. Tools did not want a new schema. They wanted a new host. That is funny and true, and it is the same compatibility Ollama chose for the laptop (`ollama-local-box`).

## What PagedAttention is not

It is not a model. It is not a license. It is not a guarantee that your 4-bit scheme matches the paper’s benches. It is not free of operational work — you still size KV pages, you still watch GPU memory, you still pin a card.

Mixtral, DeepSeek-V3, Llama 4, gpt-oss — routers and experts and, later, images. The pager had to grow. If a new architecture is slow in vLLM this week, wait a release or help. The library’s job is to chase the Hub. The Hub does not wait.

## 2026 look

A `docker run` of vLLM on an 80 GB card, pointed at a Hub id, is a boring production object. That boredom is success. The interesting remaining work is MoE routing, multimodal batches, and million-token contexts (`llama-4-scout-maverick`, DeepSeek-V4). The pager metaphor still holds. The page size arguments got more exotic.

Read the 20 June 2023 post for the date. Read the SOSP paper for the idea. Read the vLLM docs for the flags. If you have one user, you do not need this chapter. If you have a hundred, you do. Count the users before you count the tokens per second.

## Sources

Kwon, Li, et al., vLLM blog, 20 June 2023. Kwon et al., arXiv:2309.06180 / SOSP 2023. vLLM documentation and GitHub. LMSYS Chatbot Arena / Vicuna demo as the first public deployment named in the blog. Red Hat Developer, vLLM vs llama.cpp, 2025–2026.

See: `llama-cpp-gguf`, `ollama-local-box`, `tensorflow-serving-and-tflite`, `llama-3-1-405b`.
