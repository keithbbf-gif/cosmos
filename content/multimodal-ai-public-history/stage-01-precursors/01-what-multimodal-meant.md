---
id: "01"
slug: what-multimodal-meant
title: What “multimodal” meant before it was a product
stage: 01-precursors
stage_title: Precursors (before the 2021 hinge)
status: draft
voice: human
novelty_safe: true
public_record_only: true
primary_public_sources:
  - "Workshop and conference usage of 'multimodal' in vision–language literature, 2010s"
  - "Public product language after 2021 (vendor blogs, model cards)"
does_not_claim:
  - "a first-use etymology"
  - "that any lab coined the product sense"
last_reviewed: 2026-09-14
---

# What “multimodal” meant before it was a product

For a long time, multimodal was a workshop word. You said it when you had a paper that touched more than one stream — vision and language, audio and text, maybe IMU data if you were in robotics — and you needed a session title that would not lie. It did not sell. It classified. The opposite of multimodal was not “unimodal” in the marketing sense. The opposite was a clean ImageNet number.

I still hear the older meaning in older rooms. A person points at a slide with a photograph and a caption and says, carefully, that the *problem* is multimodal. They mean: the data does not come from one sensor, and if you pretend it does you will overfit a prior. Bananas are yellow. Questions that start with “how many” have small integer answers. The word was a warning.

Then the word moved.

After January 2021, and especially after the 2022 picture models, multimodal started to mean a *capability* a product could list. Text in, image out. Image in, text out. Later: speech in, and video in, and a camera pointed at a homework sheet. The warning collapsed into a feature. You can watch it happen in the language of blogs. “Connecting text and images.” “A visual language model.” “Natively multimodal.” None of that is false. It is a different job for the same adjective.

The shift matters because it hides a fork that the research already knew about.

One fork is **alignment**: force two modalities into a shared space so a sentence can retrieve a picture, or a picture can retrieve a sentence. CLIP is the public monument on that fork. The loss is contrastive. The output is not a paragraph. The output is a pair of vectors that know how to find each other.

The other fork is **generation**: condition one modality on another so a sentence can become a picture, or a picture can become a paragraph. DALL·E 1 sat on that fork the same week as CLIP, with a discrete codebook and a transformer. Diffusion sat on it a year later with a different physics. The vision–language assistants sat on a third, hybrid stool: generate *text* about *pixels*, which is captioning’s old job wearing a chat UI.

If you use “multimodal” the product way, those forks look like one story — the story of models that “understand” more than words. If you use it the workshop way, they are different bets about what the joint is for. Retrieval is a joint in space. Generation is a joint in time, token by token or step by step. Chat-about-an-image is a joint that has to talk back, which is a social demand the 2015 captioners did not have to meet.

I do not want to be precious about this. People are allowed to rename their furniture. But a public history that starts in 2021 without the older meaning will keep making the same mistake: treating every vision–language paper as an ancestor of the chatbot that looks. A lot of the important work was trying *not* to be a chatbot. CLIP does not speak. It scores. Flamingo can speak, and DeepMind presented it as few-shot, not as a product assistant. Those are different public objects.

There is a third, quieter meaning I still like. Multimodal as **a refusal to throw away the leftover channel**. A photograph is not a bag of ImageNet nouns. It has composition, light, the word someone typed under it, the word they did not type. Alt-text is a multimodal object even when it is a lie. A screenshot of a spreadsheet is multimodal in a way a cropped dog is not: the pixels *are* language. The product era discovered that last fact with great surprise, as if documents had not been images the whole time.

So when I say multimodal in the rest of this series, I will try to say which job I mean.

- Shared space, two towers, a score.
- Conditional generation, pixels or tokens, a sample.
- Conditioned language, an answer about an image.
- The leftover channel: metadata, alt-text, screenshots, speech sitting next to a frame.

If a draft slides into the product adjective, that is me getting lazy. Pull it back. The interesting history is not that models learned to “do multimodal.” It is that a handful of public joints — contrastive pairs, noisy latents, a frozen language model staring at a resampler — turned out to be enough to rearrange a decade of separate fields.

The next draft is about the field that made the old meaning look optional: ImageNet, and the last moment when a single labeled noun felt like the whole problem.
