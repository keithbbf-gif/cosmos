---
title: RedPajama, Dolma, and the open-data bet
slug: redpajama-dolma-open-data
series: open-source-ai-history-2015-2026
status: draft
voice_check: human
reading_order: 42
word_target: 600-1800
era: "2023–2026"
stack:
  - data
---

# RedPajama, Dolma, and the open-data bet

Weights without data docs are a magic trick. The 2023–2024 answer from a set of labs was to publish corpora that tried to approximate a Llama-like mix, or to publish a corpus with a paper and a license you could name.

Together’s RedPajama announcement is 17 April 2023, not March. The March date that wandered into secondary timelines is the month of the leak and Alpaca, not the dataset post. RedPajama-Data-1T was the approximation bet: rebuild the mixture described in the LLaMA paper from public sources so a base model would not have to be a leak. Allen Institute for AI’s Dolma (first dump 18 August 2023) was the documentation bet: a corpus you can cite, with versions, with cuts you can argue with. OLMo, starting 1 February 2024, paired public training code, public weights, and that corpus story.

Neither is “the internet, but legal.” Both are better than a shrug.

## RedPajama as a reaction to February

LLaMA’s paper named source categories and token budgets, not a downloadable mix. After the 3 March leak (`llama-february-2023`), a lot of people wanted a clean-room Llama. Together, with Ontocord.ai, ETH DS3Lab, Stanford CRFM, Hazy Research, and MILA Québec, shipped RedPajama-Data-1T as that attempt. The 17 April post puts the pile at over 1.2 trillion tokens and about 5 TB unzipped: CommonCrawl, C4, GitHub, books, arXiv, Wikipedia, StackExchange — a public recipe lined up against the LLaMA paper’s table (878B CommonCrawl in their column, and so on). Open-LLaMA and other trains sat on it. Quality versus Meta’s mix was the expected disappointment. The point was the recipe.

A recipe is not permission from every site in CommonCrawl. The bet was transparency over purity. The Hugging Face dataset card still says “clean-room, fully open-source implementation of the LLaMa dataset.” “Fully open-source” here means the *recipe and the dump*, not OSI magic on every token.

## Dolma’s versions, and OLMo as the pair

Ai2’s 18 August 2023 post released Dolma as a 3-trillion-token mix of web, papers, code, books, and encyclopedic text, on the Hub, under Ai2’s ImpACT license as a medium-risk artifact. That first license is a fact people skip. A later default, Dolma 1.7 (April 2024), moved the corpus terms toward ODC-BY. OLMo 7B (1 February 2024) trained on Dolma 1.5 and shipped Apache 2.0 weights with training code and logs. OLMo 1.7–7B (17 April 2024 — the same spring day as Llama 3, a coincidence of calendars) trained on Dolma 1.7, lengthened context from 2048 to 4096, and kept the “code, data, weights, logs” honorific.

“Fully open” (`open-weight-vs-open-source`) attaches here more cleanly than it attaches to Llama 3. It is still a gradient. A data doc is not the CommonCrawl warc. A training script is not the cluster image. ImpACT versus ODC-BY versus Apache on the *model* are three instruments. Write the version.

EleutherAI’s earlier The Pile is the ancestor: a documented pile, a license mess in the details, a research culture that thought the dump should be citable. Dolma is that culture with more staff and a version table.

## What `datasets` cannot save

Hugging Face `datasets` (`datasets-tokenizers-accelerate`) will load a card. It will not make the underlying text yours. A dataset repo can be MIT for the *scripts* and silent on the *text*. That silence is the trap. If the card cites CommonCrawl, you have a CommonCrawl problem, not an MIT blessing. Shops that treat Hub dataset likes as legal review will meet a lawyer eventually.

Dedup, language ID, toxicity filters, license filters — the open-data papers spend pages here. Closed vendors do this too and do not publish the pages. If you care about what was removed, you need the pages. If you only care about a bench, you will skip them. This series would rather you read the filter section once.

## Why production still uses vendor bases

Because they are stronger, or cheaper to serve, or already in the stack. Open data is a conscience and an ablation and a regulator answer. It is not, as of this pack, the default pretrain. Fine-tunes on top of Llama / Qwen / Mistral / Gemma still dominate. Those fine-tunes have data stories too — often worse-documented than Dolma. Start with your own SFT set if you want a story you can tell.

When a regulator asks what a model saw, a Dolma citation with a version number is an answer. A Llama paper’s table is a sketch. A vendor slide that says “publicly available data” is not a corpus name.

## 2026 look

Read Together’s 17 April 2023 post, the Dolma 18 August 2023 post, the 1 February 2024 OLMo post, and the dataset card’s version table. If a secondary timeline says RedPajama landed in March, correct the month. The leak is March. The dump is April. Those are different objects, and this series exists to keep them apart.

## Sources

Together, “RedPajama… 1.2 trillion tokens,” 17 April 2023; togethercomputer/RedPajama-Data-1T. Ai2, “Dolma,” 18 August 2023; allenai/dolma version table. Ai2, “Hello OLMo,” 1 February 2024; “OLMo 1.7–7B,” 17 April 2024. EleutherAI, The Pile (ancestor). LLaMA paper data table (what RedPajama was approximating).

See: `llama-february-2023`, `bloom-and-bigscience`, `datasets-tokenizers-accelerate`, `open-weight-vs-open-source`.
