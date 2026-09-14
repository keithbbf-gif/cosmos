---
id: "tph-53"
slug: "alphafold2-evoformer-2021"
title: "AlphaFold 2 Evoformer: attention off the language axis (15 July 2021)"
status: "staged-draft"
series: "transformers-public-history"
era: "2021-position-adapt"
first_public: "2021-07-15"
date_kind: "official-journal"
arxiv: ""
venue_later: "Nature 2021; CASP14 late-2020 results are not the full block diagram"
novelty_lane: "public-prior-art-only"
private_systems: "excluded"
depends_on: ["tph-02", "tph-03"]
leads_to: ["tph-25"]
---

# AlphaFold 2 Evoformer: attention off the language axis (15 July 2021)

**Status:** staged draft. Not a publication.
**Lane:** public transformer architecture history.
**First public appearance:** 15 July 2021 (`official-journal`).
**Primary source:** Jumper et al., *Highly accurate protein structure prediction with
AlphaFold*, Nature 596, 583–589 (2021).

## The claim

AlphaFold 2 is in a *language-Transformer* history because it is the most famous public
proof that **the 2017 primitives are not a language architecture**. The Evoformer stack
runs attention over a **multiple-sequence-alignment (MSA) representation** and over a
**pair representation** (residue \(i\), residue \(j\)), with information passing between
those two tensors. The score function is still attention. The axes are biological.

CASP14 (December 2020) made the *accuracy* public. This series dates the **block** at the
Nature paper, 15 July 2021, because that is when the diagrams, pair attention, and
invariant point attention (IPA) structure module were specified in a citable artifact.
A results announcement is not a wiring diagram.

## What the artifact specified

- MSA stack: attention over sequences and over residues.
- Pair stack: attention / triangle updates over the \(N_{\mathrm{res}} \times
  N_{\mathrm{res}}\) pair features (this is where the quadratic bill reappears, now in
  residue pairs).
- Structure module: IPA and 3D frame updates, not a language LM head.
- Recycling: run the network several times with its own outputs as additional input.

OpenFold and later ESMFold / RoseTTAFold papers are descendants or cousins and get their
own dates. ESM-2 (2022) is a **language-model-on-sequences** approach to proteins, a
different bet (parametric LM vs AF2's MSA+pair geometry).

## What it displaced

The idea, still common in 2019 slides, that Transformers were an NLP fashion. After AF2,
a serious architecture history has to include **pair-biased attention** and domain-specific
axes. It did not displace language decoders; it widened the primitive's passport.

## Immediate lineage

OpenFold (public reimplementation), AlphaFold-Multimer, later AF3 (2024, a different
architecture with a diffusion-style module — date AF3 by its own paper, do not steal
2021). Protein language models (ESM, ProtTrans, later ESM-3) are a parallel public line.

## What this draft does not claim

It does not claim AF2 uses the 2017 *translation* diagram. It does not treat later
closed biological models as Evoformers. Nature's 15 July 2021 stamp is the block date;
CASP14 is the result date. Both sentences can be true if they stay labeled.

## Sources

- Jumper et al., Nature 596, 583–589 (2021), published 2021-07-15 (`official-journal`).
- Vaswani et al., arXiv:1706.03762 — primitives, not the Evoformer.
- Lin et al., ESM-2 / related ESM papers — different protein-LM line; do not merge.

## Draft debt

- Add the Nature DOI and page the pair-attention figure on a PDF pass.
- Date RoseTTAFold (Baek et al., 2021) as a sibling if a biology sequel pack opens.
