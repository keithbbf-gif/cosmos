---
id: mmh-15
title: "CLIP, 2021: predicting which caption goes with which image"
slug: clip-the-matching-game
series: multimodal-ai-public-history
stage: draft
status: staged
publish: false
novelty: public-record
era: "2021"
topics: [CLIP, Radford, contrastive, zero-shot]
voice_check: edited
---

# CLIP, 2021: predicting which caption goes with which image

Radford, Kim, Hallacy, Ramesh, Goh, Agarwal, Sastry, Askell,
Mishkin, Clark, Krueger, and Sutskever's *Learning Transferable
Visual Models From Natural Language Supervision* (ICML 2021,
arXiv:2103.00020) is the paper this folder is partly for. The
pretraining task is the sentence the authors keep repeating:
predict which caption goes with which image. Four hundred million
pairs. An image encoder. A text encoder. A similarity matrix. The
loss is symmetric cross-entropy. After training, you classify by
embedding class names as sentences and taking the nearest one.

OpenAI's blog post is dated 5 January 2021. The arXiv stamp is
26 February 2021. The ICML proceedings sit in PMLR 139. Those are
three public objects. Use the blog for the demo tone, the paper
for the recipe and the limits, the proceedings for the archival
cite. Do not collapse them into "CLIP launched one day."

What was actually new, as a public package:

- **Scale plus simplicity.** Matching is not new (see ViLBERT,
  ConVIRT in medicine, earlier embedding work). Doing it from
  scratch on a web-scale pair set, with both towers trained, and
  then *releasing* image encoders, was new as a fact you could
  download.
- **Zero-shot as the headline exam.** The paper benchmarks more
  than thirty existing vision datasets without dataset-specific
  training. The ImageNet zero-shot ResNet-50 match is the sentence
  that traveled.
- **Prompting as a vision trick.** "A photo of a {label}" is a
  public hyperparameter. Later papers will ensemble prompts. The
  2021 paper already knows the wording matters.

What was not new, and what the paper does not need to be:

- Transformers (the image tower has a ViT variant).
- Contrastive batches (the vision 2020 papers).
- The idea that text supervises vision (DeViSE, captions, 2019
  matching losses).

The paper's section on broader impacts is part of the public
record, not an appendix you skip to be kind. CLIP inherits the
crawl. It can be probed for denigration and for surprising OCR.
It is a retrieval system with a moral weather. Later drafts in
stage 08 will come back to that weather without pretending the
2021 authors did not mention it.

If you read only one technical claim, read this: after CLIP, a
vision model can be **addressed in English**. That is a different
interface from a 1000-way softmax. Diffusion models will type
English into a frozen CLIP text tower. Visual-language assistants
will still, often, start from a CLIP-like encoder. The matching
game became plumbing.

---

**Stage:** draft. **Claim type:** public-record recap. This piece does
not propose a new method or a new research result.
