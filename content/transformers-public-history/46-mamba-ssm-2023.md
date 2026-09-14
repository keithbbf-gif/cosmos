---
id: "tph-46"
slug: "mamba-ssm-2023"
title: "Mamba: selective state spaces as a public alternative (1 December 2023)"
status: "staged-draft"
series: "transformers-public-history"
era: "2023-open-serve"
first_public: "2023-12-01"
date_kind: "arxiv-v1"
arxiv: "2312.00752"
venue_later: "S4 predecessor 2021-10-31 is cited, not this stamp"
novelty_lane: "public-prior-art-only"
private_systems: "excluded"
depends_on: ["tph-21"]
leads_to: ["tph-48"]
---

# Mamba: selective state spaces as a public alternative (1 December 2023)

**Status:** staged draft. Not a publication.
**Lane:** public transformer architecture history.
**First public appearance:** 1 December 2023 (`arxiv-v1`).
**Primary source:** Gu and Dao, *Mamba: Linear-Time Sequence Modeling with Selective State
Spaces*, arXiv:2312.00752.

## The claim

Mamba is in this *transformer* history because it is the 2023 public **alternative** that
forced hybrid papers. It is a selective structured state-space model: linear-time sequence
mixing with a content-dependent state, not softmax attention. S4 (Gu et al., 31 October
2021, arXiv:2111.00396) is the predecessor SSM; Mamba's bet is **selectivity** (parameters
of the state update depend on the input).

RWKV (22 May 2023, arXiv:2305.13048) and RetNet (17 July 2023, arXiv:2307.08621) are other
public alternatives in the same season. This card uses Mamba as the type-case because the
2024 hybrids (Jamba, Samba) name it.

## What the artifact specified

The selective SSM recurrence, a hardware-aware parallel scan, architecture blocks that
replace attention+FFN with Mamba blocks in the type-case, and language / genomics / audio
experiments. Author-reported 2023 quality/speed tables. There is no KV cache in the 2017
sense; there is a fixed-size state.

Zoology / MQAR (8 December 2023, arXiv:2312.04927) immediately asks whether such states
have a **recall** gap vs attention. That paper is why later hybrids keep "one layer in four
is attention."

## What it displaced

A late-2023 mood that decoder-only softmax was the only remaining architecture. It did not
retire Transformers. 2024–2026 production writes (Gemma 2 still attention; MiniMax's later
full-attention reversal; Qwen3-Next's hybrid) are the argument continuing, with timestamps.

## Immediate lineage

Jamba (28 March 2024, arXiv:2403.19887), Samba (11 June 2024, arXiv:2406.07522), Mamba-2,
Gated DeltaNet (9 December 2024, arXiv:2412.06464), Kimi Linear (30 October 2025,
arXiv:2510.26692). Those cards share `tph-48`.

## What this draft does not claim

It does not claim SSMs "won." It does not treat any closed 2025 model as secretly Mamba.
S4's 2021 date must not be overwritten by Mamba's 2023 fame.

## Sources

- Gu and Dao, arXiv:2312.00752, published 2023-12-01 (`arxiv-v1`).
- Gu et al., S4, arXiv:2111.00396, published 2021-10-31 (`arxiv-v1`).
- Peng et al., *RWKV*, arXiv:2305.13048, published 2023-05-22 (`arxiv-v1`).
- Sun et al., *RetNet*, arXiv:2307.08621, published 2023-07-17 (`arxiv-v1`).

## Draft debt

- Quote Mamba's layer diagram vs a Transformer block from the PDF.
