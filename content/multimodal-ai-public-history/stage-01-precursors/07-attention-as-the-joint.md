---
id: "07"
slug: attention-as-the-joint
title: Attention as the joint
stage: 01-precursors
stage_title: Precursors (before the 2021 hinge)
status: draft
voice: human
novelty_safe: true
public_record_only: true
primary_public_sources:
  - "Bahdanau, Cho, Bengio, neural machine translation attention, 2014/2015"
  - "Xu et al., Show, Attend and Tell, 2015"
  - "Vaswani et al., Attention Is All You Need, NeurIPS 2017"
  - "Dosovitskiy et al., ViT, ICLR 2021 (arXiv 2020)"
does_not_claim:
  - "a first-to-invent claim for attention"
  - "that transformers 'caused' multimodal AI by themselves"
last_reviewed: 2026-09-14
---

# Attention as the joint

Before attention was a brand, it was a way for a decoder to look back. Bahdanau, Cho, and Bengio needed a translation model that did not crush a whole sentence into one vector and hope. So the decoder, at each word, took a weighted glance at the encoder states. Soft weights. A little heatmap over the source. The joint, in that paper, is between two *languages*. The trick does not care.

Vision–language people borrowed it immediately, because they already had two streams. Show, Attend and Tell is the popular public moment: the LSTM, while saying *frisbee*, is invited to put weight on the blur in the air. Cross-attention is a joint you can draw. That mattered more than we admitted. A lot of science communication is drawing.

2017 changes the weather. Vaswani et al. throw out the recurrence and keep the glance. Everything is attention. Queries, keys, values. A sequence talks to itself; two sequences talk to each other with the same algebra. Once you have that algebra, a “modality” is just a way of making a token. A wordpiece is a token. A spectrogram patch can be a token. An image patch can be a token. The joint is no longer a special fusion module you name in the title. The joint is the layer.

I want to keep a lid on the mysticism. Attention is not understanding. It is a routing trick with a softmax. It can route to the right patch. It can route to a prior. It can route to a watermark in the corner because watermarks correlate with a website that uses the word *beautiful*. The 2015 captioners already knew the heatmap could lie. The transformer era made the heatmap bigger and called it a backbone.

The important historical fact is **fungibility**. After 2017, labs that were good at language could look at vision and see a sequencing problem. Labs that were good at vision could look at language and see a stack they no longer had to be afraid of. That is social, not just technical. Multimodal groups in 2018 still had to justify why they were sharing a meeting. Multimodal groups in 2021 could say “it’s all transformers” and get the room to nod, too fast.

Vision as a sequence takes an extra beat. A convolutional net is not born tokenized. You can attend over its feature map — that is the 2015 move. Or you can cut the image into patches, embed the patches, and *be* a transformer. Dosovitskiy et al.’s ViT, public as a preprint in 2020 and as ICLR 2021, is the clean version of that dare: if you have enough data, the inductive bias of convolution is optional. CLIP’s public image towers include both a ResNet family and a ViT family. That sentence is a period at the end of a fight. The fight was about whether images were special. The draw was “special until scale.”

Cross-attention will keep showing up, so I want the public versions named:

- **Decoder attends to image features** while writing words. Captioning, then Flamingo’s gated xattn, then a lot of “frozen LLM plus visual tokens” papers.
- **UNet attends to text features** while denoising. Latent diffusion’s conditioning, the sentence as a key/value the picture can query.
- **Two towers, no cross-attention at inference**, only a dot product. CLIP. Cheap. The joint happened in training.

Those are three different public objects that all get called multimodal attention if you are sloppy. I will try not to be sloppy. CLIP’s joint is a loss. Diffusion’s joint is a condition inside a generator. Flamingo’s joint is a stack of glances inside a frozen speaker.

A personal prejudice, labeled as such: I trust the cheap joint more than the pretty one. A dot product that retrieves the right picture is a fact I can check. A cross-attention map that lights up a dog is a story I want footnotes for. Both belong in the history. Only one of them shipped as a nightly habit for people who were not in the field.

Next draft: the rhyme that made the nod in the room possible — BERT and ViT, same block, different tokens — and why unification-as-engineering is not the same as unification-as-philosophy.
