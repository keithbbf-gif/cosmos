---
id: mmh-13
title: "OSCAR and VinVL: object tags as extra words"
slug: oscar-vinvl-object-tags
series: multimodal-ai-public-history
stage: draft
status: staged
publish: false
novelty: public-record
era: "2020-2021"
topics: [OSCAR, VinVL, Li, Zhang, object-tags]
voice_check: edited
---

# OSCAR and VinVL: object tags as extra words

Li, Yin, Li, Hu, Zhang, Zhang, Wang, Hu, Dong, Wei, et al.'s *OSCAR*
(ECCV 2020, arXiv:2004.06165) makes a blunt public bet: if you already
paid for a detector, **type the detected names into the transformer**.
The input is not only region features and caption tokens. It is also
the word *dog* when the detector said dog. Alignment, the paper
argues, gets easier when the two modalities share a surface string.

VinVL (Zhang, Li, Hu, Wang, Hu, Wei, et al., 2021) is the follow-up
that treats the detector as the thing to improve. Better boxes, better
tags, better downstream tables. The initials are a joke — Visual
features in Vision-Language — and a claim: the 2019 BERT pile-up
underinvested in the visual encoder. That claim is ordinary engineering
sense. It is also a high-water mark for the detector-as-tokenizer
era.

Read these papers as the last fully committed version of a story:

1. Detect objects with a supervised detector.
2. Treat features (and now tags) as the visual language.
3. Pretrain a transformer on image-text pairs plus the tags.
4. Finetune on VQA, retrieval, captioning, and the rest of the 2020
   menu.

It works. The tables are public. The code and some checkpoints were
public. Students reproduced the stack. And then CLIP, trained without
this stack, started winning the *zero-shot* conversations that OSCAR
was not designed to have. OSCAR is a finetune-and-transfer system.
CLIP is a retrieve-and-prompt system. They can both be right about
different exams.

A fair reading does not dump on tags. Tags are a form of **lossy
captioning produced by a specialist model**. They help when the
human caption forgot the object. They hurt when the detector is
wrong, or when the meaning is not an object (a mood, a diagram, a
line of text). VinVL cannot tag "the joke in the meme." Later
OCR-aware VLMs will have to read. Tagging is not reading.

I leave OSCAR and VinVL on the timeline so that "we ground in
objects" does not sound like a 2024 invention. Grounding, as a
public pretraining trick, was already a concatenation. The later
grounding models (Grounding DINO, and the referring-expression
literature before it) are a different, more spatial claim. Do not
smash them together. Concatenating the word *dog* is not the same
as pointing at the dog.

---

**Stage:** draft. **Claim type:** public-record recap. This piece does
not propose a new method or a new research result.
