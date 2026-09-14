---
title: The Chinese open-weight wave
slug: chinese-open-weight-wave
series: open-source-ai-history-2015-2026
status: draft
voice_check: human
reading_order: 38
word_target: 600-1800
era: "2023–2026"
stack:
  - qwen
  - deepseek
---

# The Chinese open-weight wave

By 2024–2026 a lot of the files a Western shop actually pinned were trained in China: Qwen, DeepSeek, and — named here so the map is not two-colored — Yi, GLM, InternLM, Kimi, MiniMax, and others this series does not give a full clock. The wave is not a conspiracy and not a monolith. It is a set of labs that published weights, often with strong multilingual and MoE stories, on the same Hub the rest of this series already uses.

English-language coverage often arrived late and loud (R1 in January 2025). The GitHub commits arrived earlier. A history that starts the wave at R1 is a history of Western attention, not of the repos. Qwen-7B is 3 August 2023, two weeks after Llama 2 (`qwen-alibaba-stack`). DeepSeek Coder and DeepSeek LLM are November 2023 (`deepseek-r1-january-2025`). The wave is as old as the Llama-2 year. The noise is younger.

## Two clocks we already walked

Qwen is Alibaba Cloud’s prolific shelf, Tongyi Qianwen License on early weights, Apache on later generations per the team. DeepSeek is the MLA / MoE / R1 / V4 line, MIT on R1, a model license on some earlier weights. If you only know those two, you already know the wave’s center of gravity for English-language engineering Twitter. If you only know those two, you do not know the wave.

## Other public names, without fake completeness

01.AI’s Yi-6B and Yi-34B landed on 2 November 2023 as bilingual English/Chinese base models; 200K-context siblings followed on the 5th; chat and quantized cards on the 23rd. Later Yi READMEs on the Hub say Apache 2.0 on code and weights. Older snapshots on the same org mentioned a community agreement and an email for commercial use. That disagreement is the lesson, not a gotcha: open a current `LICENSE` before you write “Yi is Apache.” Kai-Fu Lee’s lab is in the public record as the author. This series will not invent a 2023 valuation.

Zhipu’s GLM / ChatGLM line, Shanghai AI Lab’s InternLM, Moonshot’s Kimi, MiniMax — each has Hub orgs, papers, and license PDFs that are not interchangeable. Some files are Apache. Some are model-specific. Some are research. A census would be a different pack. This pack names the two clocks it actually walked and refuses a fake third clock. Open a Hub org before you write a sentence about any of them.

## Why the Hub made this one ecosystem

`deepseek-ai/DeepSeek-R1-Distill-Qwen-32B` is a Chinese teacher and a Chinese student on a French-American website, run through a Californian-founded library, often served on NVIDIA GPUs. National narratives that want a clean split will hate that sentence. The file system does not care.

R1 → Qwen2.5 is a graph you can draw. Llama 3.1 405B → someone’s 8B is another. The wave is not a closed loop inside one country. The Hub is the meeting point. Draw the graph with org ids, not with flags, unless a paper names a flag.

Export controls and chip supply are real political objects. They are also not this series’ primary sources. Where a paper names an H800 or an NPU, name it. Where a podcast names a secret cluster, mark `[CITE NEEDED]` or omit. This series’ job is files.

## 2026 look

DeepSeek-V4 Preview (24 April 2026) and Qwen3.6 (April 2026) are the current heads of the two clocks we track, as of the first-party posts cited in those chapters. Other labs will have moved the week after this pack is staged. The useful look is not “China vs the US.” It is “which card, which license, which active parameter count.”

If a procurement conversation uses “Chinese model” as a predicate, ask them to name the org id. Predicates are not crate labels. A Qwen collection, a DeepSeek collection, a Meta collection — same website, same `from_pretrained`, same LFS. National policy may care about origin. The loader does not. A shop that must care about origin should record the org id in the pin.

## Sources

QwenLM GitHub news logs. DeepSeek GitHub and deepseek.com news. 01-ai/Yi-34B Hub card (2 November 2023; later Apache language). Hub orgs: `Qwen`, `deepseek-ai`, `01-ai`, and the other names above as starting points, not as a census.

See: `qwen-alibaba-stack`, `deepseek-r1-january-2025`, `hub-as-distribution`, `twenty-twenty-six-the-stack`.
