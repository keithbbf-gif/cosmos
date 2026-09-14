---
title: DeepSeek-R1, 20 January 2025
slug: deepseek-r1-january-2025
series: open-source-ai-history-2015-2026
status: draft
voice_check: human
reading_order: 36
word_target: 600-1800
era: "2023–2026"
stack:
  - deepseek
---

# DeepSeek-R1, 20 January 2025

DeepSeek-AI’s GitHub release that Monday put DeepSeek-R1 and DeepSeek-R1-Zero on the table, plus six dense distillations into Qwen2.5 and Llama families, under the MIT License. R1 sits on DeepSeek-V3-Base (V3 itself: 26 December 2024, 671B total / 37B active, 128K, 14.8T tokens, code MIT, weights under DeepSeek’s model license). R1-Zero is the reinforcement-learning-on-a-base story the paper emphasizes. R1 is the version with the more usable pipeline. The distillations are what a 24 GB card actually ran.

The claim, in the repo’s own English, was comparability with OpenAI’s o1 on math, code, and reasoning benches they listed. Treat that as a vendor table. The historical fact is MIT weights on a reasoning model in January 2025, and a week in which a lot of closed-lab assumptions looked expensive.

## The line before R1

DeepSeek Coder and DeepSeek LLM (7B / 67B) in November 2023. DeepSeek-V2 (6 May 2024): 236B / 21B active, 128K, Multi-head Latent Attention, DeepSeekMoE. DeepSeek-Coder-V2 (June 2024). V3 in December. The lab was not a January surprise. January was the month the rest of the English-language internet noticed.

MLA and DeepSeekMoE are the systems reasons V2/V3 served cheaper than their total parameter counts. The R1 paper is the reason people talked about “reasoning in the open.”

## Distill as a public mechanism

R1-Distill-Qwen-32B and R1-Distill-Llama-70B are named objects on the Hub. They are also a license sandwich: MIT on the distill, Llama or Qwen on the base architecture and, depending on the file, on the student weights’ terms. Read both cards. The January repo’s MIT claim is about the R1 family they uploaded. It is not a wand over Meta’s community license if you start from a Llama student.

The idea — a strong reasoner teaching a smaller dense net — is 3.1’s distillation story (`llama-3-1-405b`) with a different teacher and a more permissive teacher license.

## After January

DeepSeek-V3.1 (21 August 2025, hybrid thinking, MIT weights on the Hub). V3.2 (1 December 2025, Sparse Attention, MIT). DeepSeek-V4 Preview (24 April 2026): V4-Pro 1.6T / 49B active, V4-Flash 284B / 13B, 1M context as a service default, open weights announced on deepseek.com. Each is a later crate. R1 remains the cultural door.

## 2026 look

A lot of local “reasoning” GGUFs are R1 distillations, not V4-Pro. Name the file. The January GitHub README is still the right primary source for R1. The 24 April 2026 news post is the right primary source for V4. Do not let a podcast flatten them.

This chapter will not diagnose a stock-market week. It will say: MIT on a reasoning dump changed what a shop could pin. Closed o-series models remained closed. The open stack gained a teacher.

Zero is the RL-on-base story the paper wants you to remember: reasoning traces that look like traces without a SFT warm start, in their telling. R1 is the usable sibling. Distills are the laptop siblings. A thread that says “R1” without which file is a thread that cannot be replicated.

MIT on the January upload is the legal shock. V3’s weights had used a DeepSeek model license. R1’s MIT is a different crate. Do not back-apply MIT to every DeepSeek file. Do not back-apply the model license to R1.

Closed reasoning APIs had a price and a waitlist. A MIT reasoner plus distillations had a download. Shops that had been about to sign a bill ran a distill instead. Some came back to the API. Some did not. This series will not diagnose a market or a stock-market week. It will say the file existed and the bill had a competitor.

R1’s public story includes reasoning traces that people pasted everywhere. Traces are evals you can argue with. They are also training data if you scrape them. The MIT license on the January upload is not a license to every pasted trace’s downstream rights. If you train on traces, write that down.

If you are still running a Qwen-32B distill in September 2026, you are running January 2025. That is allowed. Name it. V4 Preview (24 April 2026) is a later crate: 1M context as a service default, two MoE sizes, open weights announced on deepseek.com. Different card. Different chapter energy.

## Sources

deepseek-ai/DeepSeek-R1, 20 January 2025. deepseek-ai/DeepSeek-V3, 26 December 2024. DeepSeek-V2 GitHub, 6 May 2024. DeepSeek, “DeepSeek-V4 Preview,” 24 April 2026.

See: `qwen-alibaba-stack`, `gpt-oss-august-2025`, `mixtral-open-moe`, `chinese-open-weight-wave`.
