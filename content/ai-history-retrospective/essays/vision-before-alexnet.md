---
voice_check: human
title: "Before the 2012 cliff: blocks, filters, and small datasets"
slug: vision-before-alexnet
kind: essay
era: 1966–2011
tags: [vision, fukushima, lecun, summer-vision, hog]
portrait: assets/portraits/kunihiko-fukushima.placeholder.svg
portrait_status: placeholder
---

The famous joke is that someone at MIT handed a student a camera and a summer. The document is less cute. Seymour Papert’s Vision Memo No. 100, “The Summer Vision Project,” dated 7 July 1966 (MIT AI Group / Project MAC), assigns figure-ground analysis, region description, and object identification to a group of summer workers. Gerald Sussman is named as coordinator of the vision-project meetings, not as a lone intern given an impossible homework. The underestimation is still real. 1966 did not have a theory of how much work vision is. It had a vidisector, a memo, and a list of names.

![Labeled placeholder for Kunihiko Fukushima — not a photograph.](../assets/portraits/kunihiko-fukushima.placeholder.svg)

*No redistributable likeness with a clear license was available at staging. This panel is not a photograph.*

## Blocks, line drawings, and a laboratory aesthetic

The MIT and Stanford of the late 1960s treated vision as a prelude to robotics: find the edges of a stack of cubes, then move a manipulator. David Marr’s later book *Vision* (1982) tried to impose levels — computational theory, representation and algorithm, implementation — on a field that had been writing edge detectors and hoping. Marr died in 1980; the book is posthumous in the way that matters. It became a syllabus.

## A Japanese hierarchy

Kunihiko Fukushima’s neocognitron, in *Biological Cybernetics* in 1980, is a hierarchical network with simple and complex cells in a lineage from Hubel and Wiesel. It is shift-tolerant pattern recognition, described without the 2012 GPU romance. English-language histories that start vision at AlexNet are skipping a documented object.

Yann LeCun’s convolutional nets in the late 1980s and 1990s, and the 1998 LeNet-5 paper, took a related hierarchy into gradient descent and into a postal and banking economy. That is applied vision, not a summer memo.

Japanese industrial machine vision — factory inspection, semiconductor lines — ran in parallel with the academic named-feature years and did not always publish in CVPR. English-language retrospectives that treat 2005–2011 as “HOG versus SIFT” are describing a conference, not every camera on a line.

## Features you could name

The 2000s lived on named descriptors: SIFT (Lowe, 1999/2004), HOG (Dalal and Triggs, 2005), bag-of-words models, PASCAL VOC contests. You could draw the feature. You could argue about the feature. Error rates moved in small, honest increments. Caltech-101 and then Caltech-256 were the small worlds. ImageNet, proposed in 2009, was the attempt to make the world larger than a poster.

When AlexNet arrived in 2012, it did not erase this decade. It made many of its named features look like a lot of work for a smaller payoff. Researchers who had built careers on those features had to decide whether to climb the new cliff or to keep a craft. Both decisions are in the literature. Only one of them became a keynote style.
