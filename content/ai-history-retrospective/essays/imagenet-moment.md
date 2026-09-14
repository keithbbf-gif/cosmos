---
voice_check: human
title: "A database, a contest, and a 2012 drop in the error rate"
slug: imagenet-moment
kind: essay
era: 2009–2015
tags: [imagenet, alexnet, fei-fei-li, hinton, convnets]
portrait: assets/portraits/fei-fei-li.jpg
portrait_status: sourced
---

ImageNet was, first, a paper at CVPR in 2009: Jia Deng, Wei Dong, Richard Socher, Li-Jia Li, Kai Li, and Li Fei-Fei. A hierarchical image database, WordNet as scaffolding, millions of labeled photographs gathered with a scale of crowdsourcing that earlier vision datasets had not attempted. The scientific claim was not “we have solved vision.” It was “we have made a yardstick that will hurt.”

![Fei-Fei Li at the ITU AI for Good meeting, 2017.](../assets/portraits/fei-fei-li.jpg)

*Credit: ITU Pictures. CC BY 2.0. File:Fei-Fei Li at AI for Good 2017.jpg.*

## ILSVRC

The ImageNet Large Scale Visual Recognition Challenge ran through the 2010s and became a calendar. Teams published numbers. The numbers were about classification and later detection, on a 1,000-class subset that entered hallway speech as “ImageNet” even when the full database was larger.

In 2012, Alex Krizhevsky, Ilya Sutskever, and Geoffrey Hinton entered a deep convolutional network — later nicknamed AlexNet — and cut the top-5 error rate by a margin that made other groups rewrite their summer plans. The NIPS 2012 paper is short, empirical, and frank about GPUs and dropout. It does not philosophize. It did not need to.

## What was old

Convolutional nets were not invented in 2012. Fukushima’s 1980 neocognitron, LeCun’s 1980s–1990s digit work, and the 1998 LeNet-5 paper are the prior art. GPUs were not invented for this contest. What changed was the meeting of a large labeled set, enough compute, and a group willing to train a model that looked, to 2011 eyes, slightly insane in its depth and its parameter count.

Hinton’s Toronto group had been arguing for deep nets through a winter of support vectors. The 2012 result is their receipt.

## What the moment licensed

After 2012, “deep learning” escaped the NIPS hallway and entered product groups: photo search, medical-image pilots, advertising. It also licensed a new kind of dataset politics. ImageNet’s images came from the web. People in the photographs had not sat for a scientific portrait. Later criticism — of labels, of categories, of consent — belongs to the public record of the late 2010s. Fei-Fei Li has discussed those costs in subsequent talks and interviews. The 2009 paper remains what it was: a bet that scale of supervision would move a field that had been stuck on Caltech-101 and PASCAL-sized worlds.

A yardstick that hurts is still a yardstick. The next yardsticks — GLUE, SuperGLUE, MMLU, the various “chat” leaderboards — inherited ImageNet’s social form: a number, a ranking, a press cycle. Whether the number measures the thing you care about is a question the 2012 party did not close.
