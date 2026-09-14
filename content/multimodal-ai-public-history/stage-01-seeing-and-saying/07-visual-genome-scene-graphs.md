---
id: mmh-07
title: "Visual Genome: the expensive graph under the sentence"
slug: visual-genome-scene-graphs
series: multimodal-ai-public-history
stage: draft
status: staged
publish: false
novelty: public-record
era: "2016-2017"
topics: [Visual-Genome, Krishna, scene-graph, regions]
voice_check: edited
---

# Visual Genome: the expensive graph under the sentence

Krishna, Zhu, Groth, Johnson, Hata, Kravitz, Chen, Kalantidis,
Shamma, Bernstein, and Fei-Fei's *Visual Genome* (IJCV 2017;
arXiv:1602.07332) is what happens when a lab decides that a caption
is too thin. The public release attaches, to each image, region
descriptions, objects, attributes, relationships, and question-answer
pairs. The sales pitch in 2016–2017 was a **scene graph**: not "a man
on a horse," but a man node, a horse node, and an *on* edge, with
boxes.

This is multimodal supervision at annotation prices. You can feel the
prices in the paper. Crowdsourcing, quality control, WordNet linking,
the decision to reuse COCO and YFCC images so the new labels sit on
familiar photographs. The dataset became plumbing. Object detectors
were pretrained on it. Relationship models were scored on it. Later
OSCAR and VinVL papers will treat detected tags as extra tokens. Those
tags have a genealogy, and Visual Genome is a named parent.

Why a general reader should care, even if they will never train a
scene-graph parser:

- It is a **public admission that sentences underspecify**. A caption
  can be true and still leave out the cup, the brand, the left-right
  fact. Genome tried to write the underspecified parts down.
- It is a **bridge between detection and language**. Boxes plus names
  plus relations are already a little language. Models that "talk
  about objects" in 2018–2021 are often talking about this style of
  annotation.
- It is a **limit case of human labeling**. You cannot scene-graph the
  web. CLIP's later bet — take the alt-text you already have — is, in
  part, a refusal of this expense. Both bets are public. They are
  different economies.

The graphs themselves aged. Many edges are generic (*wearing*, *on*,
*has*). Annotators disagree. A scene graph is not a meaning of the
image; it is a meaning a crowd would type under time pressure. Later
work on scene-graph generation spent years chasing recall of those
edges. That literature is real. It is also a reminder that a
representation can become a benchmark and then a rut.

I keep Visual Genome on this timeline as **the last great structured
caption**. After 2021 the field's gravity moves to noisy image-text
pairs and then to instruction data. Structured supervision does not
vanish — detection, grounding, and SAM-style masks are still
structure — but the default multimodal story stops being "build a
better graph." The default becomes "align to whatever text came with
the file."

---

**Stage:** draft. **Claim type:** public-record recap. This piece does
not propose a new method or a new research result.
