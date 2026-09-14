---
id: "02"
slug: imagenet-as-unimodal-peak
title: ImageNet as the last unimodal peak
stage: 01-precursors
stage_title: Precursors (before the 2021 hinge)
status: draft
voice: human
novelty_safe: true
public_record_only: true
primary_public_sources:
  - "Deng et al., ImageNet, CVPR 2009"
  - "Krizhevsky, Sutskever, Hinton, NeurIPS 2012 (AlexNet)"
  - "Russakovsky et al., ImageNet Large Scale Visual Recognition Challenge, 2015"
  - "Radford et al., CLIP paper / OpenAI CLIP blog, 2021 (zero-shot ImageNet claim)"
does_not_claim:
  - "that ImageNet 'caused' CLIP"
  - "unpublished labeler methods"
last_reviewed: 2026-09-14
---

# ImageNet as the last unimodal peak

ImageNet is the reason a lot of us learned to talk about vision as a classification problem with a celebrity number. The dataset is public history: a WordNet-shaped catalog, more than a million training images in the ILSVRC slice people actually fought over, a yearly contest, and then a 2012 paper that made a convolutional net look like common sense.

I am not going to retell AlexNet as origin myth. That story is tired and mostly true. What I want is the *shape* ImageNet gave the field, because CLIP later used that shape as a foil.

The shape is this: an image has one right noun, or a small set of them, from a closed list. A model is good if it names the noun. The photograph is a vehicle for the noun. Everything that is not the noun — the caption someone might have written, the joke in the background, the fact that this dog is a meme and that dog is a breed standard — is noise you hope the crop removed.

That was a brilliantly useful lie. It made supervised learning scale in public. It made errors comparable. It made a graduate student in 2014 able to say “I got 8%” and be understood in another country. It also trained a generation to treat language as a *labeling interface*, not as a modality. Words sat outside the model, in the annotation tool.

You can feel the exhaustion in the later ImageNet years. Top-5 became a solved-looking number. People moved the goalposts to object detection, segmentation, video, robustness. The closed list started to look like a room the models had memorized the furniture of. Adversarial examples made the furniture look painted on. Domain shift made it look like a showroom.

CLIP’s public boast — matching a ResNet-50 on ImageNet *without using the 1.28 million labeled ImageNet training examples* — only lands if you still believe ImageNet is the exam. That is why they chose it. It is the exam the field already agreed to. Zero-shot ImageNet is a joke told in the old dialect to announce a new one: the supervision was sentences all along, just not these sentences, and not this closed list.

I do not read that as ImageNet failing. I read it as ImageNet completing its job. It proved that scale plus a clean label could move a field. Then it sat there as a monument that later work had to *step around*. If you fine-tune on ImageNet, you inherit the closed list. If you only ever test on ImageNet, you inherit the lie that a noun is a seeing.

There is a human detail in the ImageNet story that the CLIP story repeats in a different key. ImageNet’s nouns were gathered and cleaned by people. The public papers talk about WordNet, queries, crowdsourcing, quality control. CLIP’s public materials talk about 400 million image–text pairs collected from the internet. The labor moved. It did not disappear. It became whoever typed an alt-text, a filename, a page title, a Reddit title, a stock-photo caption. ImageNet hid that labor in a label file. The web hid it in the page.

Unimodal, then, is a slightly unfair word for ImageNet. The dataset was always language-shaped. WordNet is language. The synsets are language. The annotator instructions are language. What was unimodal was the *training signal the model was allowed to see*: pixels in, class index out. The words were boiled off.

That boiling is the peak. After it, the interesting public work puts the words back in, mess and all. Some of that work is captioning, which tried to emit the words. Some is VQA, which tried to answer with them. Some is embedding work, which tried to park the words next to the picture. CLIP is the embedding fork at industrial noisy scale. Diffusion-plus-text is the generation fork. The assistant that looks is the captioning fork after language models got large enough to sound like they were in the room.

If you want a single ImageNet hangover that still matters: closed-set accuracy is a terrible way to notice that a model has never seen a concept. The web-scale pairs do not solve that. They relocate it. There are still concepts that barely appear, or appear only as slurs, or appear only as advertising. ImageNet’s 1000 classes were a known poverty. The web’s vocabulary is an unknown one.

I keep ImageNet in this series so we do not start in 2021 like the previous decade was a hallway. It was a summit. People planted a flag. Then they looked down and realized the interesting country was the unlabeled slope — which had labels after all, just not ones a synset committee had approved.
