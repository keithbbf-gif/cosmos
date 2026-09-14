---
id: mmh-50
title: "Public evals: the rulers that ran the field"
slug: public-evals-rulers
series: multimodal-ai-public-history
stage: draft
status: staged
publish: false
novelty: public-record
era: "2014-2025"
topics: [COCO, VQAv2, MMBench, MMMU, GenEval]
voice_check: edited
---

# Public evals: the rulers that ran the field

A multimodal history that only names models is
a catalog. The field was steered by **exams**.
This draft is a map of the public ones, not a
meta-benchmark.

**Generation of sentences.** COCO captions
(Lin et al., 2014) plus BLEU, METEOR, CIDEr,
SPICE. The 2015–2019 captioning literature
is almost unreadable without those acronyms.
They measure overlap with reference
committees. They do not measure whether the
sentence is kind, or useful, or true about
a rare object.

**Answers.** VQA and VQAv2, OK-VQA, GQA,
TextVQA, ScienceQA. Each name is a complaint
about the last exam: too much language prior,
not enough knowledge, not enough composition,
not enough reading, not enough school
science. Complaints becoming datasets is
how the field works.

**Retrieval.** Flickr30k and COCO retrieval
for the 2019 BERT pile-up. Later, CLIP-style
zero-shot classification as a retrieval
against class sentences. ImageNet is still
in the room, as draft 01 said.

**Assistants.** MMBench, MME, SEED-Bench,
MM-Vet, MMMU (Yue et al., 2024) — the 2023–
2024 attempt to grade a chatty VLM the way
MMLU graded a chatty LM. MMMU's college-
subject framing is a public choice about
what "hard" means. It is not the only
choice.

**Image generation.** FID and CLIP-score,
DrawBench, PartiPrompts, T2I-CompBench,
GenEval. Human preference (Pick-a-Pic,
ImageReward, later arena-style votes) tried
to rescue the field from metrics that a
CFG slider can game. The rescue is
incomplete. It is still better than a
mood.

How to read a table in this literature:

- If the training data overlaps the exam,
  the number is a rumor.
- If the metric is CLIP and the model is
  guided by CLIP, the number is a rhyme.
- If the paper only reports the exams it
  wins, you are being sold.

I include this draft so later editors can
hang new exams on a hook without rewriting
the model chapters. Rulers change. The
habit of being ruled does not. A public
history of multimodal AI is, as much as
anything, a history of what the field
agreed to be scored on in public.

---

**Stage:** draft. **Claim type:** public-record recap. This piece does
not propose a new method or a new research result.
