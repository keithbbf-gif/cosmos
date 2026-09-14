---
id: mmh-39
title: "BLIP and BLIP-2: bootstrapping, then a Q-Former bargain"
slug: blip-and-blip2
series: multimodal-ai-public-history
stage: draft
status: staged
publish: false
novelty: public-record
era: "2022-2023"
topics: [BLIP, BLIP-2, Li, Q-Former, Salesforce]
voice_check: edited
voice_check_date: 2026-09-14
---

# BLIP and BLIP-2: bootstrapping, then a Q-Former bargain

Li, Li, Xiong, and Hoi's *BLIP* (ICML 2022,
arXiv:2201.12086) is a public captioner-and-filter
story: generate captions, filter noisy web pairs,
train a model that can both retrieve and generate.
The bootstrapping is in the name. The code and
checkpoints went out. For a year, "use BLIP to
caption the frames" was a real pipeline step in
other people's papers.

Li, Li, Savarese, and Hoi's *BLIP-2* (arXiv:2301.12597,
30 January 2023; ICML 2023) is the bargain. Freeze
a strong image encoder. Freeze a strong LM. Train
a thin **Q-Former** — a transformer that queries
the image with learnable queries and sits between
the two frozen giants. Two-stage training: vision-
language representation, then vision-to-language
generative learning. The paper's pitch is
parameter efficiency. The historical pitch is
that **you can buy a VLM by training the
connector**.

That bargain is why BLIP-2 belongs next to Frozen
and Flamingo rather than only next to BLIP. All
three treat the LM as an expensive object you
would rather not retrain. They differ in the
connector (prefix, gated xattn, Q-Former). 2023
open work will try linear projections too (LLaVA).
Connectors are a genre. BLIP-2 named one that
people actually downloaded.

What was public: paper, code, checkpoints, a demo
culture. What was not: a claim that Q-Former is
the last connector. InstructBLIP (Dai et al.,
2023) will instruction-tune the stack. Later
models will drop the Q-Former for simpler maps
when the LM and the data get larger. Simpler is
not always better. It is cheaper to explain.

I trust BLIP-2 as the **open Flamingo-adjacent
object of early 2023**. If you could not run
Flamingo, you could run this. Running changes a
field. PDFs do not always.

---

**Stage:** draft. **Claim type:** public-record recap. This piece does
not propose a new method or a new research result.
