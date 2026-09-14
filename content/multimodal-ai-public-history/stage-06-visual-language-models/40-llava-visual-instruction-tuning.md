---
id: mmh-40
title: "LLaVA, 2023: visual instruction tuning goes public"
slug: llava-visual-instruction-tuning
series: multimodal-ai-public-history
stage: draft
status: staged
publish: false
novelty: public-record
era: "2023"
topics: [LLaVA, Liu, instruction-tuning, Vicuna]
voice_check: edited
voice_check_date: 2026-09-14
---

# LLaVA, 2023: visual instruction tuning goes public

Liu, Li, Wu, and Lee's *Visual Instruction Tuning*
(arXiv:2304.08485, 17 April 2023; NeurIPS 2023
Oral) is the open assistant paper. A CLIP vision
encoder. A linear projection. A Vicuna language
model. The contribution the title names is the
**data**: convert image-text pairs and COCO-style
boxes into instruction-following conversations,
using GPT-4 as a teacher of dialogue, then
finetune. The 17 April repository (`haotian-liu/
LLaVA`) put weights and code on the internet the
same week as the preprint.

This is not "the first VLM." It is the moment a
VLM looked like ChatGPT-with-a-photo to people
who could clone a repo. The paper's own related
work says so, citing Flamingo, BLIP-2, and
others. Credit the paper for what it did: a
reproducible recipe that treated **instruction
format** as the lever.

Why the lever worked, as a public story:

- Language-only instruction tuning was already
  a 2022–2023 fact (InstructGPT, Alpaca, Vicuna).
  LLaVA is that fact plus an image token.
- GPT-4 (text) as a data engine is a 2023
  special case. The teacher is a closed model.
  The student is open. That split is now common.
  It is also a dependency.
- A linear connector is almost an insult to
  Q-Former. Sometimes insults are correct. If
  the LM is strong and the instructions are
  right, the connector can be dumb.

LLaVA-1.5 (October 2023) and LLaVA-NeXT (January
2024 blog) are public sequels: better data,
higher resolution, different bases. I will not
turn them into a product line review. I will
say the name became a **family**, the way BERT
did. Families are historical. They attract
clones, benchmarks, and fatigue.

The demo failure modes were also public:
hallucinated objects, yes-man answers, OCR that
works until it does not. Those failures keep
this draft from becoming a launch post. An
assistant that speaks fluently about a picture
is a 2015 captioner with a chat template and a
better prior. The template is new. The
temptation to believe the fluency is old.

---

**Stage:** draft. **Claim type:** public-record recap. This piece does
not propose a new method or a new research result.
