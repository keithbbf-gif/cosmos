---
id: "tph-45"
slug: "yarn-pagedattention-sinks-2023"
title: "2023 retrofits: interpolation, PagedAttention, sinks (June–October)"
status: "staged-draft"
series: "transformers-public-history"
era: "2023-open-serve"
first_public: "2023-06-27"
date_kind: "arxiv-v1-family"
arxiv: "2306.15595"
venue_later: "A six-month cluster; see body for per-item stamps"
novelty_lane: "public-prior-art-only"
private_systems: "excluded"
depends_on: ["tph-30", "tph-37", "tph-43"]
leads_to: ["tph-48"]
---

# 2023 retrofits: interpolation, PagedAttention, sinks (June–October)

**Status:** staged draft. Not a publication.
**Lane:** public transformer architecture history.
**First public appearance:** 27 June 2023 (Position Interpolation) as the cluster start.
**Primary sources:** listed per mechanism below. None of these require a new pretrain from
scratch in their type-case.

## The claim

Mid-2023 is a distinct phase: **the models already exist**, and the field publishes ways to
make them longer, cheaper to serve, or less broken at the start of a sliding window. The
mechanisms are from four families; only the calendar says they are one phase.

| Date | Object | Kind | ID / URL |
|---|---|---|---|
| 2023-06-27 | Position Interpolation | `arxiv-v1` | 2306.15595 |
| ≤2023-06-30 | NTK-aware scaled RoPE | `community-post` (weak pin) | TGI issue #512 + YaRN citation of bloc97 |
| 2023-07-07 | NTK-by-parts | `github-pr` | jquesnelle/yarn PR #1 |
| 2023-08-31 | YaRN | `arxiv-v1` | 2309.00071 (published 2023-08-31) |
| 2023-09-12 | PagedAttention / vLLM | `arxiv-v1` | 2309.06180 |
| 2023-09-27 | Mistral window ships | `official-blog` | `tph-43` |
| 2023-09-29 | Attention sinks / StreamingLLM | `arxiv-v1` | 2309.17453 |
| 2023-10-03 | Ring Attention | `arxiv-v1` | 2310.01889 |

NTK-aware RoPE originated as a Reddit post by u/bloc97. Automated fetches of Reddit fail.
This series pins it **on or before 30 June 2023** via Hugging Face TGI issue #512 (title
reproduces the post) and YaRN's citation. That is the weakest pin in the pack.

## What the artifacts specified

**PI / NTK / YaRN:** stretch RoPE's frequency basis so a 2k–4k-trained model can be
fine-tuned or even, in some claims, zero-shot extended. They disagree on how to treat high
vs low frequencies. YaRN is the named synthesis many configs later cite
(`rope_scaling.rope_type: yarn`).

**PagedAttention:** treat the KV cache like virtual memory — non-contiguous pages, no giant
pre-allocated contiguous cache per sequence. This is serving architecture. vLLM is the
system. It does not change softmax.

**Attention sinks:** softmax mass piles on the first tokens; if you drop them in a sliding
window, quality collapses. Keep a few "sink" tokens (plus the recent window). Qualcomm's
*Quantizable Transformers* (22 June 2023, arXiv:2306.12929) already discussed heads that
do nothing / outlier sinks in a quantization setting — three months earlier. StreamingLLM
is the generation-time naming event, not necessarily the first observation.

**Ring Attention:** blockwise attention so sequence shards live on different devices and
rotate; theoretically huge context if you pay communication. Not a sparse pattern.

## What it displaced

The idea that long context required a new pretrain. After this cluster, "extend the RoPE
and page the cache" is a default conversation. It did not make 1M-token *quality* free.

## Immediate lineage

LongRoPE (21 February 2024), Infini-attention (10 April 2024), Llama 3 / 4 long-context
claims (check each report; 10M-class numbers deserve upper-bound skepticism), and 2025
learned sinks in gpt-oss model cards.

## What this draft does not claim

It does not treat a vendor "128k context" as measured needle-in-haystack quality. It does
not claim Ring Attention is widely deployed. The bloc97 date stays weak until a primary
fetch exists.

## Sources

- Chen et al., arXiv:2306.15595, published 2023-06-27 (`arxiv-v1`).
- Peng et al., arXiv:2309.00071, published 2023-08-31 (`arxiv-v1`).
- Kwon et al., arXiv:2309.06180, published 2023-09-12 (`arxiv-v1`).
- Xiao et al., arXiv:2309.17453, published 2023-09-29 (`arxiv-v1`).
- Liu, Zaharia, Abbeel, arXiv:2310.01889, published 2023-10-03 (`arxiv-v1`).
- Bondarenko et al., arXiv:2306.12929, published 2023-06-22 (`arxiv-v1`).
- https://github.com/huggingface/text-generation-inference/issues/512 (`community-pin`).

## Draft debt

- Photograph TGI #512 and the YaRN bibliography entry.
- Re-read Ring Attention so a secondary-source ID mix-up (2310.01889 is the correct one)
  stays corrected.
