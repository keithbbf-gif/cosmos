---
id: mmh-38
title: "Flamingo, 2022: few-shot visual language, paper not weights"
slug: flamingo-few-shot-paper
series: multimodal-ai-public-history
stage: draft
status: staged
publish: false
novelty: public-record
era: "2022"
topics: [Flamingo, Alayrac, DeepMind, Perceiver]
voice_check: edited
---

# Flamingo, 2022: few-shot visual language, paper not weights

Alayrac, Donahue, Luc, Miech, Barr, Hasson, Lenc,
Mensch, Millican, Reynolds, et al.'s *Flamingo*
(arXiv:2204.14198, 29 April 2022; NeurIPS 2022) is
the paper later LLaVA writing will call a GPT-3
moment for vision-language. A frozen vision encoder.
A Perceiver Resampler that turns a variable number of
visual features into a fixed token set. A frozen LM
with newly inserted **gated cross-attention** layers
that can attend to those tokens. Training on
interleaved image-text corpora, not only single
pairs. The headline: one model, many image and video
tasks, few-shot, by prompting.

Weights were not a hobbyist download. That split
again: generous method, closed file. OpenFlamingo
and IDEFICS will be the public replies. This draft
is the letter they were answering.

What Flamingo added that Frozen did not:

- **Interleaving as a first-class input.** A
  document can be text, image, text, image. That
  is closer to a web page or a slideshow than a
  COCO pair.
- **A resampler.** The LM does not have to eat
  every patch. A perceiver compresses. Compression
  is a method (see VQGAN) now sitting in front of
  an LM.
- **Gated xattn.** New layers, carefully initialized
  so the frozen LM does not explode, can be trained
  on multimodal data while the original weights
  stay a language model.

The evaluation style matters. Flamingo reports
few-shot numbers on captioning, VQA, OK-VQA,
video tasks. It invites comparison to finetuned
specialists. Sometimes it wins with 16 examples
what another model won with thousands of
finetune labels. That sentence is the 2022 brag.
It is also a research protocol, not a product
review.

I will not reconstruct DeepMind's interleaved
corpus from the paper's sketches. The paper
describes sources at a high level. High level is
what outsiders have. Honesty is staying there.

If CLIP made images addressable in English,
Flamingo made **English able to continue after
an image**, in context, as a published system
diagram. The open 2023 assistants are that
diagram with different connectors and a chat
template.

---

**Stage:** draft. **Claim type:** public-record recap. This piece does
not propose a new method or a new research result.
