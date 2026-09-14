---
title: "Synthetic data and copyright fights"
slug: synthetic-data-and-copyright
meta_description: "The NYT sued OpenAI and Microsoft on 27 December 2023. Synthetic data is both a scarcity response and a new legal surface. Not legal advice."
tags: [copyright, synthetic-data, nyt, training-data, 2023]
era_start: 2023-12
citations:
  - "NYT2023 https://nytco-assets.nytimes.com/2023/12/NYT_Complaint_Dec2023.pdf"
  - "NYT_NEWS https://www.nytimes.com/2023/12/27/business/media/new-york-times-open-ai-microsoft-lawsuit.html"
  - "ABDIN2024 https://arxiv.org/abs/2404.14219"
status: draft
voice_check: edited
---

On 27 December 2023, The New York Times Company filed a copyright complaint in the Southern District of New York against OpenAI and Microsoft. The public PDF is 30-plus megabytes of allegation: training copies, memorized output, Bing-adjacent display, a request for statutory damages and (in the ask that made engineers sit up) destruction of datasets. It is a complaint. It is not a verdict.

The filing is still the cleanest public artifact of the fight the whole industry had been having in private: is training a fair use, a license event, or a mass infringement? And when a model emits a near-copy, is that a second wrong or the same one?

This piece will not pick a winner. Courts will. As of the last primary-adjacent check (Judge Stein denying key dismissal arguments in 2025; case ongoing), the core infringement theory was still alive. `[CITE NEEDED]` PACER opinion if you quote holdings.

## Two copies, often confused

**Training copy.** To compute gradients on an article you generally make a copy the statute can see. Labs argued this is a fair-use-style conversion, like a search index, and that outputs are new. Rightsholders argued it is a substitute for the market they sell (subscriptions, licensing, archives). The 2023–26 settlement wave (some news groups licensed; some sued; some did both in sequence) is the market voting while the law works.

**Output copy.** If the model regurgitates a paywalled paragraph, you do not need a theory of training to have a problem. The Times complaint attached long examples. OpenAI said user prompts and jailbreaks were being used to force regurgitation, and that they mitigate. Both can be true. Mitigation is not a defense you want to test on a jury with a famous paragraph.

Do not collapse these in a blog or a board memo. They fail and succeed on different facts.

## Scarcity, and the turn to synthetic

By 2024 the "we will run out of clean tokens" essay was a genre (Villalobos et al. and the various "data wall" notes — cite the specific paper if you quote a year-of-exhaustion). The practical response was already in motion: filter harder, license more, generate more.

Phi-3's report (April 2024) is a public case of synthetic-heavy training for a small model. Reasoning models generate traces and then train on the traces (DeepSeek-R1, January 2025, is unusually open about RL on self-generated chains). Web-scale labs also use models to rewrite, translate, and "clean" crawls. That can raise average quality. It can also collapse diversity: the model starts teaching itself its own average sentence.

Synthetic data does not end the copyright story. It moves it. Who owns a teacher-model's rewrite of a Times article? If the teacher saw the article, is the student a laundering pass? There is not a stable public answer. Anyone who tells you synthetic is a "get out of license free" card is selling a pipeline.

## Licenses, the other market

While dockets moved, a licensing market grew up around them. Several news groups struck deals with OpenAI, Google, or both in 2023–25 (Associated Press, Axel Springer, and others — names and terms vary; check the current press release before listing them as current). Getty and Shutterstock sold image-training access. Reddit and Stack Overflow sold dump access and then discovered their users had feelings about it. These deals do not settle fair use. They price a risk.

EU text-and-data-mining exceptions (DSM Directive 2019/790, Articles 3–4) already gave research and, with opt-out, commercial TDM a statutory hook that US law does not copy-paste. That is one reason European rightsholders leaned on opt-out registries and one reason US plaintiffs leaned on §106. Same crawl, different statute.

## Other dockets, same weather

Authors Guild-adjacent book suits, image-artist suits against Stable Diffusion hosts, code suits around Copilot and public GitHub, EU text-and-data-mining exceptions with opt-out mechanics, Japan and Singapore's more permissive research exceptions — the map is jurisdictional. A training run is global. The law is not.

Fairness to labs: "the web" was the research norm in 2018, and the 2020–22 papers cited Common Crawl the way they cited Adam. Fairness to writers: a norm among researchers is not a license, and a 2023 product with a $20 subscription is not a thesis.

Robots.txt and "do not train" meta tags arrived as a folk protocol. Some labs honor them now. Crawlers that ignored them in 2021 created the datasets that still sit under 2026 models. You cannot un-see a corpus without a retrain. That is why destruction remedies scare people, and why they get asked for.

## What a builder can do without playing lawyer

- Know what you *fine-tune* on. Your ticket dump may be cleaner than a crawl, or dirtier (PII).
- Log outputs that look like verbatim. That log is how you notice a regurgitation bug.
- Prefer licensed or first-party corpora when the product *is* the style of a publication.
- Do not promise "our model never saw X" unless you have the crawl card. You probably do not.

## Opinion

The Times filing pulled a research habit into a commercial light. Synthetic data is a technical response to scarcity and a legal response to risk. It is not a moral solvent.

Until a higher court or a statute says otherwise, treat training data as something you can explain, not something you can shrug. And treat regurgitation as a product defect today, regardless of how the fair-use argument ends tomorrow.

Memorization research (Carlini et al. and the later extraction papers) is the technical sibling of the Times examples. It does not decide fair use. It does decide whether you can honestly say "the model never stores copies." Sometimes it does, in the sloppy sense that a prompt can pull a page back out. Test for that on *your* fine-tune, not only on a newspaper the internet already argued about.
