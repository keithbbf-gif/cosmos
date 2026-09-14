---
id: mmh-02
title: "AlexNet, 2012: a unimodal shock that multimodal work still spends"
slug: alexnet-unimodal-shock
series: multimodal-ai-public-history
stage: draft
status: staged
publish: false
novelty: public-record
era: "2012"
topics: [AlexNet, Krizhevsky, GPU, ImageNet]
voice_check: edited
voice_check_date: 2026-09-14
---

# AlexNet, 2012: a unimodal shock that multimodal work still spends

Krizhevsky, Sutskever, and Hinton's 2012 ImageNet paper is not a
vision-language paper. It has no caption decoder. It has no contrastive
text tower. It has a convolutional net, data augmentation, dropout, and
two GPUs. The reason it belongs in this set is inheritance. After 2012,
"a visual model" in public English meant a deep net you could finetune.
Every later multimodal paper that freezes a vision encoder is spending
that inheritance.

The shock was empirical and social. The ILSVRC-2012 top-5 error dropped
in a way the workshop audience could feel. The code and the talk
traveled. Within a few years the default backbone for detection,
segmentation, and then captioning was a descendant of this object: a
stack of convolutions pretrained on ImageNet classification. Show and
Tell will plug such a stack into an LSTM. Bottom-up attention will
replace the stack's last pooling with Faster R-CNN boxes. CLIP will
later ask whether you still need the classification pretraining at all.
That question is only interesting because the pretraining worked.

Two public lessons, neither of them romantic.

First: **compute became a character**. The 2012 paper is frank about
GPUs. Later diffusion and image-text papers will be frank about
hundreds of millions of pairs and thousands of accelerator-days. The
genre of "we could not have done this on a CPU lab" starts here, in
vision, before it becomes a language-model cliché.

Second: **features became a commodity**. Once a pretrained
convolutional net could be downloaded or reimplemented, vision-language
researchers stopped inventing a new visual front-end for every paper.
They argued about the *interface*: do you pool a grid, detect objects,
or embed the whole image next to a sentence? The 2012 shock is why
those arguments are about interfaces rather than about whether deep
features exist.

A caution, because this set is trying not to make myths. AlexNet did
not "solve vision." It won a classification contest and moved a
default. Plenty of 2013–2016 vision still failed at composition,
counting, and anything off the ImageNet prior. Multimodal papers that
treat 2012 as year zero of intelligence are doing advertising.
Multimodal papers that treat 2012 as the start of a reusable visual
encoder are doing history.

If you only remember one sentence: the first multimodal systems of the
2010s did not learn to see from captions. They borrowed a seer that
had already been graded on a closed list of nouns.

---

**Stage:** draft. **Claim type:** public-record recap. This piece does
not propose a new method or a new research result.
