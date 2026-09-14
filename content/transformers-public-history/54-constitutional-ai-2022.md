---
id: "tph-54"
slug: "constitutional-ai-2022"
title: "Constitutional AI: preference without a human on every pair (15 December 2022)"
status: "staged-draft"
series: "transformers-public-history"
era: "2022-align-kernel"
first_public: "2022-12-15"
date_kind: "arxiv-v1"
arxiv: "2212.08073"
venue_later: ""
novelty_lane: "public-prior-art-only"
private_systems: "excluded"
voice_check: "edited"
voice_check_date: "2026-09-14"
depends_on: ["tph-34"]
leads_to: ["tph-44"]
---

# Constitutional AI: preference without a human on every pair (15 December 2022)

**Status:** staged draft. Not a publication.
**Lane:** public transformer architecture history.
**First public appearance:** 15 December 2022 (`arxiv-v1`).
**Primary source:** Bai, Kadavath, Kundu, Askell, Kernion, Jones, Chen, Goldie, Mirhoseini,
McKinnon, Chen, Olsson, Olah, Hernandez, Drain, Ganguli, Li, Tran-Johnson, Perez, Kerr,
Mueller, Ladish, Landau, Ndousse, Lukosuite, Lovitt, Sellitto, Elhage, Schiefer, Mercado,
DasSarma, Lasenby, Larson, Ringer, Johnston, Kravec, El Showk, Fort, Lanham, Telleen-Lawton,
Conerly, Henighan, Hume, Bowman, Hatfield-Dodds, Mann, Amodei, Joseph, McCandlish, Brown,
Kaplan, *Constitutional AI: Harmlessness from AI Feedback*, arXiv:2212.08073.

## The claim

Constitutional AI (CAI) is training architecture on the InstructGPT line: still a decoder,
still a preference stage, but the **critique and revision** of responses is done by a
model against a written **constitution** (a list of principles), and the preference model
can be trained on **AI feedback** (RLAIF) rather than on a human pair for every sample.

This is 15 December 2022 — two weeks after the ChatGPT blog, and not a ChatGPT paper.
Anthropic's earlier HH / "Helpful and Harmless" paper (12 April 2022, often cited as
arXiv:2204.05862) is the human-RLHF sibling. CAI is the *constitution + AI feedback*
move.

## What the artifact specified

A two-phase story: (1) supervised constitutional critique/revision to get a harmless-ish
SFT policy, (2) RLAIF using a preference model trained on AI-labeled comparisons guided
by the constitution. The constitution itself is an appendix artifact — a public list of
principles, not a neural block. That list is part of the specified system. A write-up that
says "we used CAI" without saying which principles is underspecified.

The attention formula does not change. The **data-generation graph** does. This series
keeps those graphs when they become the thing labs copy (see also DPO, `tph-44`).

## What it displaced

The claim that the only public preference recipe was "hire more labelers." After CAI,
synthetic preference data is a first-class, citable method. It did not make human data
obsolete; it changed the mix.

## Immediate lineage

RLAIF follow-ups, Claude product model cards that mention constitutional methods without
publishing the stack, and a 2023–2025 industry of "LLM-as-judge" pipelines. Self-Instruct
(20 December 2022, arXiv:2212.10560) is a *different* synthetic-data paper (instruction
generation, not constitutional harmlessness) five days later. Do not merge them.

## What this draft does not claim

It does not claim CAI is sufficient for safety. It does not reconstruct unpublished Claude
blocks from this paper. It does not treat a constitution as a legal document; it is a
training artifact in this pack.

## Sources

- Bai et al., arXiv:2212.08073, published 2022-12-15 (`arxiv-v1`).
- Ouyang et al., arXiv:2203.02155, published 2022-03-04 (`arxiv-v1`).
- Wang et al., *Self-Instruct*, arXiv:2212.10560, published 2022-12-20 (`arxiv-v1`).

## Draft debt

- Quote the paper's list of stages from Figure 1.
- Confirm the HH paper's arXiv id and stamp on a dedicated fetch.
