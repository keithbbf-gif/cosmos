---
id: "tph-12"
slug: "sparse-transformer-2019"
title: "Sparse Transformer: fixed sparse patterns (23 April 2019)"
status: "staged-draft"
series: "transformers-public-history"
era: "2019-refine"
first_public: "2019-04-23"
date_kind: "arxiv-v1"
arxiv: "1904.10509"
venue_later: ""
novelty_lane: "public-prior-art-only"
private_systems: "excluded"
depends_on: ["tph-02"]
leads_to: ["tph-20", "tph-48"]
---

# Sparse Transformer: fixed sparse patterns (23 April 2019)

**Status:** staged draft. Not a publication.
**Lane:** public transformer architecture history.
**First public appearance:** 23 April 2019 (`arxiv-v1`).
**Primary source:** Child, Gray, Radford, Sutskever, *Generating Long Sequences with Sparse
Transformers*, arXiv:1904.10509.

## The claim

If the 2017 primitive's bill is the \(n \times n\) matrix, one honest response is to **not
compute most of the matrix**, using a hand-designed sparsity pattern that still lets
information travel across the sequence in a small number of layers. The Sparse Transformer is
the first widely cited public paper that does this for deep generative Transformers, with
strided and fixed patterns aimed at very long sequences (including images treated as
token sequences).

This is 23 April 2019 — before Reformer, Longformer, and BigBird. "Sparse attention" as a
family starts here in this pack, not in 2025's Native Sparse Attention, and not in Mistral's
2023 window.

## What the artifact specified

Two pattern families, described in the paper with diagrams:

- **Strided** sparsity: a head attends locally and then every \(k\)-th position, so a token
  reaches far away in \(O(1)\) or \(O(\log n)\) hops depending on stacking.
- **Fixed** sparsity: a subset of positions act as global hubs.

They also discuss mixing heads with different patterns. The rest of the paper is an engineering
stack for training these models on long sequences (recomputed attention, mixed precision, and
related tricks). Those tricks are easy to over-credit; the architecture event is the **mask**.

They generate long images, text, and audio sequences and report likelihoods. Author-reported
2019 density-modeling numbers; not a 2026 LLM eval.

## What it displaced

The assumption that a Transformer either attends densely or is not a Transformer. After this
paper, a mask is a design parameter. That sounds small. It is the license for Longformer's
window, BigBird's random+global+window, and every later "this head is local, that head is
global" production config.

## Immediate lineage

Longformer (10 April 2020) makes sliding window plus a few global tokens the default for
*documents*. BigBird (28 July 2020) adds random connections and a proof-flavored claim about
universal approximation / Turing completeness under sparsity. Routing Transformer and
Reformer's LSH are *content-based* sparsity, a different family (who you attend to depends on
the vectors, not only on index). Keep those families separate.

2025 Native Sparse Attention and DeepSeek Sparse Attention are learned / hardware-aligned
descendants, not this paper's fixed pattern, and they get later cards.

## What this draft does not claim

It does not claim the 2019 patterns are compute-optimal on 2024 GPUs. FlashAttention made dense
exact attention much cheaper in 2022; several sparse schemes then had to beat a faster dense
baseline. It does not claim any closed lab's unpublished mask is a Sparse Transformer.

## Sources

- Child, Gray, Radford, Sutskever, arXiv:1904.10509, published 2019-04-23 (`arxiv-v1`).
- Beltagy, Peters, Cohan, arXiv:2004.05150, published 2020-04-10 (`arxiv-v1`).
- Zaheer et al., arXiv:2007.14062, published 2020-07-28 (`arxiv-v1`).

## Draft debt

- Reproduce the paper's pattern diagrams in words more tightly against Figure 3.
- Add Routing Transformer as a dated content-based sparse sibling if the sequel pack opens.
