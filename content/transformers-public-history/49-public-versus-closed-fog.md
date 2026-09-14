---
id: "tph-49"
slug: "public-versus-closed-fog"
title: "The architecture fog: what closed reports withhold (2023–2026)"
status: "staged-draft"
series: "transformers-public-history"
era: "2024-2026-select"
first_public: "2023-03-15"
date_kind: "arxiv-v1-typecase"
arxiv: "2303.08774"
venue_later: "GPT-4 report as the type-case of a withhold"
novelty_lane: "public-prior-art-only"
private_systems: "excluded"
depends_on: ["tph-23", "tph-34"]
leads_to: []
---

# The architecture fog: what closed reports withhold (2023–2026)

**Status:** staged draft. Not a publication.
**Lane:** public transformer architecture history.
**First public appearance:** 15 March 2023 for the type-case withhold (GPT-4 report).
**Primary source:** OpenAI, *GPT-4 Technical Report*, arXiv:2303.08774.

## The claim

From GPT-3 (28 May 2020) to GPT-4 (15 March 2023) the public record **changes genre**.
GPT-3 published layer counts, widths, head counts, and a sparse/dense note. GPT-4
publishes capability, contamination discussion, and safety tests, and **explicitly does
not** publish architecture, hardware, or training compute. A history that then fills those
cells from rumor has left the public lane.

This card is the series' refusal protocol for closed systems.

## What the artifacts specified (as withholds)

**GPT-4 (2023-03-15).** Architecture, size, hardware, training compute: not disclosed. The
report is still a primary source for *evals and the fact of the withhold*.

**ChatGPT (2022-11-30 official blog).** Product launch. No block diagram. Instruction /
dialogue wrapping of a GPT-3.5-class model is the public description of that moment; later
versions are not specified here.

**Claude / Gemini / Grok product lines.** Technical reports and model cards, when they
exist, vary. Gemini 1 (6 December 2023 family paper) is more architectural than GPT-4 on
some multimodal points and still not a LLaMA-style §2. Treat each card as its own
artifact. Do not copy a leaked slide into this folder.

**What stayed public anyway.** Open-weight reports (LLaMA, Mistral, Mixtral, DeepSeek-V2/V3,
Gemma, Qwen, Phi, gpt-oss) plus kernel papers (FlashAttention) plus serving papers (vLLM)
are enough to write forty drafts without guessing closed stacks. That is the point of the
pack.

## What it displaced

The 2017–2020 norm that a flagship model paper included Table 2.1. After GPT-4, "we trained
a transformer-based model" is sometimes the entire architecture section. Science moved to
whoever still published `config.json`.

## Immediate lineage

gpt-oss (8 August 2025, arXiv:2508.10925) is notable as a later OpenAI **open-weight card**
with inspectable config fields (layer types, window, rope scaling). That does not retroactively
open GPT-4. It shows the withhold is a *choice*, not a law of nature.

## What this draft does not claim

It does not reconstruct GPT-4, Claude, Gemini Ultra, or any unnamed private stack. It does
not treat "everyone knows it is a MoE" as a source. It does not analogize any closed
product to a private non-public system outside this reading pack.

If a later official report publishes a block, a new draft can date *that* report. Until
then the correct sentence is: **unpublished**.

## Sources

- OpenAI, arXiv:2303.08774, published 2023-03-15 (`arxiv-v1`).
- Brown et al., arXiv:2005.14165, published 2020-05-28 (`arxiv-v1`) — contrast: a paper
  that did publish the table.
- OpenAI, *Introducing ChatGPT*, 2022-11-30 (`official-blog`).
- OpenAI, arXiv:2508.10925, published 2025-08-08 (`arxiv-v1`) — later open card, not a
  GPT-4 reveal.

## Draft debt

- List Gemini 1 / Claude model-card URLs with what they actually disclose, sentence by
  sentence, on a later pass.
