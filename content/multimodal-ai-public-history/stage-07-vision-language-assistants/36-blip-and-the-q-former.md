---
id: "36"
slug: blip-and-the-q-former
title: BLIP, BLIP-2, and the Q-Former
stage: 07-vision-language-assistants
stage_title: Vision–language assistants
status: draft
voice: human
novelty_safe: true
public_record_only: true
primary_public_sources:
  - "Li et al., BLIP, 2022"
  - "Li et al., BLIP-2, 2023"
  - "Salesforce / public model cards and code"
does_not_claim:
  - "that Q-Former is the only correct glue"
  - "unpublished caption-cleaning pipelines beyond the papers"
last_reviewed: 2026-09-14
---

# BLIP, BLIP-2, and the Q-Former

Not every lab had a frozen 70B and a desire to keep it frozen. Some labs had the old captioning job, a CLIP-like encoder, and a need to make web data less filthy before they taught a model to speak.

**BLIP** (Li et al., 2022) is, in public, a bootstrapping story. Web image–text pairs are noisy. So you use a model to *caption* and to *filter*, and you grow a cleaner supervision, and you train a model that can both understand and generate language about images. Contrastive, matching, generating — more than one loss in one body. I will not recap every head. I will recap the instinct: **do not trust the alt-text; rewrite it.** That instinct is the opposite of ALIGN’s “scale will wash the dirt.” It is a 2015 captioner’s instinct at 2022 scale. Both instincts published numbers. Both can be true in different rooms.

**BLIP-2** (2023) is the glue paper a lot of open work actually cited. Frozen image encoder. Frozen LLM. In the middle, a **Q-Former**: a small transformer that learns a fixed set of query tokens, attends to the image features, and produces a short sequence the language model can eat. Train the middle (in stages, in the paper’s recipe). Do not pay to train the giants again.

You can hear Flamingo in this. You can also hear a budget meeting. The Q-Former is a Perceiver-resampler cousin with a BERT-like accent: queries that ask the image what the language model will need. Whether those queries learn anything interpretable I leave to later interpretability papers. Historically, they learned a **shape people could reimplement**.

Why BLIP-2 mattered in City B: it gave a route to “LLM + pictures” that was not “wait for a lab.” You could pick a publicly available frozen LLM (within license pain), pick a frozen CLIP or EVA or whatever your GPU could hold, train the sandwich, and get something that answered questions about images. The answers were often mediocre and sometimes startling. Mediocre-and-sometimes-startling is how open assistants begin.

I want a care with the word *understand*. BLIP’s generation head writes captions. BLIP-2’s LLM writes more fluent answers. Fluency is not a VQA v2 complementary pair. The banana is still yellow. The Q-Former can learn to pass the LLM what the LLM needs to sound right. That may or may not be what is in the picture. The 2015–2017 scars apply without mercy.

A smaller public gift of the BLIP line: **a culture of released checkpoints for captioning and retrieval**, not only for pretty pictures. Before 2022, if you wanted a decent captioner you trained one. After, you downloaded one, then complained about it, then fine-tuned it. That is infrastructure. Infrastructure is how LLaVA’s later weekend becomes possible — not because LLaVA is BLIP (it isn’t), but because the field had accepted “frozen visual tower + trainable glue + language model” as a default diagram.

InstructBLIP and the instruction-tuning cousins sit on this diagram and add the 2023 spice: not just captions, but *orders*. “Write a recipe.” “Explain the meme.” I will let draft 38 take the instruction-data story, because LLaVA made that story loud. BLIP-2 is the sandwich. Instruction is the filling that made the sandwich a product.

If you are mapping joints:

| Object | Joint |
| --- | --- |
| CLIP | Contrastive space, no speaker |
| Flamingo | Gated xattn into a frozen speaker, resampler |
| BLIP-2 | Q-Former queries, frozen speaker |
| LLaVA (next-next) | Linear (or MLP) map, speaker often not frozen |

The map is the literature. Everything else is branding.

Next: two Google-adjacent public objects that pull the map in different directions — PaLI, which scales the *vision* encoder like it is the point, and PaLM-E, which puts pixels into a robot paper and a language model at once.
