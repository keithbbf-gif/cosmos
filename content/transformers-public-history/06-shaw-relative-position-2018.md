---
id: tph-06
slug: shaw-relative-position-2018
title: "Relative position representations (6 March 2018)"
status: staged-draft
series: transformers-public-history
era: 2018-fork
first_public: "2018-03-06"
date_kind: arxiv-v1
arxiv: "1803.02155"
venue_later: "NAACL 2018"
novelty_lane: public-prior-art-only
private_systems: excluded
depends_on: ["tph-04"]
leads_to: ["tph-16", "tph-30"]
---

# Relative position representations (6 March 2018)

**Status:** staged draft. Not a publication.
**Lane:** public transformer architecture history.
**First public appearance:** 6 March 2018 (`arxiv-v1`).
**Primary source:** Shaw, Uszkoreit, Vaswani, *Self-Attention with Relative Position
Representations*, arXiv:1803.02155.

## The claim

Nine months after the 2017 paper, three of its authors (plus Shaw) published the first widely
cited **relative** position scheme for this architecture. Instead of adding a vector that
depends only on absolute index \(i\), they let the compatibility score and the value
aggregation depend on the **clipped offset** \(j - i\). Absolute position is no longer the only
order channel.

This is the first public admission, from inside the same author set, that §3.5's absolute
encodings were a starting point rather than a settled design.

## What the artifact specified

Shaw et al. add two learned embeddings per clipped distance, \(a_{ij}^K\) and \(a_{ij}^V\), and
fold them into the attention logits and the value mix. Distances beyond a threshold \(k\) share
embeddings, so the parameter count is \(O(k)\) rather than \(O(n)\). The 2017 sinusoidal basis
is not required.

The paper evaluates on WMT English-to-German and shows consistent gains over the absolute
baseline at comparable size. It is a translation paper, not a long-context paper. It does not
claim a 32k window and does not propose interpolation.

Two later relative families should not be collapsed into this one:

- **T5** (23 October 2019) uses a **scalar relative bias** \(b_{j-i}\) added to the logits, with
  logarithmic bucketing of long distances, and drops the \(1/\sqrt{d_k}\) scale. That is a
  simpler relative move than Shaw's vector-valued \(a^K, a^V\).
- **RoPE** (20 April 2021) does not add a bias vector at all. It rotates \(Q\) and \(K\) so the
  dot product depends on \(j - i\). Different mechanism, later date.

## What it displaced

The unspoken assumption that "add a PE to the embedding and forget it" was enough. After Shaw,
position becomes a **per-attention-edge** object. That is conceptually closer to how later
decode-time caches have to think (every new query against every past key has an offset) than
the 2017 additive PE is.

It did not displace absolute embeddings in the 2018–2019 pretrained-encoder wave. BERT, GPT-1,
GPT-2, and RoBERTa all shipped learned absolute positions. Relative representations won first
in encoder–decoder and then, via RoPE, in decoder-only LLMs. The adoption lag is part of the
history: the idea is 2018, the default in open decoder-only models is 2021–2023.

## Immediate lineage

Transformer-XL (9 January 2019) combines segment-level recurrence with a relative encoding
descended from this line (Shaw plus a later relative-bias formulation). T5's bias is the
production-simple descendant. Music Transformer (Huang et al., 2018) also sits on relative
attention and is out of scope here except as evidence that the idea traveled off WMT quickly.

A reader dating "relative position = RoPE = 2021" erases three years of public work.

## What this draft does not claim

It does not claim Shaw embeddings extrapolate. Clipping at \(k\) is an explicit non-extrapolation
device: far offsets share a bucket. It does not claim T5 "is Shaw." It does not treat any
closed model's unpublished position channel as Shaw-like.

The NAACL 2018 venue year must not replace 6 March 2018.

## Sources

- Shaw, Uszkoreit, Vaswani, arXiv:1803.02155, published 2018-03-06 (`arxiv-v1`).
- Vaswani et al., arXiv:1706.03762, §3.5, published 2017-06-12 (`arxiv-v1`).
- Raffel et al., arXiv:1910.10683, published 2019-10-23 (`arxiv-v1`).
- Dai et al., *Transformer-XL*, arXiv:1901.02860, published 2019-01-09 (`arxiv-v1`).

## Draft debt

- Quote Shaw's exact \(k\) default and the WMT BLEU delta from the PDF.
- Add Music Transformer as a dated off-ramp if a multimodal-early pack opens.
