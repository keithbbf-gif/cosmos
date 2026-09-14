---
title: Two GTX 580s in a bedroom
dek: The ImageNet paper says five to six days, two consumer cards, 3 GB each. The rest is a culture that needed a number.
slug: 12-two-gtx-580s-alexnet
series: AI Compute Chip Magazine
status: staged
kind: standalone-article
scope: public-history
novelty: public-record-only
exclusions: [no-cosmos, no-patents, no-unpublished-claims]
---

# Two GTX 580s in a bedroom

The paper is eight pages and it does not waste them. “Our network takes between five and six days to train on two GTX 580 3GB GPUs.” That is Alex Krizhevsky, Ilya Sutskever, and Geoffrey Hinton, 2012, ImageNet classification with a deep convolutional network. The cards are consumer Fermi-generation GeForce parts. The time is a work week. The dataset is ILSVRC’s 1.2 million labeled images. The error rate that mattered in the contest, after they averaged models, was 15.3 percent top-5 against a second place at 26.2. Computer vision as a field changed its mind in public.

The Computer History Museum later released the original source and said the training happened on a computer with two NVIDIA cards in Krizhevsky’s bedroom at his parents’ house. Hinton, talking to the museum, summarized the division of labor with a line that is already too famous and still accurate enough: Ilya thought they should do it, Alex made it work. The museum’s write-up also notes the precursor, cuda-convnet, trained on CIFAR-10, and Dan Cireşan’s earlier GPU convnets that won smaller contests. AlexNet is not the first convolutional net on a GPU. It is the one that hit a dataset the field already respected and won by a humiliating margin.

Read the paper for the hardware constraint, not only for ReLU and dropout. The authors say the network’s size is limited mainly by GPU memory and by the training time they will tolerate. They split the net across two cards. They wrote their own 2D convolution. They tell you, in the last sentence of that paragraph, that the results should improve if you wait for faster GPUs and bigger datasets. That is a procurement forecast disguised as a conclusion. The industry took it literally.

Why two cards? Because one 3 GB GTX 580 could not hold the thing they wanted to run. Model parallelism, in this paper, is not a slogan. It is a way to fit. The GPUs communicate at certain layers and otherwise keep their own pieces. Anyone who has later trained on eight H100s with a megatron-style split is in a direct line from that necessity, even if the software is unrecognizable.

CUDA is present the way electricity is present. The paper does not pause to thank a platform. It assumes a highly optimized GPU implementation is a thing a graduate student can write. That assumption is the 2006–2012 story landing. A student could buy two gaming cards, speak CUDA, and outrun institutional vision systems that had spent a decade on hand-built features. The unfairness is the point. Platforms are unfair on purpose.

There is a tidy myth that says “AlexNet invented deep learning.” The paper does not say that. Neural nets were old. Convnets were old. ImageNet was new enough and large enough. GPUs were newly programmable enough. The combination is the event. CHM’s commentary is right to say each needed the other. A magazine piece should keep the combination, not pick a favorite parent.

Another myth: it had to be NVIDIA. In 2012, if you wanted a documented path from C to a fast conv on a card you could buy at a shop, CUDA was the path a Toronto student actually used. That is a historical fact, not a law of nature. The law-of-nature version is later marketing.

If you want a physical object, a GTX 580 with the 3 GB tag on the box is enough. Two of them in a desktop that still has a dusty 600-watt power supply is better. The bedroom is not a gimmick. It is a reminder that the most important training run of the decade did not require a national lab. It required a platform that had already leaked into consumer SKUs, and a person willing to keep the machine on for six days.

The afterlife of the paper is an industry. This article stops at the week of training and the contest number. Those are the facts that do not need a sequel to be complete.

## Sources

- Krizhevsky, Sutskever, Hinton, “ImageNet Classification with Deep Convolutional Neural Networks,” NeurIPS 2012.
- Computer History Museum, AlexNet source release and accompanying essay (bedroom training; cuda-convnet precursor; Hinton quotation).
- ILSVRC-2012 public contest record: 15.3% top-5 (winning entry) vs. 26.2% second place, as reported in the paper.
