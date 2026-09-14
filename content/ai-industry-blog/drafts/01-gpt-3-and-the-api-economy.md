---
title: "GPT-3 and the API economy"
slug: gpt-3-and-the-api-economy
meta_description: "May–June 2020: the GPT-3 paper, the OpenAI API, and why few-shot text became a product instead of a checkpoint."
tags: [gpt-3, api, 2020, few-shot, openai]
era_start: 2020-05
citations:
  - "BROWN2020 https://arxiv.org/abs/2005.14165"
  - "OAI_API2020 https://openai.com/index/openai-api/"
  - "KAPLAN2020 https://arxiv.org/abs/2001.08361"
status: draft
voice_check: human
figures:
  - comparison-era-capability-2020-2023-2026
  - infographic-training-inference-cost
---

On 28 May 2020, Brown and thirty-plus co-authors put a 72-page paper on arXiv: *Language Models are Few-Shot Learners*. The headline number was 175 billion parameters. The useful claim sat one layer down. You could specify a task in English, optionally with a handful of examples, and get usable output without a fine-tune.

Three weeks later, on 11 June, OpenAI opened an HTTP API. The paper was the science. The API was the product. That split — weights stay home, tokens leave the building — is the shape most of the industry still ships.

<!-- ai-blog-figures:begin -->
<figure class="blog-figure">
  <img src="../assets/comparison-era-capability-2020-2023-2026/fig-02-era-comparison.svg" alt="Side-by-side schematic of 2020, 2023, and 2026 capability framing" width="1200" loading="lazy" />
  <figcaption><strong>Figure 1.</strong> How buyers talked about “good enough” shifted by era — not interchangeable benchmark scores.</figcaption>
</figure>

<figure class="blog-figure">
  <img src="../assets/infographic-training-inference-cost/infographic-training-inference.svg" alt="Schematic of training versus inference costs in a model lifecycle" width="1200" loading="lazy" />
  <figcaption><strong>Figure 2.</strong> Training capex and serving opex dominate different parts of the lifecycle. <em>Illustrative.</em></figcaption>
</figure>

<!-- ai-blog-figures:end -->
## What actually shipped

GPT-3 was a decoder-only transformer in the GPT-2 line, scaled. The paper reports eight model sizes from 125 million parameters up to 175 billion, trained on a filtered Common Crawl mix plus books and Wikipedia. The 175B run used alternating dense and locally banded sparse attention. None of that was a secret architecture. The move was scale plus the demonstration that, past a certain size, the same model could do translation, trivia, and "use this invented word in a sentence" from a prompt.

The few-shot protocol is easy to forget now because chat UIs hide it. Zero-shot: instructions only. One-shot: one worked example. Few-shot: several. No gradient step at test time. That is the whole trick, and it is why a billing meter on tokens made sense. You were not selling a sentiment classifier. You were selling a general next-token machine that could be aimed with text.

The paper is also honest in ways the later marketing was not. GPT-3 still failed some reasoning sets. It showed "methodological issues" on datasets that likely sat in the crawl. Human raters had trouble telling model-written news from human news in a controlled test. The authors flag that last point as a social problem, not a trophy.

## The API, not the checkpoint

If you wanted GPT-2 you downloaded a file. If you wanted GPT-3 you sent `davinci` a prompt. OpenAI's 11 June 2020 post framed this as a platform: developers would compose language into software the way they already composed payments or maps. Waitlists, rate limits, and a content policy came with it. So did a new economic object — the token — that finance teams still do not quite know how to budget.

This mattered because it reset who could experiment. A fine-tune in 2019 meant GPUs, a dataset, and a week. A 2020 prototype meant a key and a Saturday. The cost of a bad idea collapsed. So did the cost of a sloppy one. People wrapped the API around search boxes, support queues, and "write my email" toys. Most of those toys were bad. A few became companies.

Closed weights were a product choice with a research alibi. The GPT-2 staged release (2019) had already argued that open checkpoints can be misused. GPT-3 made the argument operational: if the only copy of the 175B weights lives on OpenAI's side of the meter, you can revoke, filter, and charge. You also create a single point of policy and a single outage domain. Both showed up later.

## What changed after June 2020

Three things, in order.

First, "prompt" became a job. People who would have been annotators or PMMs started writing few-shot templates and A/B testing them. That craft is still with us. It is also why so many 2020–21 apps died when the model changed under them. You did not own the function. You rented its current mood.

Second, evaluation got worse while looking better. The paper already worried about contamination. Once the API was public, every new leaderboard had to answer: did this task leak into the crawl, and did the model's weekly silent update invalidate last Tuesday's score? Most teams pretended the answer was no.

Third, the rest of the field had to decide whether to compete on weights or on access. Google and Meta still published papers. Startups started publishing wrappers. The wrapper business is what people later called "the GPT wrapper," usually as an insult. Some wrappers were thin. Some were the first time a hospital or a bank would let a language model near a ticket. Insults do not ship.

## A short 2020–21 product tour

The named engines (`ada`, `babbage`, `curie`, `davinci`) were a size ladder sold as SKUs. People learned, the hard way, that `davinci` was the one that few-shot well and the one that blew the budget. `davinci-instruct-beta` (late 2021) and then the InstructGPT default (2022) were the first time the API quietly changed personality under the same product name. That habit — swap the model, keep the URL — is still how vendors ship.

Pricing in that era was dollars per thousand tokens, not per million. The unit hid how fast a chatty prompt ate money. Teams that cached embeddings (when `text-embedding-ada-002` arrived in December 2022) got a second meter. Teams that did not learned what a retry loop costs.

The first serious products were not "chat." They were classification, extraction, copy drafts, and a wave of no-code "GPT-3 writers" that Jasper and Copy.ai popularized. Those companies ate well in 2021 and then had to explain themselves when ChatGPT was free. The API economy created them. The consumer box cannibalized them.

## What did not change

The underlying bet was Kaplan's January 2020 scaling result: loss keeps falling if you buy more compute, data, and parameters in the right mix. GPT-3 is that bet made into a SKU. Architecture papers still arrived. Almost none of them displaced "make it bigger and sell the completions."

Also unchanged: the model does not know when it is wrong. Few-shot competence is not a calibrated belief. 2020 demos hid that with cherry-picked prompts. Production did not. The teams that survived the next two years treated the API as a noisy colleague, not as a database.

## Opinion

The 2020 break is not "AI became smart." It is "AI became an HTTP resource." That sounds dull next to 175 billion. It is the part that compounded. Once completions are a meter, every later fight — safety filters, copyright, evals, agent tools — happens on top of a billing relationship. Weights can be open or shut. The meter taught the industry how to charge for uncertainty.

We have been watching that meter since it appeared. The interesting question in 2026 is not whether another lab can train a 175B-class model. Plenty have. It is whether you still want to buy intelligence by the token from a single front door, or whether the 2020 shape was a temporary monopoly of convenience.
