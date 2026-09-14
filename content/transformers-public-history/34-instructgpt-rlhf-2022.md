---
id: "tph-34"
slug: "instructgpt-rlhf-2022"
title: "InstructGPT and RLHF: aligning the decoder (January–March 2022)"
status: "staged-draft"
series: "transformers-public-history"
era: "2022-align-kernel"
first_public: "2022-01-27"
date_kind: "official-blog-then-arxiv"
arxiv: "2203.02155"
venue_later: "arXiv v1 2022-03-04; OpenAI blog 2022-01-27"
novelty_lane: "public-prior-art-only"
private_systems: "excluded"
depends_on: ["tph-23"]
leads_to: ["tph-44", "tph-49"]
---

# InstructGPT and RLHF: aligning the decoder (January–March 2022)

**Status:** staged draft. Not a publication.
**Lane:** public transformer architecture history.
**First public appearance:** 27 January 2022 (`official-blog`); paper 4 March 2022
(`arxiv-v1`).
**Primary source:** Ouyang et al., *Training language models to follow instructions with
human feedback*, arXiv:2203.02155; OpenAI blog *Aligning language models to follow
instructions*.

## The claim

InstructGPT does not introduce a new attention primitive. It publicizes a **three-stage
training architecture** on top of a GPT-3-class decoder: (1) supervised fine-tune on
instruction demonstrations, (2) train a **reward model** on human pairwise comparisons,
(3) optimize the policy with PPO against that reward model, with a KL penalty back to the
SFT (or pretrained) policy.

Two dates, two kinds: the blog is 27 January 2022; the arXiv v1 is 4 March 2022. Secondary
timelines that pick one and hide the other are sloppy. This series keeps both.

Christiano et al. 2017 (RLHF for control) and Ziegler et al. 2019 (RLHF on language models)
are predecessors. InstructGPT is the type-case that tied RLHF to the **instruction-following
decoder product**.

## What the artifact specified

Human data pipelines (labeler instructions, comparison interface), reward-model training,
PPO details, and evaluations on "following instructions" vs raw GPT-3. The 1.3B InstructGPT
preferred over 175B GPT-3 on their human evals is the headline social fact; it is
author-reported and setup-specific.

Architecturally, the load-bearing new *object* is the **reward model** (usually another
Transformer that outputs a scalar) and the KL-regularized RL loop. Those objects later get
replaced by DPO (29 May 2023), which skips the explicit RL step.

## What it displaced

"The model is the pretrained LM" as a complete description of a deployed assistant. After
InstructGPT, a serious write-up must say **pretrain / SFT / preference**. ChatGPT
(30 November 2022 official blog) is a product on this line; it is not a block diagram.

## Immediate lineage

Anthropic HH / Constitutional AI (Bai et al., 15 December 2022 for CAI). Llama 2 Chat
(18 July 2023) publishes a long RLHF section. DPO, ORPO, KTO, GRPO, and process-reward
models are later public preference stacks. This card does not flatten them into "RLHF."

## What this draft does not claim

It does not claim PPO is the only legal preference method. It does not reconstruct
ChatGPT's unpublished later stacks from this paper. It does not treat safety policy as
architecture except where the paper specifies a loss.

## Sources

- Ouyang et al., arXiv:2203.02155, published 2022-03-04 (`arxiv-v1`).
- OpenAI, *Aligning language models to follow instructions*, 2022-01-27 (`official-blog`).
- Bai et al., *Constitutional AI*, arXiv:2212.08073, published 2022-12-15 (`arxiv-v1`).
- Rafailov et al., *DPO*, arXiv:2305.18290, published 2023-05-29 (`arxiv-v1`).

## Draft debt

- Quote the KL coefficient discussion from the paper.
