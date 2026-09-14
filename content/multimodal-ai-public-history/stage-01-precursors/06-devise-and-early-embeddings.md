---
id: "06"
slug: devise-and-early-embeddings
title: DeViSE and the unglamorous ancestor
stage: 01-precursors
stage_title: Precursors (before the 2021 hinge)
status: draft
voice: human
novelty_safe: true
public_record_only: true
primary_public_sources:
  - "Frome et al., DeViSE: A Deep Visual-Semantic Embedding Model, NeurIPS 2013"
  - "Norouzi et al., ConsVSM / related zero-shot embedding work (public 2010s line)"
  - "Weston, Bengio, Usunier, WSABIE (earlier ranking embeddings)"
does_not_claim:
  - "that DeViSE is the sole ancestor of CLIP"
  - "unpublished Google training details beyond the paper"
last_reviewed: 2026-09-14
---

# DeViSE and the unglamorous ancestor

DeViSE is not a pretty paper in the 2022 sense. There are no astronauts. There is a deep visual-semantic embedding, a skip-gram language model, a ConvNet, and a ranking loss that tries to make an image land near the right word vector and away from the wrong ones. It is 2013. The authors are at Google. The point, said plainly, is to replace a closed softmax with a space you can generalize in.

I like starting here because it ruins a lazy origin story. CLIP did not invent the joint space. CLIP did not invent the idea that text could supervise vision. What CLIP did in public was take a related instinct — pull matched pairs together, push the batch of mismatches apart — and run it at a scale and with a text encoder that made the space *useful for everything*. DeViSE’s space was useful for a table about zero-shot and few-shot recognition. That is a different kind of useful. Both are real.

Read DeViSE with 2021 eyes and you can see the missing pieces like missing teeth.

The text side is **words**, mostly, not captions. A class name is a thin sentence. “Golden retriever” does not contain “wet from the lake, tennis ball in mouth.” CLIP’s text tower gets those extra words for free, because the web wrote them. DeViSE has to hope the skip-gram geometry already clustered *retriever* near *dog* near *puppy*. Sometimes it did. Sometimes *jaguar* the car sat too close to *jaguar* the cat, and the image encoder had to live with that.

The image side is a **ConvNet of that year**, trained the usual way, then mapped. The visual features still came from a classification world. The embedding was a translation layer. CLIP trains the image encoder *for the joint*, at least in the public description: the visual tower’s job is to be findable by text, not to win ILSVRC as a primary goal. That change in job description is easy to skip and fatal to skip.

The loss is already in the ranking family. Push the right pair up. That family includes older work (WSABIE and the Weston–Bengio line) that treated annotation as retrieval. Contrastive learning at CLIP’s batch size is a descendant, not a stranger. I will not flatten the math; the public papers do not all use the same InfoNCE spelling. The family resemblance is the point.

Why did this not feel like a phase change in 2013? Scale, cleanliness, and interface. The public could not type “a photo of a golden retriever in the style of a faded Polaroid” and get a retrieval trick that doubled as a classifier. There was no prompt template culture. There was no OpenCLIP. There was a paper, a talk, a zero-shot number that looked good for 2013, and then the field went back to softmaxes because softmaxes won contests.

That last sentence is not an insult. Contests pay. Embeddings, in 2013, paid in a different currency: the hope that a new class would not require a new head. The industry needed a decade of language-model weather, a decade of ConvNet then ViT weather, and a web full of alt-text before that hope became a default.

There is a lineage chart I refuse to draw with arrows that look like destiny. WSABIE and metric learning. DeViSE and ConsVSM. VirTex and ICMLM and ConVIRT, which the CLIP paper itself cites as nearer neighbors — language as supervision, sometimes contrastive, sometimes generative. CLIP is explicit about debts in a way later product blogs are not. A public history should be at least as polite as the paper.

What I take from DeViSE as a person, not as a citation engine: the unglamorous papers are where the *job* appears. The job is “stop treating nouns as a closed panel of buttons.” Everything after is instrumentation. If you only read the 2021 blogs, you will think the job was invented by a lab that also made a picture generator the same day. The job is older. The lab was the first to make the job feel like weather.

Next I want the mechanism that made two modalities able to point at each other inside a model, not just inside a loss: attention, and the moment vision became a sequence.
