---
title: Gemma, Phi, and the small weights
slug: gemma-phi-small-weights
series: open-source-ai-history-2015-2026
status: draft
voice_check: edited
reading_order: 37
word_target: 600-1800
era: "2023–2026"
stack:
  - gemma
  - phi
---

# Gemma, Phi, and the small weights

Not every open-weight story is a 70B. Google’s Gemma and Microsoft’s Phi are the two corporate small-model lines this series keeps on the table: weights you can fetch, papers you can read, licenses you have to read twice. Llama 3.2 1B/3B, Ministral, and the Qwen 0.5B-class cards share the drawer. This chapter walks the two that came with a research accent and a company behind them.

## Phi: data diet, MIT more often than not

Microsoft Research’s Phi-2 (2.7B, 12 December 2023, MIT) was the surprise-power small model of that winter — the same week as Mixtral and MLX. Phi-3-mini (3.8B, 23 April 2024, MIT, 128K) made a long context a small-card feature, five days after Llama 3. Phi-3-vision and larger Phi-3 sizes followed. Phi-4 (14B, 12 December 2024, MIT on the later Hub weights) and Phi-4-reasoning (30 April 2025, MIT) kept the research-lab accent: careful data, modest size, a model card that talks like a paper.

Phi is easy to underestimate because it is not a Hub social phenomenon. It is a research product that happens to be MIT. For a lot of internal tools, that is the correct crate. Microsoft Research’s cards talk like papers. They are easy to miss on the Hub’s social graph. Missing them is a shop error if you need a small MIT text model.

## Gemma: Gemini’s public sibling, then Apache

Gemma (2B / 7B, 21 February 2024) was “built from the same research and technology used to create the Gemini models,” under the Gemma Terms of Use — a custom instrument, not Apache. That sentence is a kinship claim, not a weight claim. You did not get Gemini. You got Gemma under Gemma terms. Gemma 2 (9B / 27B, 27 June 2024) stayed on those terms. Gemma 3 (1B / 4B / 12B / 27B, 10 March 2025) added vision, 128K, 140+ languages, still Gemma Terms. Gemma 3n (26 June 2025) was the mobile-first pair.

Gemma 4 (2 April 2026) is the license event: Apache 2.0, multimodal including audio in Hugging Face’s writeup, sizes from E2B/E4B through a 26B-A4B MoE and a 31B dense, agentic framing from Google DeepMind’s blog. The Gemmaverse download counts in that blog are vendor counts. The license change is a file.

A company that spent two years on custom terms and then shipped Apache is allowed to do that. A shop that pinned Gemma 2 and assumes Gemma 4’s terms is not. A license scanner that keys on the word “Gemma” will be wrong after 2 April 2026. Split the family.

## Small as a job, not a consolation

Llama 3.2 1B/3B, Ministral 3B/8B, Gemma, Phi, the Qwen 0.5B-class cards — the edge drawer filled in 2024–2026. TFLite’s instinct (`tensorflow-serving-and-tflite`) came back as GGUF and LiteRT. A phone model is not a failed 70B. It is a different joint: RAM, battery, offline. A 31B dense Gemma 4 is not a phone model. The family contains both. Name the size.

Need MIT text-only, 2024–2025: Phi-3/4. Need Apache multimodal, 2026: Gemma 4. Need Llama-shaped edge: 3.2 1B/3B (community license). Need a coder: Qwen-Coder small or Ministral. The sentence “just use a small model” is not a pin.

## 2026 look

If you need MIT and a 3–14B text model, Phi is still a first card to read. If you need Apache and a 2026 multimodal small model, Gemma 4 is the Google answer as of April. If you need a Llama-shaped edge model, 3.2 1B/3B still exists. Name the license. Name the year.

Read the Gemma 4 blog (2 April 2026) next to the Gemma 1 Terms of Use. They are not the same instrument. That is the chapter. Then read a Phi-4 card if you want the MIT shelf. Two companies, two habits, one drawer.

## Sources

Microsoft, Phi-2, 12 December 2023; Phi-3, 23 April 2024; Phi-4 card, December 2024; Phi-4-reasoning, 30 April 2025. Google, Gemma, 21 February 2024; Gemma 2, 27 June 2024; Gemma 3, 10 March 2025; Gemma 3n, 26 June 2025; Gemma 4, 2 April 2026. Hugging Face, “Welcome Gemma 4,” 2 April 2026.

See: `llama-3-april-2024`, `licenses-that-are-not-open`, `tensorflow-serving-and-tflite`, `twenty-twenty-six-the-stack`.
