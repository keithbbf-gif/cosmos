---
title: Open weight versus open source
slug: open-weight-vs-open-source
series: open-source-ai-history-2015-2026
status: draft
voice_check: edited
reading_order: 41
word_target: 600-1800
era: "2015–2026"
stack:
  - licenses
---

# Open weight versus open source

![A ladder from research grants to Apache and MIT.](../assets/license-ladder/ladder.svg)

*Figure 3. Availability of a file is not the OSI test.*

**Open weight** means the parameters are a file you can download. **Open source**, in the software sense this series uses, means an OSI-approved license without field-of-use bans. A model can be one, both, or — if it is API-only — neither. The confusion is the story of 2023–2026.

The Open Source Definition is older than TensorFlow. It asks for use, study, modification, and redistribution, without field-of-use bans. Apache 2.0 and MIT pass. A research-only grant fails. A community license with an acceptable-use list and a user-count cap fails. A RAIL that forbids named applications fails. Those failures can still be good policy. They are not open source under that definition.

## Three layers, three answers

A stack can have Apache training code, a community-licensed weight file, and a scraped dataset with no license that would survive a hard look (`redpajama-dolma-open-data`). People point at the first and say the third is open. People point at the second and say the first is contaminated. Precision is boring and is the job.

TensorFlow 2015 was both: open-source code, and the “weights” people used (Inception, later official zoos) were published as part of that culture. Llama 2 was open weight, not open source. Mixtral 8x7B was both. GPT-4o is neither. gpt-oss is Apache on the weights plus a usage policy OpenAI names in the same breath (`gpt-oss-august-2025`) — a pair you should read as a pair.

Ask three questions instead of one adjective. 1. Can I download the weights? 2. What license is on those weights? 3. What do I know about the data and the training code? A yes on 1 only is open weight. A yes on 1 and an OSI-shaped yes on 2 is open-source-licensed weights (still maybe a no on 3). A yes on all three is the honorific “fully open.” OLMo tries. Llama 3 does not. Mixtral is yes / yes / no. Be precise.

## Why vendors blur

“Open source” is a compliment in engineer English. It hires. It soothes procurement. It sounds like 2015. “Open weight” sounds like a footnote. Meta’s 2023–2024 blogs said “open source.” Meta’s 5 April 2025 Llama 4 post preferred “open-weight.” Google’s Gemma 1 post said “open models” under custom terms; Gemma 4’s 2 April 2026 prose could point at an Apache file. The blur is not always malice. It is marketing meeting a word that already meant something. Hold the word.

OSI’s 2024–2025 public work on “open source AI” is an attempt to write a definition that includes data and weights. Drafts and notes exist. They are not, as of this pack, a replacement for the software definition on cards. When a card says “open source AI” pointing at an OSI-AI badge, read what the badge’s version actually required. Until a definition is both ratified and used on cards, this series keeps the old software test for the word “source” and “open weight” for the file.

## Fully open as a third noun

OLMo, some Eleuther models, some TinyLlama-class rebuilds: public code, public weights, public-ish data docs. “Fully open” is the community honorific. It is still a gradient. A data doc is not the CommonCrawl warc. A training script is not the cluster image. RedPajama and Dolma (`redpajama-dolma-open-data`) are the data half of this honorific. They are not Llama. Dolma’s own license moved — ImpACT on the first dump, ODC-BY on later versions — which is why “the Dolma license” is not a pin without a version.

## API-only as a third pole, not a villain

A closed API can be the right crate for a shop that does not want weights. This series is not a sermon against APIs. It is a history of the files. The third pole exists so the first two have something to be unlike. GPT-4o is neither open weight nor open source. That is a complete description, not an insult. DistBelief’s ghost — a great system you cannot share — returned as the API-only half of every vendor that also dumps some weights.

## 2026 look

When a slide says “open-source AI,” ask: code, weights, data, license name, gate, acceptable use. Six answers. If the speaker has one adjective, they have not opened the crate.

This chapter is the spine the intro promised. The license chapters on either side are the ribs. Read the OSI definition, the Llama 4 wording, and one Apache card in the same hour. The difference is the series.

## Sources

OSI, Open Source Definition; OSI public notes on AI, 2024–2025. Meta Llama 4 wording, 5 April 2025. Meta Llama 2–3 blog prose as contrast. Mistral Apache releases. OpenAI gpt-oss help article (Apache plus usage policy). OLMo / Eleuther public docs as “fully open” examples.

See: `licenses-that-are-not-open`, `what-a-license-actually-permits`, `intro-the-open-stack`, `redpajama-dolma-open-data`.
