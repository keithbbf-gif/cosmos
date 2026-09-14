---
id: mmh-37
title: "Frozen, 2021: a language model that looks, a little"
slug: frozen-lm-looks-at-pictures
series: multimodal-ai-public-history
stage: draft
status: staged
publish: false
novelty: public-record
era: "2021"
topics: [Frozen, Tsimpoukelli, prefix, few-shot]
voice_check: edited
---

# Frozen, 2021: a language model that looks, a little

Tsimpoukelli, Menick, Cabi, Eslami, Vinyals, and Hill's
*Multimodal Few-Shot Learning with Frozen Language Models*
(NeurIPS 2021, arXiv:2106.13884) is the public paper that
makes a later Flamingo diagram feel inherited. Keep a
pretrained language model still. Train a visual encoder
so that its outputs can be consumed as a **prefix** — a
soft prompt — the LM already knows how to continue. Show
the system a few interleaved examples. Ask a new
question about a new image.

This is not CLIP. CLIP aligns two towers and retrieves.
Frozen keeps generation as the LM's job and treats
vision as a way to start the sentence. The few-shot
claim is the 2021 point. The authors want the
multimodal system to inherit in-context learning, which
was then a language-model headline, without finetuning
the LM.

Limits, public and useful:

- The visual prefix is a **bottleneck**. A handful of
  vectors have to carry the photograph. Later papers
  will add more tokens, perceivers, or Q-formers
  because this bottleneck is real.
- The tasks are research tasks. This is not a 2023
  chat app.
- "Frozen" is a training choice, not a virtue. You
  save the LM. You also inherit the LM's refusals,
  priors, and dated knowledge.

I start the VLM stage here so LLaVA does not look like
year zero. LLaVA will also connect a frozen (or partly
frozen) visual encoder to an LM. The 2023 difference
is instruction data and a larger public LM. The 2021
difference is that someone wrote down the prefix bet
and showed few-shot transfer with the LM locked.

If you only remember a picture, remember this one: a
column of language-model blocks that do not update,
and a vision network that must speak the LM's private
dialect. That picture is the next three years of open
VLM engineering, in drag.

---

**Stage:** draft. **Claim type:** public-record recap. This piece does
not propose a new method or a new research result.
