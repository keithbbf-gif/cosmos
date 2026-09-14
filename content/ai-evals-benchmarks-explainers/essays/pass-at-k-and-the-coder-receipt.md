---
voice_check: human
title: "pass@k, a receipt for a sample"
slug: pass-at-k-and-the-coder-receipt
kind: essay
era: 2021–2024
tags: [pass-at-k, humaneval, mbpp, code]
portrait: null
portrait_status: none
figures:
  - ../assets/pass-at-k-and-the-coder-receipt/historical-timeline.svg
  - ../assets/pass-at-k-and-the-coder-receipt/instrument-chart.svg
---

Coding benchmarks did not have to invent a new metaphysics. They inherited unit tests. A function either satisfies the hidden tests or it does not. That is already cleaner than BLEU. The mess arrived when the models became samplers.

A language model does not emit one program. It emits a distribution. Temperature, nucleus sampling, and the number of tries are part of the instrument. Mark Chen and colleagues, in the 2021 Codex paper that also introduced HumanEval, needed a way to say “how often would you get a program that passes if you were allowed k samples?” They used `pass@k`.

The metric is a receipt, not a personality. This essay is about what the receipt says, and what it hides.

## The estimator

<!-- graphics-pack:v1 -->

<figure class="eval-figure">
<img src="../assets/pass-at-k-and-the-coder-receipt/historical-timeline.svg" alt="Timeline of public milestones for pass@k, a receipt for a sample: dated anchors from the published record, not a live leaderboard." width="760" height="460" loading="lazy" decoding="async" />
<figcaption>Figure 1. Dated public anchors for this piece. Years follow the essay; verify against BIBLIOGRAPHY.md before print.</figcaption>
</figure>


The naive version is easy to game in your head: generate k samples, if any one passes, count a win. If you report that number from a single lucky run of k, you have described a lottery ticket. The Codex paper, and the evaluation code that followed it, use an unbiased estimator from n ≥ k samples: draw n completions, count the number that pass, then estimate the probability that at least one of k random draws would have passed.

People still say “pass@1” when they mean “greedy decode, one try, temperature 0,” and they say “pass@100” when they mean “we threw a compute bag at the problem.” Those are different instruments that share a prefix. A table that mixes them without naming n, k, and temperature is a table of rumors.

## Why code got a cleaner cheap judge

<!-- graphics-pack:v1 -->

<figure class="eval-figure">
<img src="../assets/pass-at-k-and-the-coder-receipt/instrument-chart.svg" alt="Instrument chart for pass@k, a receipt for a sample: how items flow to a published metric (illustrative scoring shape, not scraped scores)." width="760" height="460" loading="lazy" decoding="async" />
<figcaption>Figure 2. Scoring shape for this instrument — protocol, not a weekly rank.</figcaption>
</figure>


BLEU compares strings to a reference translation. `pass@k` compares behavior to tests. Two programs that look nothing alike can both pass. That is the whole point of a test suite, and it is why HumanEval and MBPP (Austin et al., 2021) could score programs the authors had never seen.

The cleanliness is limited. Tests are not specifications. A HumanEval problem has a docstring, a signature, and a few hidden tests. A program can pass those tests and still be a menace: quadratic when it should be linear, wrong on an empty list the tests forgot, helpful in the way a stack-overflow snippet is helpful until production. MBPP’s “mostly basic” problems are mostly basic. They measure a real skill. They do not measure software engineering.

SWE-bench (Jimenez, Yang, Wettig, Yao, Pei, Press, Narasimhan; ICLR 2024) changed the receipt. The unit is not a function. It is a repository and an issue. The scorer is fail-to-pass tests from a real pull request, plus a check that previously passing tests still pass. That is still `pass` in spirit — did the suite go green? — and it is a different hardship. One sample is an agent trajectory, not a 20-line completion. People still quote a percentage. They should quote the harness: which subset, which tools, how many attempts.

## The compute leftover

`pass@k` makes compute part of the score. A weaker sampler with a hundred tries can beat a stronger sampler with one. That is not a scandal if you name k. It becomes a scandal when a plot implies a single “coding ability” axis. LiveCodeBench (Jain et al., 2024) and later contest-style suites exist partly because HumanEval’s 164 items, and the `pass@k` culture around them, were no longer hurting the models that had seen too many docstrings.

There is a second leftover: contamination of the tests themselves. If the hidden tests leaked into training, `pass@1` is memorization with a green bar. If the problem text leaked but the tests did not, you get a model that writes the textbook solution and still fails an off-by-one the hidden tests catch. Both happen. Neither is visible in a lone percentage.

## How to read a coding number

Ask:

1. Which file? HumanEval, HumanEval+, MBPP, DS-1000, LiveCodeBench, SWE-bench, a private fork?
2. Which k, which n, which temperature, greedy or not?
3. Does “pass” mean hidden unit tests, a pytest from a PR, or a model judge staring at code?
4. Was the model allowed tools, search, execution, or multiple files?

If the card cannot answer those, you do not have a coding eval. You have a vibe.

The receipt is still worth keeping. Execution is a better cheap judge than n-gram overlap. The field should not apologize for wanting a green test. It should apologize for saying the green test is a colleague.

HumanEval’s docstring is a small room. SWE-bench’s issue tracker is a larger one. `pass@k` will follow the models into both rooms if you let it. Let it. Then write down k.
