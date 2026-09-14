---
id: "tph-25"
slug: "vision-transformer-2020"
title: "Vision Transformer: 16×16 patches as tokens (22 October 2020)"
status: "staged-draft"
series: "transformers-public-history"
era: "2020-long-scale"
first_public: "2020-10-22"
date_kind: "arxiv-v1"
arxiv: "2010.11929"
venue_later: "ICLR 2021"
novelty_lane: "public-prior-art-only"
private_systems: "excluded"
depends_on: ["tph-08", "tph-09"]
leads_to: ["tph-26", "tph-29"]
---

# Vision Transformer: 16×16 patches as tokens (22 October 2020)

**Status:** staged draft. Not a publication.
**Lane:** public transformer architecture history.
**First public appearance:** 22 October 2020 (`arxiv-v1`).
**Primary source:** Dosovitskiy, Beyer, Kolesnikov, Weissenborn, Zhai, Unterthiner, Dehghani,
Minderer, Heigold, Gelly, Uszkoreit, Houlsby, *An Image is Worth 16x16 Words: Transformers
for Image Recognition at Scale*, arXiv:2010.11929.

## The claim

ViT is the moment the 2017 **encoder** leaves language without a convolution backbone.
An image is cut into patches (the type-case is \(16 \times 16\)), each patch is linearly
projected to \(d_{\mathrm{model}}\), a `[CLS]` token and **learned 2D-aware position
embeddings** are added, and a BERT-like encoder classifies. The paper's bet is that at
sufficient pre-train scale, this beats or matches ResNets without the spatial inductive
bias people assumed was mandatory.

ICLR 2021 is the venue. The public date is 22 October 2020.

## What the artifact specified

ViT-Base / Large / Huge configurations (layer counts and widths in the paper's table),
patch sizes 14 or 16 in the headline experiments, hybrid variants that still use a CNN
stem (the paper is honest that hybrids help at smaller scales). Position embeddings are
learned; they interpolate them when fine-tuning at higher resolution — a vision-specific
relative of the 2023 language "position interpolation" story, and **not** RoPE.

Pre-training is on large image-labeled sets (ImageNet-21k, JFT-300M in the paper). That
data dependence is part of the architecture claim: the block is simple; the scale is not.

## What it displaced

The assumption that ImageNet-class recognition required conv nets (or at least a conv
stem). It did not displace conv nets in all of vision; it opened a second default. Swin
(25 March 2021) puts hierarchy and shifted windows back in, because a plain ViT is
expensive on dense prediction.

## Immediate lineage

DeiT (data-efficient training), BEiT / MAE (self-supervised ViTs), CLIP's image tower
(often a ViT), DETR's encoder side, and DiT (diffusion transformer, 19 December 2022).
When a 2024 "multimodal LLM" says "vision encoder," it is often this block or a Swin/ViT
cousin, plus a projector.

## What this draft does not claim

It does not claim ViT was the first attention-for-images paper (there are 2019–2020
predecessors). It claims ViT is the type-case that made patch-as-token the default. It
does not treat unpublished visual frontends of closed chat models as ViT unless a report
says so.

## Sources

- Dosovitskiy et al., arXiv:2010.11929, published 2020-10-22 (`arxiv-v1`).
- Liu et al., *Swin Transformer*, arXiv:2103.14030, published 2021-03-25 (`arxiv-v1`).
- Radford et al., *CLIP*, arXiv:2103.00020, published 2021-02-26 (`arxiv-v1`).

## Draft debt

- Quote ViT-B/16 vs ViT-L/16 parameter counts from Table 1.
