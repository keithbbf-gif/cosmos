---
title: "Context windows: 2K to a million"
slug: context-windows-2k-to-a-million
meta_description: "GPT-3's 2048 tokens to Gemini 1.5's million and Llama 4 Scout's 10M claim. Longer is not the same as used."
tags: [context, gemini, claude, llama, 2024]
era_start: 2023-03
citations:
  - "GPT4 https://openai.com/index/gpt-4-research/"
  - "GEMINI15 https://blog.google/technology/ai/google-gemini-next-generation-model-february-2024/"
  - "LLAMA4 https://ai.meta.com/blog/llama-4-multimodal-intelligence/"
status: draft
voice_check: human
---

GPT-3's context window was 2,048 tokens. That is a short story, not a repo. GPT-4 launched on 14 March 2023 at 8,192, with a 32,768-token sibling in limited access. Claude 2.1 advertised 200K in November 2023. GPT-4 Turbo (6 November 2023, DevDay) put 128K on a price list. Google's Gemini 1.5 Pro (15 February 2024) made a million tokens the demo: a 44-minute Apollo video, a 402-page transcript, a 100,000-line codebase, in the blog's telling.

Meta's Llama 4 Scout (5 April 2025) was sold with a 10-million-token context. `[CITE NEEDED]` on independent needle tests at that length; vendor blogs are not a retrieval study.

The number got cheap to print. Using the middle of the window did not.

## Why the window grew

Attention is quadratic if you are naive. A 1M window at full dense attention is a finance event. The 2023–25 tricks were sparse and cached: sliding windows, grouped-query attention, ring attention, state-space cousins (Mamba, 2023), prefix-cache reuse, and a lot of "we will not tell you the exact pattern." Long-context is a systems paper wearing a product number.

The product reason was RAG fatigue and PDF fatigue. Customers wanted to drop the binder in the box. A 128K window is a small binder. A million is a shelf. A ten million is a filing cabinet you should not trust without a test.

## Lost in the middle

Liu et al., *Lost in the Middle* (2023), measured a U-shaped use of context: models attend to the start and the end and drop the haystack's center. Every serious long-context vendor now runs some form of "needle in a haystack." Many needles are single magic sentences, which is a toy. A real test is: a contradictory clause on page 187, a table on page 40, a later page that updates the table. Ask which number the model uses.

Gemini 1.5's public demos were impressive and still left this question open. Claude's 200K was usable for a contract if you also cited the clause. GPT-4 Turbo's 128K was the first window many production RAG systems could *stop* chunking for mid-size docs — and then they kept chunking, because citation and recency required it.

Long context does not retire retrieval. It changes the chunk size. If you cannot point at the span, you have a longer hallucination.

## Cost and caching

A needle test that plants one UUID is a start. A better test plants a *correction*: page 12 says 14 days; page 88 says 7 days after a policy change. If the model cites 14, it cannot use the middle *or* it cannot resolve conflict. Product policy: prefer the later dated span, or refuse. Do not average.

A long prompt is a long bill unless you cache the prefix. Anthropic, OpenAI, and Google all shipped prompt-caching products in 2024–25. The economics flip: the first request pays, the next hundred with the same binder are cheaper. That is the actual enabler of "upload your corpus." Without cache, a million-token system prompt is a stunt.

Latency follows the same curve. Prefill on a fat prompt is the part users feel. Speculative decoding and cached KV help. They do not make a 10M-token first request feel like a 2K chat.

## Position encodings and the ugly middle

RoPE (Rotary Position Embeddings, Su et al., 2021) and its stretch tricks (NTK-aware, YaRN, 2023–24) are how a model trained at 4K or 8K gets sold at 32K or 128K. Sometimes the stretch works. Sometimes the model "sees" the tokens and still cannot bind a variable across a 40K-token gap. A vendor who will not say whether the window is *trained* or *extrapolated* is selling you a stretch. Ask.

Claude's early 100K (Claude 2, July 2023) was usable for a contract because the jobs were "find the indemnity" — a needle. It was less usable for "reconcile these four exhibits." Those are different tasks. Design the eval to the second, or you will celebrate the first and ship the second.

## What changed in product design

2020–22: stuff the best three passages into 2K and pray.

2023: stuff the best twenty into 8K, or buy 32K and stuff a paper.

2024: offer "whole PDF" as a button, then quietly retrieve anyway.

2025–26: advertise millions, cache the tenant's corpus, still fail on the updated table in the middle.

The honest 2026 design is hybrid: retrieve the candidates, put them in a window the model can actually use (measured, not advertised), cite the spans, and keep a log of what was in the window when the answer was born. The window size is a budget. Treat it like one.

## Opinion

Context length was the easiest number to inflate after parameter count got embarrassing. Some of the inflation was real engineering. A lot of it was a demo of a needle the vendor hid.

Measure your own middle. If the model cannot use page 187, you do not have a million-token product. You have a million-token invoice.
