---
voice_check: human
title: "GPQA: graduate questions, Google not invited"
slug: gpqa
kind: explainer
era: 2023–2024
tags: [gpqa, diamond, rein]
portrait: null
portrait_status: none
figures:
  - ../assets/gpqa/historical-timeline.svg
  - ../assets/gpqa/instrument-chart.svg
---

David Rein, Betty Li Hou, Asa Cooper Stickland, Jackson Petty, Richard Yuanzhe Pang, Julien Dirani, Julian Michael, and Samuel R. Bowman published “GPQA: A Graduate-Level Google-Proof Q&A Benchmark” in 2023 (arXiv:2311.12022; later COLM 2024). The subtitle is the design. The questions are written by domain experts in biology, physics, and chemistry so that a non-expert with a search engine should still struggle, and an expert should be able to agree on the answer.

“Google-proof” is a 2023 sentence. It does not mean “proof against a 2026 agent with tools.” It means: we tried to write items that a web page will not politely hand you in the first snippet.

## What an item is

<!-- graphics-pack:v1 -->

<figure class="eval-figure">
<img src="../assets/gpqa/historical-timeline.svg" alt="Timeline of public milestones for GPQA: graduate questions, Google not invited: dated anchors from the published record, not a live leaderboard." width="760" height="460" loading="lazy" decoding="async" />
<figcaption>Figure 1. Dated public anchors for this piece. Years follow the essay; verify against BIBLIOGRAPHY.md before print.</figcaption>
</figure>



## Why Bowman is on this paper too

<!-- graphics-pack:v1 -->

<figure class="eval-figure">
<img src="../assets/gpqa/instrument-chart.svg" alt="Instrument chart for GPQA: graduate questions, Google not invited: how items flow to a published metric (illustrative scoring shape, not scraped scores)." width="760" height="460" loading="lazy" decoding="async" />
<figcaption>Figure 2. Scoring shape for this instrument — protocol, not a weekly rank.</figcaption>
</figure>



## An item in the hand

A diamond item in chemistry or physics asks for a distinction that a first-year survey course does not make. The distractors are the mistakes a confident almost-expert makes. A non-expert with a browser finds a related page and still cannot tell which letter is right. That gap — expert high, non-expert-with-Google low — is the authors’ acceptance test for an item.

If later agents close the non-expert gap by reading papers instead of snippets, the “Google-proof” adjective should be retired for those students. The file can remain. The adjective is a 2023 weather report.

Julian Michael and Samuel Bowman on the author list are a link back to GLUE’s editorial culture: hidden hardship, suspicion of easy numbers, a preference for a file you can argue about item by item.

## Tools change the instrument

A model allowed to browse, to read PDFs, to run code, is not taking the same test as a frozen chatbot. The “Google-proof” claim is about non-expert humans and ordinary search. An agent with a paper-reading tool is a different student. Cards that report GPQA with tools and GPQA without tools in the same breath are adding apples to a spectrometer.

## Contamination and expertise theater

Graduate questions still leak once they are famous. Diamond items will be screenshotted. A later crawl may contain them. The original “we asked experts to write new questions” shield is time-limited, like HumanEval’s handwritten shield.

There is also expertise theater: a question can be hard because it is obscure, or hard because it is well-posed. GPQA aims at the second. A few items, in any graduate set, will be the first. When a model fails, ask whether a working chemist would call the item fair.

## How to read a GPQA line

Name full versus Diamond, with or without tools, multiple-choice versus a generative recast, and the date. Compare to MMLU-Pro if you want broader undergraduate-plus hardship, and to Humanity’s Last Exam if you want a later, wider expert solicitation. Do not compare to GSM8K and call the axis “reasoning.” GPQA is graduate science recognition, Google-resistant at birth. That is already a long, specific claim. It does not need a larger noun.

A common mis-citation is to say “GPQA” and mean Diamond, or the reverse, without a word. The denominators differ. The word is cheap. Spend it.
