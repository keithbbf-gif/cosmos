---
id: "tph-52"
slug: "perceiver-2021"
title: "Perceiver: cross-attend into a latent bottleneck (4 March 2021)"
status: "staged-draft"
series: "transformers-public-history"
era: "2021-position-adapt"
first_public: "2021-03-04"
date_kind: "arxiv-v1"
arxiv: "2103.03206"
venue_later: "ICML 2021"
novelty_lane: "public-prior-art-only"
private_systems: "excluded"
voice_check: "edited"
voice_check_date: "2026-09-14"
depends_on: ["tph-26", "tph-02"]
leads_to: ["tph-38"]
---

# Perceiver: cross-attend into a latent bottleneck (4 March 2021)

**Status:** staged draft. Not a publication.
**Lane:** public transformer architecture history.
**First public appearance:** 4 March 2021 (`arxiv-v1`).
**Primary source:** Jaegle, Gimeno, Brock, Vinyals, Zisserman, Carreira, *Perceiver: General
Perception with Iterative Attention*, arXiv:2103.03206.

## The claim

Perceiver attacks the \(n \times n\) bill by **not doing self-attention on the raw input**.
A small set of latent vectors repeatedly **cross-attends** to a byte/pixel/audio array of
length \(n\), then self-attends among themselves. Cost is \(O(n \cdot m + m^2)\) with
\(m \ll n\). The 2017 primitive is still there; the *sequence it is applied to* is a
learned bottleneck.

This is a different escape hatch from Linformer (project length) and from Performer
(approximate softmax). It is closer in spirit to DETR's object queries (`tph-26`) pointed
at *perception in general*.

Perceiver IO (2021, later paper) adds a flexible output query interface. Perceiver AR
(15 February 2022, arXiv:2202.07765) is the auto-regressive cousin. Do not date those at
4 March 2021.

## What the artifact specified

Latent array size \(m\), iterative cross-attend + self-attend blocks, no modality-specific
conv stem required in the type-case (they show pixels, audio, point clouds, and multimodal
concatenations). Position encodings still appear because the latent still needs to know
*where* in the byte array a feature came from.

Flamingo's visual resampler (29 April 2022) is a production-famous descendant of "cross-
attend the picture into a few tokens." That is a lineage sentence, not a claim that
Flamingo *is* Perceiver.

## What it displaced

The idea that a Transformer for images had to self-attend every patch at full \(n\) (ViT's
default). Perceiver says you can pay \(n\) only on the *cross-attend* side. ViT still won
the "simple and scalable" branding; Perceiver won a slot in the efficient-attention family
tree.

## Immediate lineage

Perceiver IO, Perceiver AR, Flamingo resampler, and various "Q-Former" / BLIP-2 bottleneck
modules (2023). Those later modules are often smaller and trained with a different
objective; they share the **latent query** idea.

## What this draft does not claim

It does not claim Perceivers retired ViTs. They did not. It does not treat unpublished
visual tokenizers in closed chat models as Perceivers.

## Sources

- Jaegle et al., arXiv:2103.03206, published 2021-03-04 (`arxiv-v1`).
- Carion et al., arXiv:2005.12872, published 2020-05-26 (`arxiv-v1`).
- Alayrac et al., arXiv:2204.14198, published 2022-04-29 (`arxiv-v1`).

## Draft debt

- Quote default \(m\) and iteration counts from the paper.
