---
id: mmh-09
title: "Bottom-up top-down, 2018: objects as the caption's vocabulary"
slug: bottom-up-top-down
series: multimodal-ai-public-history
stage: draft
status: staged
publish: false
novelty: public-record
era: "2018"
topics: [Anderson, Faster-R-CNN, BUTD, COCO]
voice_check: edited
voice_check_date: 2026-09-14
---

# Bottom-up top-down, 2018: objects as the caption's vocabulary

Anderson, He, Buehler, Teney, Johnson, Gould, and Zhang's *Bottom-Up
and Top-Down Attention for Image Captioning and Visual Question
Answering* (CVPR 2018, arXiv:1707.07998) is the paper that made
Faster R-CNN features a multimodal default. Instead of attending over
a convolutional grid, the model attends over **detected objects**.
Each object is a pooled feature plus a class. The language decoder
does top-down attention over that set. On the 2017 COCO captioning
leaderboard the combination was hard to ignore. For two or three
years, if you built a VQA model, someone asked whether you had used
"bottom-up features."

The public artifact was not only the paper. Anderson and colleagues
released extracted features. Other labs trained on those files
without rerunning detection. That is scholarship as a tarball. It
also froze a detector. When your language model can only see the
objects a 2017 detector proposed, your errors inherit that proposal.
A missed box is a missed word. A spurious box is a hallucination
with a confidence score.

Why this is a hinge, not a curiosity:

- It **aligns the unit of vision with the unit of language**. Words
  often name objects. Boxes name objects. The 2018 paper makes that
  folk theory into an architecture.
- It **sets up OSCAR and VinVL**. Those later pretrained models
  concatenate object tags with captions. They are unthinkable without
  a detector good enough to be treated as a tokenizer.
- It **ages the moment CLIP arrives**. CLIP embeds the whole image
  (or a crop) against a sentence. No box required. The 2021 paper
  does not need to win a fight with Anderson et al. in public; the
  field simply starts doing fewer two-stage pipelines for retrieval
  and zero-shot classification. Detection does not die. It moves to
  grounding and SAM-adjacent work.

A reader should hold both thoughts. Object-centric features were a
real gain on 2018 captioning and VQA numbers. They were also a
commitment to a visual vocabulary that looks like a detector's
class list. Open-vocabulary models will later try to escape that
list. They will still, in 2023–2024, come back to boxes when the
user asks "which one." The 2018 paper is the moment the field said,
out loud, that **looking at objects is not the same as looking at a
grid**.

---

**Stage:** draft. **Claim type:** public-record recap. This piece does
not propose a new method or a new research result.
