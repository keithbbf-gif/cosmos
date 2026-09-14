---
voice_check: human
title: "SimpleQA: a short fact, three grades"
slug: simpleqa
kind: explainer
era: 2024
tags: [simpleqa, openai, factuality]
portrait: null
portrait_status: none
figures:
  - ../assets/simpleqa/historical-timeline.svg
  - ../assets/simpleqa/instrument-chart.svg
---

Jason Wei, Karina Nguyen, Hyung Won Chung, Yunxin Joy Jiao, Spencer Papay, Amelia Glaese, John Schulman, and William Fedus published “Measuring short-form factuality in large language models” in 2024 (arXiv:2411.04368; also posted by OpenAI as the SimpleQA paper). The file has 4,326 short, fact-seeking questions. The answers are supposed to be single and indisputable. The grades are three: correct, incorrect, not attempted.

The third grade is the instrument. A model that guesses when it should shut up is not “informative.” It is wrong. A model that shuts up too often is calibrated and useless. SimpleQA wants the pairing: try the ones you know, skip the ones you do not.

## Why short form

<!-- graphics-pack:v1 -->

<figure class="eval-figure">
<img src="../assets/simpleqa/historical-timeline.svg" alt="Timeline of public milestones for SimpleQA: a short fact, three grades: dated anchors from the published record, not a live leaderboard." width="760" height="460" loading="lazy" decoding="async" />
<figcaption>Figure 1. Dated public anchors for this piece. Years follow the essay; verify against BIBLIOGRAPHY.md before print.</figcaption>
</figure>



## How it differs from older QA

<!-- graphics-pack:v1 -->

<figure class="eval-figure">
<img src="../assets/simpleqa/instrument-chart.svg" alt="Instrument chart for SimpleQA: a short fact, three grades: how items flow to a published metric (illustrative scoring shape, not scraped scores)." width="760" height="460" loading="lazy" decoding="async" />
<figcaption>Figure 2. Scoring shape for this instrument — protocol, not a weekly rank.</figcaption>
</figure>



## An item in the hand

A short question: who won a particular prize in a particular year; what is the capital of a first-order administrative region people confuse; what is a publication date that is not the first Google hit. The target is a string you can check. The model may answer, refuse, or waffle.

Waffle is the interesting failure. A judge that only has correct/incorrect will stuff a hedge into incorrect and call it a day. The paper’s third bucket exists so that a calibrated refusal is not punished the same way as a confident invention. If your implementation cannot see the third bucket, you are not running SimpleQA. You are running a trivia quiz with extra guilt.

Adversarial collection against GPT-4 means the items were chosen because a strong 2024 model already stumbled. That is a gift to later comparisons and a bias: the set is “hard for that student,” not a random sample of world facts. TriviaQA was closer to a dump of what the internet already asked. SimpleQA is closer to a filter on what a particular model got wrong.

## What “indisputable” cannot save

Facts move. Titles change. Populations update. A few items will age. A few will turn out to have been disputable after all. The authors aimed at a single target; they did not repeal the world. When you rerun the set a year later, sample the failures by hand.

The file is also a particular notion of fact: the kind that fits in a short string. Causal claims, legal interpretations, and “what should we do” questions are out of scope. Good.

## How to read a SimpleQA line

Report correct, incorrect, and not-attempted — not a single accuracy that treats a refusal as a zero without comment. Name the judge. If the card only prints one percentage, ask where the refusals went.

Wei and Nguyen’s group built a small, slightly stubborn factuality floor with a third door. Use the third door. A model that never uses it is not brave. It is uncalibrated.

A common mis-citation is to treat SimpleQA as TruthfulQA’s sequel. One asks for a small true fact and whether you will attempt it. The other tempts you toward a popular lie. Run both if you want both. Do not let one noun eat the other.
