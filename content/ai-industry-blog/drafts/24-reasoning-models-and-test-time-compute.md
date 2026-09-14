---
title: "Reasoning models and test-time compute"
slug: reasoning-models-and-test-time-compute
meta_description: "o1-preview (12 Sept 2024), DeepSeek-R1 (20 Jan 2025), and the bet that thinking longer can beat training larger."
tags: [o1, deepseek-r1, reasoning, test-time, 2024, 2025]
era_start: 2024-09
citations:
  - "O1 https://openai.com/index/introducing-openai-o1-preview/"
  - "DEEPSEEK2025 https://arxiv.org/abs/2501.12948"
  - "GPT5 https://openai.com/index/introducing-gpt-5/"
status: draft
voice_check: human
---

On 12 September 2024, OpenAI posted *Introducing OpenAI o1-preview*. The claim was not a bigger pretrain. It was a model trained to spend more time "thinking" before it answers — hidden chain-of-thought, reinforcement learning, better scores on math, code, and science slices. Rate limits at launch were tiny (the 17 September update: 50 o1-preview queries per week on the Plus tier, in their post). People used the fifty. Screenshots of the "thought" UI leaked a culture: wait longer, pay more, get a better integral.

On 20 January 2025, DeepSeek-R1 landed with weights and a paper that was more specific about the RL stage than OpenAI had been. Hugging Face's Open-R1 write-up (28 January 2025) called the week what it was: a closed recipe, partially opened, immediately cloned. Equity markets noticed. This pack is not a trading desk. The engineering notice is enough. Test-time compute was no longer a single vendor's SKU.

## What "thinking" is, publicly

You do not have OpenAI's recipe. You have a blog, a model card, and later o-series ships (o1, then o3-class announcements in late 2024 / 2025 — verify the card in front of you; the letter-number soup moved fast). The public shape: generate a long internal trace, score it against checkable rewards (unit tests, math answers, format), reinforce the traces that win, hide most of the trace from the user so you do not leak a jailbreak surface or a copyrighted chain.

DeepSeek-R1-Zero, in their telling, skipped supervised fine-tune and went straight to RL on a capable base (DeepSeek-V3, a 671B MoE). R1 then added a more palatable pipeline so the thing would speak like a product. Group Relative Policy Optimization (GRPO) is the named optimizer in the paper. Replicators had to rebuild data they were not given.

Process-vs-outcome rewards are the research fight. Outcome: did the boxed answer match. Process: did step 4 deserve a point. Outcome is easy to game with a lucky last line. Process is expensive to label. The 2025 papers you have not finished yet are mostly this fight.

## Chain-of-thought, the 2022 parent

Wei et al., *Chain-of-Thought Prompting* (2022), and the self-consistency follow-ups already showed that "think step by step" plus majority vote lifts math. o1 is that idea with a training loop and a hidden trace. People who treat 2024 as a new science are skipping a paper. People who treat 2024 as "just CoT" are skipping the RL and the verifier. Both skips make you a worse buyer.

Process supervision (Uesato, Lightman et al., the "let's verify step by step" line, 2023) is the research that tried to grade the middle of the proof. Expensive. Closer to how a human TA works. If your vendor says "process reward" and will not say who labeled the steps, they mean outcome reward with better PR.

## What it is good at, and not

Good: contest math, coding problems with a test, puzzles that look like the RL environment. The o1 launch tables (AIME, Codeforces-ish, GPQA-style science) are the genre.

Bad: "what's our refund policy" (you wanted RAG), "be warm on a crisis line" (you wanted a small aligned chat model), "don't spend $2 of decode on a yes/no." A reasoning model is a bad default for a customer-support button. GPT-5 (7 August 2025) was sold as a unified system that *picks* when to think longer. That is the product admission. Always-on o1 is a bill.

Also bad: unverifiable tasks. If you cannot check the answer, RL on "looks smart" will buy you fluent wrong. Hidden traces make this worse to debug. If your vendor will not show a redacted trace on a failure, you are buying a priest.

## Test-time compute as a scaling axis

Kaplan's 2020 laws were about train FLOPs. 2024–26 added a second axis: FLOPs at the request. Search (sample many, pick a winner), longer traces, tool-in-the-loop, majority vote. Snell et al. and the "inference scaling" notes (2024) are the academic cousins. `[CITE NEEDED]` if you quote a specific exponent; the popular graphs are lab-specific.

This axis has a human cost. Latency. A 40-second think is fine for a theorem and fatal for a voice barge-in (see the voice draft). Product design is a router: cheap model first, reasoner on hard, cache the proof.

## Safety, said once

A model that thinks longer can also scheme longer, in the toy-eval sense the safety papers use. OpenAI said they ran extra preparedness work and gave early access to the US/UK AISIs. Treat that as a process claim. Hidden traces are a new logging problem. If you cannot store the thought, you cannot audit it. If you store it, you have a new confidential corpus.

## Opinion

o1 made "wait" a feature. R1 made "wait" a file. GPT-5 tried to hide the toggle. The useful 2026 habit is the toggle you own: a verifier, a budget, and a model that is allowed to think only when you can check the work.

If you cannot check the work, you did not want a reasoner. You wanted a citation.
