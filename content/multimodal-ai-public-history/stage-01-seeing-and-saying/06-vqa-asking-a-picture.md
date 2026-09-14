---
id: mmh-06
title: "VQA, 2015: asking a picture a question"
slug: vqa-asking-a-picture
series: multimodal-ai-public-history
stage: draft
status: staged
publish: false
novelty: public-record
era: "2015-2017"
topics: [VQA, Antol, balanced-VQA, language-prior]
voice_check: edited
---

# VQA, 2015: asking a picture a question

Antol, Agrawal, Lu, Mitchell, Batra, Zitnick, and Parikh's *VQA: Visual
Question Answering* (ICCV 2015, arXiv:1505.00468) gave the field a
task that looked like intelligence and graded like a multiple-choice
exam. Show a photograph. Ask a free-form question. Demand an answer,
often a short one. "How many dogs?" "What color is the bus?" "Is it
raining?" The dataset, the challenge, and the later VQAv2 rebalance
are public objects. They ran workshops. They ran leaderboards. They
ran a thousand ablation tables.

The educational fact is not that neural nets can answer some of the
questions. The educational fact is that **language priors cheat**.
Early models learned that "how many" likes the answer "2" and that
"what sport" likes "tennis." Goyal and colleagues' 2017 balanced
dataset (VQAv2) was a public correction: for each question, pair two
images with different answers so a text-only model looks foolish.
That correction is part of the history of the task, not a footnote.

VQA pulled in a different crowd than captioning. Captioning is a
generation demo. VQA is an accuracy number. Accuracy numbers attract
architectures: bilinear pooling, stacked attention, relational nets,
bottom-up top-down. The 2016–2018 papers are a catalog of ways to
fuse a question vector with an image feature. Most of them are
obsolete as systems. They are not obsolete as **warnings**. Fusion
is a place where a paper can look busy and still be answering from
the question.

What VQA did for later multimodal work:

- It made **evaluation adversarial to the text prior**. CLIP's
  zero-shot classification and later VLM benchmarks inherit the
  suspicion. If your model can answer without looking, you have not
  measured looking.
- It licensed **open-endedness** while still being gradable. That
  compromise — free-form questions, short answers, ten human
  annotators — is why VQA survived as a number people quote.
- It created a **public vocabulary of failure**: counting, negation,
  reading text in the image, uncommon objects. GPT-4V's 2023 system
  card will still talk about some of these. The failures were named
  when the models were LSTMs.

A reader should not confuse a VQA score with "the model understands
the picture." Understanding is not an item on the annotation
interface. The interface asks for an answer string. The history is
the interface, the cheat, the rebalance, and the stubborn remainder
that still needs vision.

---

**Stage:** draft. **Claim type:** public-record recap. This piece does
not propose a new method or a new research result.
