---
id: "32"
slug: dreambooth-and-textual-inversion
title: DreamBooth and textual inversion
stage: 06-control-and-personalization
stage_title: Control and personalization
status: draft
voice: human
novelty_safe: true
public_record_only: true
primary_public_sources:
  - "Ruiz et al., DreamBooth, 2022"
  - "Gal et al., An Image is Worth One Word (textual inversion), 2022"
  - "Public community implementations on Stable Diffusion checkpoints"
does_not_claim:
  - "unpublished regularization tricks beyond the papers"
  - "that personalization is only these two methods"
last_reviewed: 2026-09-14
---

# DreamBooth and textual inversion

Once the checkpoint was a file, the next hunger was obvious. People did not only want *a* dog. They wanted *their* dog. A handful of photographs. A new noun. The 2022 papers that named the hunger in academic dialect are textual inversion (Gal et al.) and DreamBooth (Ruiz et al.). The hunger itself is older than both. It is what a portrait is.

**Textual inversion** is the smaller spell. You keep the model weights still. You learn a new **token embedding** — a word that did not exist — whose job is to stand for the thing in the pictures. “An image is worth one word,” the title says, and the word is a vector in the text encoder’s table. At prompt time you write that word (or a placeholder like `<sks-dog>`) and the cross-attention has a new key to listen to. The model was not really retrained. The vocabulary grew by one.

**DreamBooth** is the larger spell. You fine-tune the generative model so that a rare token (`sks` is the meme) plus a class word (`dog`) reconstructs your subject in new settings. The paper talks about class-specific prior preservation: generate some generic dogs while you train, so the model does not forget what *dog* means while it learns *your* dog. That sentence is the technical kindness. Without it, personalization is amnesia with a cute output.

I want the difference to stay sharp because the culture smeared them. Both give you a handle on a subject. One is a word. One is a weight change. The word is small and portable and sometimes weak. The weight change is stronger and heavier and, on a popular checkpoint, became a file you could share. Sharing a DreamBooth of a *person* is a different social object than sharing a DreamBooth of a chair. The papers are about subjects. The internet is about faces.

Why this is multimodal history, not only “fine-tuning”:

Because the handle is still a **word**. Even DreamBooth, which touches the UNet, is invoked by a prompt. The joint remains language-shaped. You have not given the model a mesh of your dog. You have given it a name. Names are leaky. They collide. They pick up a style you did not mean. They fail when the ten photos were all the same kitchen.

The ten-photo constraint is the human part. A person can stand in a room and take ten pictures. That is a dataset size a family can produce. ImageNet cannot be a family. WIT cannot be a family. Personalization is the first time the web-scale pair diet meets a *private* pair diet. The ethics flip: now the consent problem is not only “was this alt-text written for training.” It is “did this face agree to be a token that strangers can prompt into a bikini.” City B had no good answer. City A had filters and a terms-of-service. Both leaked.

I will not write a how-to. The papers are public; the repos are public; this draft is a history of the *job*. The job is: **bind a new concept to a linguistic handle with few examples.** That job will reappear in LoRA (next), in IP-Adapters, in “image prompt” products, in every later system that says “teach it your brand.” The 2022 papers are the moment the job got names a citation can hold.

A reading, labeled: textual inversion is the more theoretically honest of the two, because it admits that what you wanted was a word. DreamBooth is the more practically honest, because a word in a frozen table often cannot carry a specific face. Together they are a fork about **where a concept lives** — in the vocabulary, or in the generative spine. Vision–language people had been arguing a version of this since DeViSE. 2022 made the argument something you could see on a kitchen table.

Next: the file that made the weight change small enough to become a community object — LoRA — which did not start as an image paper at all.
