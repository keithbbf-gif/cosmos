---
title: Scout, Maverick, and the missing Behemoth
slug: llama-4-scout-maverick
series: open-source-ai-history-2015-2026
status: draft
voice_check: human
reading_order: 32
word_target: 600-1800
era: "2025–2026"
stack:
  - llama
---

# Scout, Maverick, and the missing Behemoth

On Saturday 5 April 2025 Meta released Llama 4 Scout and Llama 4 Maverick: natively multimodal mixture-of-experts models, 17B active parameters each in Meta’s telling, Scout with a 10-million-token context claim and Maverick with a 1-million-token window, under the Llama 4 Community License. The blog post, “The Llama 4 herd,” previewed Llama 4 Behemoth as a still-training teacher “not yet releasing.” Reuters and TechCrunch dated the launch the same day. As of September 2026, Scout and Maverick have public cards; Behemoth does not.

Meta’s own wording on this generation preferred “open-weight.” That is the honest noun. The company had spent two years calling Llama “open source.” The fourth generation quietly stood up. This series treats that edit as one of the few honest marketing corrections in the clock (`open-weight-vs-open-source`).

## MoE as a Meta architecture

Mixtral had made open MoE ordinary in December 2023 (`mixtral-open-moe`). DeepSeek-V2 and V3 had made it a Chinese-lab specialty. Llama 4 is Meta arriving with early-fusion multimodal MoE and a context-length headline. Serving MoE is a different vLLM problem than serving 70B dense. Shops that skipped 4 are not necessarily behind. They may be counting active parameters and router overhead.

Native multimodal means image (and, in the post’s training description, video) in the same weights, not a bolted vision adapter only. Llama 3.2 had already shipped vision siblings. 4 made the herd’s flagships multimodal from the start. If vision is in the same weights, your text-only deploy may still load vision-shaped capacity. Active parameter counts (17B in the post) are the inference bill. Total expert counts are the memory bill. Both belong on the ops sheet. If you do not need images, a 3.3 70B may be the cheaper card. Native multimodal is a capability and a bill. The April 2025 post sells the capability. Your cluster pays the bill.

## Context length as a serving claim

10M tokens on Scout is a claim you test with your retrieval job, not with a chat vibe. Most products will never pack 10M. Some legal and code jobs will try. The KV cache for a serious fraction of that window is the real product. PagedAttention’s children have work to do (`vllm-paged-attention`). A card that says 10M and a server that OOMs at 200K are a pair you should expect until you measure.

Maverick’s 1M window is already a different product than Llama 3.1’s 128K. Do not flatten “Llama 4 context” into one number. Name the animal.

## Behemoth as a public non-release

A previewed 2T-class teacher that never ships is still a historical object. It tells you Meta wanted a distillation story (3.1’s story) and then did not, or could not, put the teacher on the Hub. Secondary reporting through 2025–2026 described delays and internal doubt. This series will not pretend to have the memo. Write: previewed 5 April 2025; not released as of 2026-09. Do not write a conspiracy. Do not write a ship date you do not have.

Non-releases matter because they shape the “open” story. A herd with a missing bull is a different zoo. First-party silence is also a source.

## Arena and the other benches

Llama 4’s launch week included leaderboard drama the internet enjoyed too much. This chapter will not adjudicate contamination or routing. It will say: multimodal MoE plus a 10M context claim is a serving and eval problem the field did not have in 2023. If your eval is a short English chat, you are not testing Scout’s point. If you must mention the drama, mention it as a warning about short-context leaderboards for a long-context multimodal MoE. Then go back to the cards.

## 2026 look

The current Meta open-weight line, as of September 2026, is this herd plus the still-served 3.x dense models. Behemoth remains a preview. The Community License remains the crate label. Read the 5 April post, the Scout card, the Maverick card, and the license. If a slide says “Llama 4” without a name, ask which animal.

The series’ Llama thread ends here as a family, not as a victory. Qwen3, DeepSeek-V4, gpt-oss, and Gemma 4 are other rooms in the same year (`twenty-twenty-six-the-stack`).

## Sources

Meta AI, “The Llama 4 herd,” 5 April 2025. Reuters, 5 April 2025. TechCrunch, Kyle Wiggers, 5 April 2025. Llama 4 Community License. Hub cards for Scout and Maverick (Behemoth absent as of 2026-09).

See: `llama-3-1-405b`, `mixtral-open-moe`, `open-weight-vs-open-source`, `twenty-twenty-six-the-stack`.
