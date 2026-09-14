---
id: "04"
slug: show-and-tell-and-the-caption
title: Show and Tell, and the caption as a finished-looking problem
stage: 01-precursors
stage_title: Precursors (before the 2021 hinge)
status: draft
voice: human
novelty_safe: true
public_record_only: true
primary_public_sources:
  - "Vinyals et al., Show and Tell, CVPR 2015 / PAMI follow-on"
  - "Xu et al., Show, Attend and Tell, ICML 2015"
  - "Karpathy and Fei-Fei, Deep Visual-Semantic Alignments, CVPR 2015"
  - "COCO / Flickr captioning benchmarks (public leaderboards)"
does_not_claim:
  - "that any one paper 'solved' captioning"
  - "unpublished decoder tricks"
last_reviewed: 2026-09-14
---

# Show and Tell, and the caption as a finished-looking problem

2015 was a good year to believe image captioning was about to become furniture. You had Show and Tell: a ConvNet encoder, an LSTM decoder, a sentence coming out the end that a civilian could read. You had Show, Attend and Tell: the same idea with a spotlight that walked across the picture as the words arrived. You had Karpathy’s alignments, which made the joint look almost pedagogical — this word, that region. COCO gave everyone a shared exam. BLEU, METEOR, CIDEr, later SPICE. The tables filled up.

I remember the screenshots more than the scores. A bird on a branch. A man on a snowboard. A pizza on a table. The sentences were short, grammatical, slightly bored. They sounded like a person who had been asked to describe a stock photo and wanted to go home. That was the tell, if you were listening. The models had learned the *genre* of a dataset caption.

A dataset caption is a particular literary form. It names the salient objects. It sometimes names a relation (*on*, *holding*, *next to*). It almost never names a mood, a brand, a political context, or a joke. It prefers “a group of people” to a proper noun. It is what you write when you are paid by the image and the instructions say be objective. Training on that form produces fluency in that form. It does not produce seeing.

The field knew this faster than the press did. Captioning papers started to talk about hallucination — objects in the sentence that were not in the picture. They talked about genericness. They talked about the way metrics reward n-gram overlap with reference captions, which means a safe sentence can beat a true one. Attention maps were pretty and not always faithful; later work would show that you can scramble the attention and keep a lot of the score. None of that is a scandal. It is what happens when you optimize a proxy.

Why put this in a multimodal history? Because captioning is the first time a lot of people watched a model *speak about a picture* and felt the future lean in. It is also the first time the public joint was a language model. The decoder was not a 1000-way softmax. It was a sequence. That sequence was small and brittle and trained on a polite corpus, but the shape is the shape that Flamingo and LLaVA and GPT-4V will wear in nicer clothes. Pixels become a prefix. Words become a continuation.

The other fork — retrieval, CLIP — is in some ways a *refusal* of this 2015 object. CLIP does not have to emit “a pizza on a table.” It has to know that the string “a pizza on a table” scores higher than “a snowboard.” That is a lighter demand and, at web scale, a more robust one. Generation of text about images stayed hard after generation of images about text got easy. That asymmetry is one of the jokes of the decade. We got oil-painting astronauts before we got trustworthy alt-text.

Show, Attend and Tell deserves a separate nod because it made the joint *visible*. You could watch the model look at the yellow of a banana while saying *yellow*. Civilians loved that. Researchers learned, slowly, that a heatmap is not an explanation. I still like the paper. It taught a generation to think of captioning as alignment in time: each word is a bet about where to look. That is a multimodal idea even when the implementation is a shallow attention over conv features.

Karpathy’s alignment work did a related public service. It treated the caption not as a blob but as a set of fragments that should attach to regions. That is closer to how a person reads a picture with a sentence in hand. It is also closer to how later grounding papers will talk, and how people will prompt image generators with extra parentheses around the words they care about. The instinct — bind this token to that patch — keeps coming back.

What 2015 did not give us was scale of supervision. COCO is large if you are a 2015 captioner. It is a rounding error if you are a 2021 contrastive model. The sentences are clean. The pictures are licensed and boxed. The joint is polite. CLIP’s joint is rude: alt-text, page titles, the SEO sentence someone wrote to sell a lamp. Diffusion’s joint is ruder still, because the sentence becomes a steering wheel for a generative process that can invent a lamp that was never for sale.

I do not treat Show and Tell as a cute antique. I treat it as the first time the public saw a neural net write a sentence that seemed to look. The seeming was the product. The looking was the open problem. The rest of this series is what happened when people stopped trusting the seeming, and then, in 2022, started selling it again with better lighting.
