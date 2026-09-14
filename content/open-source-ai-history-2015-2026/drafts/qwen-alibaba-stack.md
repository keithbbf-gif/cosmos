---
title: Qwen and the Alibaba stack
slug: qwen-alibaba-stack
series: open-source-ai-history-2015-2026
status: draft
voice_check: edited
reading_order: 35
word_target: 600-1800
era: "2023–2026"
stack:
  - qwen
---

# Qwen and the Alibaba stack

Alibaba’s Qwen (Tongyi Qianwen) team posted Qwen-7B and Qwen-7B-Chat on 3 August 2023. The code was Apache 2.0. The weights used the Tongyi Qianwen License. That split — clean code, custom weight terms — is the first-generation crate label. Qwen-72B and 1.8B followed on 30 November 2023. Then the generations came fast enough that a chapter has to be a clock, not a biography.

Qwen1.5 (5 February 2024), including a later MoE. Qwen2 (6 June 2024). Qwen2.5 (19 September 2024) plus Coder and Math lines — the generation a lot of 2025 distillations sat on. QwQ-32B-Preview (28 November 2024), a reasoning preview. Qwen3 (29 April 2025), hybrid thinking / non-thinking, MoE up to 235B-A22B, with the team stating that open-weight Qwen models were now Apache 2.0. Qwen3-Coder (22 July 2025), including a 480B-A35B instruct. Qwen3.5 (16 February 2026) and Qwen3.6 (16 April 2026), still Apache in the project’s news log.

The first-party filing cabinet is QwenLM on GitHub. Use it. Secondary timelines are maps. Hidekazu Konishi’s open-weights timeline (updated 26 July 2026) is a finding aid this pack used and then checked against those logs. If a date in this chapter ever fights a log, the log wins.

Qwen-VL and Qwen-Audio siblings existed early enough that “Qwen” was never only a text 7B. The 30 November 2023 72B / 1.8B drop is the first time the shelf looked like a hardware store: a big card, a tiny card, and a chat pair, still on Tongyi terms. People who pin “Qwen-7B” in 2026 without a generation are pinning a 2023 license.

## Why this stack is a stack

Not one 7B, a shelf: dense sizes from sub-billion to 72B, MoE, VL, coder, math, reasoning. Hugging Face collections for each generation. A multilingual default that is not an afterthought — Chinese and English as a pair, then a long tail. If Llama is a herd, Qwen is a hardware store.

2.5 in particular became the base DeepSeek-R1 distilled into (`deepseek-r1-january-2025`). That is a historical hinge: an Alibaba dense family as the student of a DeepSeek teacher. The open-weight world is not a set of isolated brands.

## License movement

Tongyi Qianwen License on early weights. Apache 2.0 as the stated weight license from Qwen3 onward, per the team’s own Qwen3 repo notes. If you are pinning a 2023 7B, you are not on the 2025 terms. Read the card in front of you. This series will not collapse three years of PDFs into one adjective.

## 2026 look

Qwen3.5 / 3.6 are the current generation as of this pack’s spring-2026 sources; check the GitHub news log before you write “current” in a later month. The habit to keep is: Alibaba ships often, documents on GitHub, and uses the Hub as a CDN. The habit to drop is: treating “Qwen” as one model.

If a paper says “we used Qwen,” ask which generation, which size, whether it is a coder line, and which license file sat in the repo that week.

Write the generation, the size, the line (base / instruct / coder / VL / math / reasoning), and the GitHub news-log date. “Qwen” is not a pin. A 2023 7B and a 2026 3.6 MoE do not share a license story or a tokenizer story. Shops that store one `QWEN_MODEL` env var are storing a bug. If you run `DeepSeek-R1-Distill-Qwen-32B`, you are in both this chapter and the R1 chapter. The card names both parents if it is honest.

Qwen’s English benches are fine. Qwen’s Chinese benches are the reason the stack exists. A Western shop that treats Qwen as “Llama but Apache” is leaving the actual product on the table. A procurement shop that treats Qwen as “the Chinese model” is leaving the generation and the license on the table. Name the card.

A stack that ships Qwen-VL and Qwen-Coder as named lines is a stack that does not treat those jobs as fine-tunes you must invent. Pin the line. A VL card in a text-only server is a waste of memory. A base card in a coding agent is a waste of a line that already existed. `[CITE NEEDED]` is allowed when a news log is a month and not a day.

## Sources

QwenLM/Qwen and QwenLM/Qwen3 GitHub news logs. Qwen-7B, 3 August 2023. Qwen2.5, 19 September 2024. Qwen3, 29 April 2025. Qwen3.5 / 3.6 notes, February–April 2026. Hub collections.

See: `deepseek-r1-january-2025`, `chinese-open-weight-wave`, `mistral-7b-apache`, `twenty-twenty-six-the-stack`.
