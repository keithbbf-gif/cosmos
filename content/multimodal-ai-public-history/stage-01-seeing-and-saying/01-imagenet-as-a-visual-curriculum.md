---
id: mmh-01
title: "ImageNet as a visual curriculum, not a multimodal paper"
slug: imagenet-as-a-visual-curriculum
series: multimodal-ai-public-history
stage: draft
status: staged
publish: false
novelty: public-record
era: "2009-2012"
topics: [ImageNet, Deng, Li-Fei-Fei, curriculum]
voice_check: edited
voice_check_date: 2026-09-14
---

# ImageNet as a visual curriculum, not a multimodal paper

A history of vision-language models that starts at CLIP is a history
that has already skipped the school. ImageNet is not a multimodal
dataset. It is a labeled photograph collection organized on WordNet
synsets, announced by Deng, Dong, Socher, Li, Li, and Fei-Fei in 2009
and then run as an annual challenge. The public fact that matters here
is not a number on a leaderboard. It is that a whole field agreed, for
about a decade, on what "seeing" looked like when you wanted a grade.

WordNet is already a language object. That is easy to forget. The
folders have names. The names are English lexical concepts. A
researcher who trained a classifier on ImageNet was, in a thin sense,
already aligning pixels with words. The alignment was a lookup table:
this crop is *n02123045*, and *n02123045* is a tabby cat. There was no
sentence. There was no caption. There was a closed list.

Closed lists are a kind of honesty. They tell you what the system
refuses to see. If your photograph is a feeling, a joke, or a
relationship between two people, ImageNet has no class for it. Later
multimodal papers will brag about open vocabularies. They are bragging
against this curriculum. You cannot hear the brag if you do not know
the school.

The ILSVRC years also trained a *public*. Newspaper charts, workshop
talks, and the 2012 Krizhevsky-Sutskever-Hinton result taught
non-specialists that vision had a contest and that the contest could
move. Multimodal work inherits that public. When a 2021 CLIP paper
says it matches a ResNet-50 on ImageNet without using the 1.28 million
training labels, the sentence only works because ImageNet is still the
shared yardstick. Transfer is a story you tell about a familiar exam.

I will not pretend ImageNet is innocent. Later writing on the dataset
— from the original collection papers through the 2019–2020 audits of
labels, faces, and harmful categories — is also public. A curriculum
can be revised. The revision does not erase the years when the field
treated the exam as the world.

If you are reading this set for CLIP and diffusion, keep ImageNet on
the table as **infrastructure**. It is the classification default.
Captioning will try to talk. Visual question answering will try to
interrogate. Contrastive image-text models will try to throw the label
set away. All three moves are replies. Replies need an addressee.

---

**Stage:** draft. **Claim type:** public-record recap. This piece does
not propose a new method or a new research result.
