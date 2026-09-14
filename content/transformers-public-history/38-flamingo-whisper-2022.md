---
id: "tph-38"
slug: "flamingo-whisper-2022"
title: "Flamingo and Whisper: cross-attention and sequence beyond text (2022)"
status: "staged-draft"
series: "transformers-public-history"
era: "2022-align-kernel"
first_public: "2022-04-29"
date_kind: "arxiv-v1-family"
arxiv: "2204.14198"
venue_later: "Whisper arXiv:2212.04356 on 2022-12-06"
novelty_lane: "public-prior-art-only"
private_systems: "excluded"
depends_on: ["tph-29", "tph-16"]
leads_to: ["tph-41"]
---

# Flamingo and Whisper: cross-attention and sequence beyond text (2022)

**Status:** staged draft. Not a publication.
**Lane:** public transformer architecture history.
**First public appearance:** 29 April 2022 (Flamingo); 6 December 2022 (Whisper).
**Primary sources:** Alayrac et al., *Flamingo*, arXiv:2204.14198; Radford et al.,
*Robust Speech Recognition via Large-Scale Weak Supervision*, arXiv:2212.04356.

## The claim

Two 2022 public systems show the 2017 block leaving the text-only box **without** becoming
a new primitive.

**Flamingo** (29 April 2022): a frozen (or separately trained) vision encoder, a large
frozen language model, and **gated cross-attention** layers inserted so text tokens can
read visual tokens. Few-shot multimodal learning is the evaluation story. The architecture
lesson is **cross-attention as a bolt-on**, not "train a ViT-GPT from scratch."

**Whisper** (6 December 2022): an encoder–decoder Transformer for speech recognition /
translation, trained on large-scale weak supervision (audio–transcript pairs). Architecturally
it is T5-adjacent seq2seq pointed at spectrogram patches / audio features. The lesson is
that the 2017 diagram, with enough noisy paired data, becomes a default ASR stack.

A wrong Flamingo id (2204.11175) resolves to a physics paper. The correct id is
**2204.14198**.

## What the artifacts specified

Flamingo: Perceiver-resampler (or similar) to a small number of visual tokens, interleaved
cross-attention with tanh gates, frozen LM weights in the type-case. Whisper: 80-channel
log-mel, encoder–decoder depths from tiny to large-v2 in the paper/card, multilingual
speech, task tokens (transcribe / translate).

Neither is LLaVA (17 April 2023), which uses a **linear projector** into a decoder-only
LM rather than Flamingo-style gated cross-attention. Those are different multimodal
wirings. Do not collapse them.

## What it displaced

The idea that "Transformer multimodal" had to mean CLIP-style contrastive only, or that
ASR had to mean a specialized recurrent/CTC stack to get robustness. Whisper in particular
reset the public ASR baseline.

## Immediate lineage

LLaVA, BLIP-2, MiniGPT-4, and a 2023 forest of projector-based VLMs. Audio Flamingo and
later audio LMs are descendants in name and sometimes in wiring. Keep the 2022 stamps.

## What this draft does not claim

It does not claim Flamingo weights were released (they were not, originally). It does not
treat GPT-4V as Flamingo. Closed visual stacks stay unpublished unless a report speaks.

## Sources

- Alayrac et al., arXiv:2204.14198, published 2022-04-29 (`arxiv-v1`).
- Radford et al., arXiv:2212.04356, published 2022-12-06 (`arxiv-v1`).
- Liu et al., arXiv:2304.08485, published 2023-04-17 (`arxiv-v1`).

## Draft debt

- Quote Flamingo's gate / resampler sizes from the PDF.
