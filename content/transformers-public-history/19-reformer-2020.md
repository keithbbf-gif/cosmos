---
id: "tph-19"
slug: "reformer-2020"
title: "Reformer: LSH attention and reversible stacks (13 January 2020)"
status: "staged-draft"
series: "transformers-public-history"
era: "2020-long-scale"
first_public: "2020-01-13"
date_kind: "arxiv-v1"
arxiv: "2001.04451"
venue_later: "ICLR 2020"
novelty_lane: "public-prior-art-only"
private_systems: "excluded"
voice_check: "edited"
voice_check_date: "2026-09-14"
depends_on: ["tph-12"]
leads_to: ["tph-21"]
---

# Reformer: LSH attention and reversible stacks (13 January 2020)

**Status:** staged draft. Not a publication.
**Lane:** public transformer architecture history.
**First public appearance:** 13 January 2020 (`arxiv-v1`).
**Primary source:** Kitaev, Kaiser, Levskaya, *Reformer: The Efficient Transformer*,
arXiv:2001.04451.

## The claim

Reformer attacks two different bills with two different devices, and popular slides often keep
only one:

1. **LSH attention.** Hash queries and keys with locality-sensitive hashes so tokens attend
   inside the same hash bucket (plus a neighborhood), in the hope of \(O(n\log n)\) rather
   than \(O(n^2)\) attention.
2. **Reversible residual layers.** Recalculate activations on the backward pass instead of
   storing them, cutting activation memory — a training-memory move independent of the hash.

Both are 13 January 2020. Neither is FlashAttention. FlashAttention (2022) keeps exact
softmax attention and reorders IO. Reformer changes *who attends to whom* and *what is stored*.

## What the artifact specified

Shared-QK LSH attention (queries and keys from the same projection in the LSH variant),
multiple rounds of hashing to reduce the chance that a relevant key misses the bucket,
chunking along the sequence, and the reversible block design adapted from Gomez et al.
They show long-sequence tasks (including 64k) that a naive dense 2017 implementation of the
era could not hold in memory on the hardware they used.

Approximate attention means the mask is **content-dependent** and stochastic across hashes.
That is a different family from Longformer's fixed window.

## What it displaced

The idea that the only way to train long sequences was a bigger accelerator. It did not
displace dense attention as the quality default. After FlashAttention, "we hashed because
matmuls were impossible" has to be re-argued; many later systems chose exact attention plus
a better kernel.

## Immediate lineage

Routing Transformer, Sinkhorn, Nyströmformer, Performer, Linformer — the 2020 efficient-
Transformer wave. This series gives that wave two more cards (`tph-21`, `tph-22`) rather
than twenty stubs. Reformer is the January starting gun.

## What this draft does not claim

It does not claim LSH attention is exact. It does not claim reversible layers are widely
used in 2024 LLM pre-training (they are not the LLaMA-class default). It does not treat
any closed long-context product as a secret Reformer.

## Sources

- Kitaev, Kaiser, Levskaya, arXiv:2001.04451, published 2020-01-13 (`arxiv-v1`).
- Child et al., arXiv:1904.10509, published 2019-04-23 (`arxiv-v1`).
- Dao et al., arXiv:2205.14135, published 2022-05-27 (`arxiv-v1`).

## Draft debt

- Quote the paper's complexity statements and the 64k task names from the experiments
  section.
