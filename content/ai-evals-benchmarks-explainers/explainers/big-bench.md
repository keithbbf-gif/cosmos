---
voice_check: human
title: "BIG-bench: a barn raising with two hundred tasks"
slug: big-bench
kind: explainer
era: 2022–2023
tags: [big-bench, google, beyond-the-imitation-game]
portrait: null
portrait_status: none
---

BIG-bench is what happens when a field tries to crowdsource its own exam. Aarohi Srivastava, Abhinav Rastogi, Abhishek Rao, and a very long author list published “Beyond the Imitation Game: Quantifying and Extrapolating the Capabilities of Language Models” — the paper is dated 2022 on arXiv (2206.04615) and later appeared in *Transactions on Machine Learning Research* (2023). Google organized. The community donated tasks. The acronym is a stretch that everyone immediately shortened.

The imitation game in the title is Turing’s. The “beyond” is a pile: hundreds of tasks, contributed by hundreds of people, covering problems that did not fit in GLUE’s English classification mood — arithmetic, proto-science, social reasoning, constructed languages, jokes that stop being jokes when you explain them.

## A benchmark as a conference

Most suites are edited like a journal special issue: a small committee, a taste. BIG-bench is edited like a conference. Tasks have authors. Tasks have varying quality. Some are clever and tiny. Some are large and dull. Some measure a real capability. Some measure whether the model has seen a particular meme. The paper is explicit that this heterogeneity is the point. Diversity of hardship over purity of hardship.

The original public release is in the hundreds of tasks (the paper’s abstract and later write-ups commonly say 204). Do not invent a more precise folklore number; cite the paper’s table if you need one. A JSON format, a GitHub repository, and a rule that you could add a task made the suite feel like infrastructure.

## What “beyond” included

Things GLUE would not have hosted. Program-like reasoning. Translation between toy languages. Moral and social hypotheticals of uneven seriousness. Music and ASCII. Tasks that are easy to contaminate because they are fun to screenshot. Tasks that are hard to score because the authors wanted generation, not a letter.

The scoring is therefore a federation. Some tasks are exact match. Some are multiple choice. Some need a human or a heuristic. The headline “BIG-bench score” you see on a card is usually a subset average, often the “lite” slice, not a sacred mean of all 200-plus. If the card does not name the slice, it is not a BIG-bench number. It is a mood.

## Scale as a character

The paper’s scientific plot is scale. They ran models of different sizes, including Google’s own, and asked which tasks suddenly yield as parameters grow. The “breakthrough” language in the surrounding discussion — capabilities that look flat and then jump — comes from this plot and from later popularizations. Treat “breakthrough” as a description of a curve, not as a metaphysics. Some tasks yield smoothly. Some stay flat. Some are too noisy to say.

Because Google organized, and because some evaluated models were Google’s, a careful reader keeps the affiliation in view. The paper is still a community object. The runs are still someone’s compute.

## The lite fork and the hard fork

A 200-task suite is a poor CI job. BIG-bench Lite exists because people needed a cheaper slice. BIG-bench Hard (Suzgun et al., 2022) exists because people needed the tasks that large models still failed. See [BIG-bench Hard](big-bench-hard.md). Those forks are how a barn raising becomes a toolkit. They are also how the original name starts to mean three instruments.

## What it taught the next suites

It taught that you can solicit evals the way you solicit workshop papers. Humanity’s Last Exam later solicited expert questions with a different editorial bar. HELM solicited a taxonomy instead of a task bazaar. Arena solicited voters. BIG-bench is the bazaar.

It also taught that a zoo is hard to cite honestly. “We evaluate on BIG-bench” is, by itself, an empty sentence. Which tasks, which scoring, which models in the original paper’s tables versus your own re-run?

## How to read it now

Use it as a map of what 2021–2022 researchers thought a language model might fail. Use BBH when you want the failures that lasted a bit longer. Do not use a single zoo-average as a mind. The imitation game was one question in a room. BIG-bench was hundreds of questions in a repository. Quantity was the method. Editorial unevenness was the price. Both should appear in the citation.
