---
voice_check: human
title: "MMMU: a college exam with diagrams"
slug: mmmu
kind: explainer
era: 2024
tags: [mmmu, multimodal, yue]
portrait: null
portrait_status: none
---

Xiang Yue, Yuansheng Ni, Kai Zhang, Tianyu Zheng, Ruoqi Liu, Ge Zhang, Samuel Stevens, Dongfu Jiang, Weiming Ren, Yuxuan Sun, Cong Wei, Botao Yu, Ruibin Yuan, Renliang Sun, Ming Yin, Boyuan Zheng, Zhenzhu Yang, Yibo Liu, Wenhao Huang, Huan Sun, Yu Su, and Wenhu Chen published “MMMU: A Massive Multi-discipline Multimodal Understanding and Reasoning Benchmark for Expert AGI” at CVPR 2024. The file is a college-level exam that refuses to drop the figures: charts, chemical structures, maps, scores, diagrams that a text-only model cannot honestly see.

<!-- figure-pack -->
<figure>
  <img src="../assets/diagrams/multimodal-exam.svg" alt="MMMU multimodal college exam schematic with images and multiple-choice answers" width="720" height="400" loading="lazy" decoding="async" />
  <figcaption><strong>MMMU (Yue et al., CVPR 2024).</strong> College-level multimodal questions where figures are required—multiple-choice scoring like MMLU with vision attached.</figcaption>
</figure>


The title’s “expert AGI” is a mouthful. The instrument is more modest and more useful: can a multimodal model do the kind of question a human student meets when the answer is in the image and the caption together?

## What an item is

A question from a college subject — the paper’s subject list is broad, from art history to clinical medicine to engineering — plus one or more images. Answers are multiple choice or a short expression, depending on the item. The scorer is closer to MMLU than to a captioning metric. The vision is not a decoration. If you cover the figure, the question should break.

That last sentence is the quality bar the authors tried to enforce. Some items in any multimodal pile still leak into text. A good card reports a text-only ablation. If the score barely drops when the image is removed, you were not running MMMU. You were running a caption exam.

## Why it is not VQAv2

VQAv2 (Goyal et al., CVPR 2017) is everyday photographs and short answers, with a famous unanswerable/balanced design against language priors. ChartQA, DocVQA, TextVQA, MathVista — each later file took a slice (charts, documents, scene text, math figures). MMMU’s bet is breadth-plus-difficulty: many disciplines, college hardness, one noun.

MathVista (Lu et al., ICLR 2024) is the closer cousin for figures-and-math. If your claim is mathematical visual reasoning, say MathVista. If your claim is multi-discipline college multimodal, say MMMU. If your claim is “the model can see,” you need more than one file.

## An item in the hand

A chemistry question with a skeletal formula. An art-history question with a painting and a demand that you use what is on the canvas, not only the famous title in the prompt. A medical item with a scan or a chart. Cover the image: the stem should become unfair. If it stays fair, the figure was a poster.

College difficulty means the distractors are not “banana” versus “mitochondria.” They are the near-miss a student writes on a midterm. A vision model that can caption “a graph going up” and cannot read the axis units will look fluent and be wrong. That is the failure MMMU is allowed to catch.

Wenhu Chen’s group also sits on MMLU-Pro. The through-line is exam-shaped measurement with a harder curve. Here the curve includes pixels.

## The AGI adjective

CVPR titles are allowed to reach. This series is not. MMMU does not measure whether a system is a general colleague. It measures whether a system can sit a particular kind of illustrated exam. Treat the acronym as the dataset. Leave the prophecy in the paper’s title.

## How it ages

Images in exam problems leak less casually than pure text, but they leak: papers, blogs, the dataset itself. As models climb, the next sequel will add harder figures or hide the options. Until then, MMMU is the default multimodal college noun, the way MMLU was the default text college noun.

Protocol matters: resolution, how many images you actually feed, whether you describe the figure in text first (a cheat that can also be a legitimate accessibility tool). Name the pipeline.

## How to read an MMMU line

Subject breakdown, multiple-choice versus open, text-only ablation, and the model’s vision encoder identity. A number without the ablation is a rumor about seeing.

Yue and Chen’s group put the diagram back on the exam. That is the whole request. If your system cannot use the diagram, it should not get the college credit. The scorer is willing to be that strict. The card should be too.
