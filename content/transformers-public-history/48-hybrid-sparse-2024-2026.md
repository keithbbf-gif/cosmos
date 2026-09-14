---
id: "tph-48"
slug: "hybrid-sparse-2024-2026"
title: "Interleaved, sparse, and hybrid stacks (2024–2026 public fight)"
status: "staged-draft"
series: "transformers-public-history"
era: "2024-2026-select"
first_public: "2024-07-31"
date_kind: "arxiv-v1-family"
arxiv: "2408.00118"
venue_later: "A moving argument; stamps in the table"
novelty_lane: "public-prior-art-only"
private_systems: "excluded"
depends_on: ["tph-43", "tph-46", "tph-47"]
leads_to: ["tph-49"]
---

# Interleaved, sparse, and hybrid stacks (2024–2026 public fight)

**Status:** staged draft. Not a publication.
**Lane:** public transformer architecture history.
**First public appearance:** 31 July 2024 used as the Gemma 2 stamp that makes
interleaving boring; the fight continues through 2026.
**Primary sources:** per row below. Prefer `config.json` over marketing when they disagree.

## The claim

Once windows, linear states, and full softmax all exist, labs **mix them**, then publicly
disagree about whether the mix was worth it. This card is a dated map, not a winner.

| Date | Object | Kind | Source |
|---|---|---|---|
| 2024-03-28 | Jamba (Transformer–Mamba hybrid) | `arxiv-v1` | 2403.19887 |
| 2024-06-11 | Samba | `arxiv-v1` | 2406.07522 |
| 2024-07-31 | Gemma 2 interleaved local/global | `arxiv-v1` | 2408.00118 |
| 2024-10-07 | Differential Transformer | `arxiv-v1` | 2410.05258 |
| 2024-12-09 | Gated DeltaNet | `arxiv-v1` | 2412.06464 |
| 2025-01-14 | MiniMax-01 lightning attention | `arxiv-v1` | 2501.08313 |
| 2025-02-16 | Native Sparse Attention | `arxiv-v1` | 2502.11089 |
| 2025-04-05 | Llama 4 iRoPE blog claim | `official-blog` | ai.meta.com Llama 4 post |
| 2025-08-08 | gpt-oss model card (learned sinks; alternating layer types) | `arxiv-v1` | 2508.10925 |
| 2025-10-30 | Kimi Linear | `arxiv-v1` | 2510.26692 |
| 2025-10-30 | MiniMax M2 "back to full attention" | `official-blog` + later report | same-day disagreement with Kimi |
| 2025-12-13 | DroPE | `arxiv-v1` | 2512.12167 |

Gemma 2's paper says they alternate local sliding-window and global attention. Gemma 3
(later card, official 2025) tightens the local span and changes the local:global ratio —
read the card, not this paragraph, for Gemma 3. gpt-oss-120b's public `config.json` (when
read by third parties in 2025) is the kind of artifact this series prefers for "alternating
`sliding_attention` / `full_attention`": the file, not the keynote.

## What this phase specified

Three design questions, finally asked at once:

1. **Where is the state?** Full KV (linear in tokens), windowed KV, latent KV (MLA), or a
   fixed-size SSM/linear state.
2. **Which tokens are worth scoring?** NSA, MoBA, DeepSeek sparse attention experiments.
3. **Do you still need positions?** DroPE's public bet is that you can drop them after
   some training. That is one paper from one lab in December 2025 until reproduced.

MiniMax's 30 October 2025 full-attention reversal is the honesty check: a lab that shipped
linear/lightning attention can say, in public, that the KV cache was the thing they did
not want to lose. Kimi Linear, same day, argues the other side. Architecture history that
erases one of those posts is propaganda.

## What it displaced

The 2023 slogan that everyone would converge on "LLaMA block + GQA + YaRN + FlashAttention."
That slogan is still a good *starting* stack. It is no longer the only public endgame.

## Immediate lineage

Whatever 2026 MiniMax Sparse Attention and later cards add. This pack stops at staged
drafts, not at a finish line.

## What this draft does not claim

It does not rank these mechanisms. It does not treat blog FLOP claims as measurements. It
does not analogize any of them to a private system. Llama 4's long-context marketing number
is an upper-bound-class claim until a measurement paper says otherwise.

## Sources

- Gemma Team, arXiv:2408.00118, published 2024-07-31 (`arxiv-v1`).
- Yuan et al., arXiv:2502.11089, published 2025-02-16 (`arxiv-v1`).
- OpenAI, arXiv:2508.10925, published 2025-08-08 (`arxiv-v1`).
- Kimi / Moonshot, arXiv:2510.26692, published 2025-10-30 (`arxiv-v1`).
- Gelberg et al., arXiv:2512.12167, published 2025-12-13 (`arxiv-v1`).
- MiniMax-01, arXiv:2501.08313, published 2025-01-14 (`arxiv-v1`).

## Draft debt

- Re-read gpt-oss `config.json` and Qwen3-Next `config.json` end to end and quote
  `layer_types` / `full_attention_interval` rather than secondary summaries.
- Fetch the MiniMax M2 blog paragraph on why they returned to full attention.
