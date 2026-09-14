---
id: "tph-32"
slug: "preln-rmsnorm-swiglu"
title: "Pre-LN, RMSNorm, and SwiGLU: the quiet modern stack (2019–2020)"
status: "staged-draft"
series: "transformers-public-history"
era: "2021-position-adapt"
first_public: "2019-10-16"
date_kind: "arxiv-v1-family"
arxiv: "1910.07467"
venue_later: "Xiong Pre-LN analysis 2020-02-12; Shazeer GLU variants 2020-02-12"
novelty_lane: "public-prior-art-only"
private_systems: "excluded"
depends_on: ["tph-05"]
leads_to: ["tph-41"]
---

# Pre-LN, RMSNorm, and SwiGLU: the quiet modern stack (2019–2020)

**Status:** staged draft. Not a publication.
**Lane:** public transformer architecture history.
**First public appearance:** 16 October 2019 (RMSNorm); 12 February 2020 (Pre-LN analysis and
GLU variants).
**Primary sources:** Zhang and Sennrich, arXiv:1910.07467; Xiong et al., arXiv:2002.04745;
Shazeer, arXiv:2002.05202.

## The claim

The 2023 LLaMA-class block is often described as if Meta invented a new Transformer. The
unpublished-looking pieces were public years earlier:

| Piece | 2017 default | Later public default | First public in this pack |
|---|---|---|---|
| Norm placement | post-LN | Pre-LN | GPT-2 report 2019-02-14 (use); Xiong et al. 2020-02-12 (analysis) |
| Norm flavor | LayerNorm | RMSNorm | 2019-10-16 |
| FFN nonlinearity | ReLU | SwiGLU / GeGLU | Shazeer 2020-02-12 |

This card exists so "LLaMA architecture" is not dated 2023 for those three widgets.

## What the artifacts specified

**RMSNorm:** normalize by root-mean-square, no mean centering, cheaper, used later by
Gopher/Chinchilla/LLaMA-class reports as a cited default.

**Pre-LN:** LayerNorm (or RMSNorm) *before* the sublayer; residual add stays outside. Xiong
et al. analyze gradient scales and why post-LN wants warmup. GPT-2 already shipped a Pre-LN
decoder; the 2020 paper is the public analysis many citations use.

**GLU variants:** Shazeer replaces \(\mathrm{ReLU}(xW_1)W_2\) with a gated linear unit,
\(\mathrm{Swish}(xW) \otimes (xV)\) then out-proj (SwiGLU), and reports quality gains. LLaMA
cites this. PaLM uses SwiGLU. The extra matrix is a real parameter/FLOP change, not a
rename of ReLU.

## What it displaced

The 2017 FFN and post-LN as unquestioned defaults for *new* large decoders. Translation
encoder–decoders and many BERT descendants kept older choices longer.

## Immediate lineage

LLaMA (27 February 2023) is the widely copied combination: Pre-LN + RMSNorm + SwiGLU + RoPE
+ GQA (GQA arrives in Llama 2 70B, not LLaMA-1). That *combination* is a 2023 assembly.
Every bolt is older.

## What this draft does not claim

It does not claim these three always co-occur. BLOOM used ALiBi, not RoPE. Some models keep
LayerNorm. It does not treat closed stacks as SwiGLU without a report.

## Sources

- Zhang and Sennrich, arXiv:1910.07467, published 2019-10-16 (`arxiv-v1`).
- Xiong et al., arXiv:2002.04745, published 2020-02-12 (`arxiv-v1`).
- Shazeer, arXiv:2002.05202, published 2020-02-12 (`arxiv-v1`).
- Touvron et al., arXiv:2302.13971, published 2023-02-27 (`arxiv-v1`).

## Draft debt

- Quote LLaMA §2's exact citations for these three.
