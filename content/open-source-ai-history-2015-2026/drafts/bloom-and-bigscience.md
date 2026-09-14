---
title: BLOOM and BigScience
slug: bloom-and-bigscience
series: open-source-ai-history-2015-2026
status: draft
voice_check: human
reading_order: 21
word_target: 600-1800
era: "2021–2023"
stack:
  - huggingface
  - bloom
---

# BLOOM and BigScience

BLOOM (176B, July 2022) was a multilingual language model trained by BigScience, a collaboration of hundreds of researchers, on the Jean Zay supercomputer in France, with Hugging Face as a central engineering and Hub host. The paper (arXiv:2211.05100) and the model card are the public objects. The Responsible AI License (RAIL) on the weights is the legal object. This chapter is about a third path that is neither a company dump nor a leak: a workshop that tried to train a large model in public.

## What BigScience was

It was not a startup. It was not Meta. It was a research collaboration with working groups — data, tokenization, evaluation, legal — and a lot of videoconference. Hugging Face’s Hub was the filing cabinet. The French public compute was the furnace. Participants listed their names. That list is part of the artifact.

The data work (ROOTS) tried to be more documented than a typical scrape. “Tried” is doing labor. Documented is not the same as clean, and clean is not the same as licensed. The collaboration published what it could about sources. That publication is why this chapter exists. Most 2022–2024 training sets did not get a ROOTS-shaped paper.

## RAIL, not Apache

BLOOM’s license is a Responsible AI License: use is allowed with restrictions aimed at named harms. It is not OSI-approved open source in the old software sense. It is also not a non-commercial research grant. It sits on the middle rung of this series’ ladder (`licenses-that-are-not-open`). People who called BLOOM “open source” were doing the 2022 habit: open weights plus a PDF they had not compared to Apache.

The collaboration was explicit about wanting restrictions. That honesty is rarer than a 176B dump. You can disagree with RAIL and still record that they named the instrument.

## Why BLOOM did not become the default fine-tune

Timing and quality, mostly. LLaMA arrived seven months later, smaller, stronger per parameter on the English benches people actually ran, and then leaked. The weekend fine-tunes (`alpaca-vicuna-weekend-finetunes`) sat on Llama, not on BLOOM. Multilingualism was BLOOM’s point and not the English-language Twitter point.

The model still matters as a governance experiment. You can train a large LM with a public participant list, a public data paper, and a non-Apache license, and the Hub will hold it. That sentence was not obvious in 2021.

## Hugging Face’s role without swallowing the credit

The company hosted, engineered, and branded. The scientists were a crowd. A history that says “Hugging Face trained BLOOM” is a press release. A history that omits Hugging Face is a different error. The Hub as infrastructure (`hub-as-distribution`) is the accurate noun.

## 2026 look

BLOOM’s card is a time capsule: RAIL, ROOTS, a 176B dense model, a collaboration that looked like science. The default stacks moved to Llama, then Mistral, then Qwen and DeepSeek. The collaboration model did not become the industry default. OLMo and other fully open attempts (`redpajama-dolma-open-data`) took pieces of the spirit — public data docs, public training code — without always taking RAIL.

If you want objects: arXiv:2211.05100, the BLOOM card, the ROOTS paper, and the RAIL text. Read the license before you call the model open source. That is this series’ refrain and this chapter’s special case, because the authors asked you to.

## ROOTS as a data argument you can have

The ROOTS paper listed sources and filters. People argued with the list. That argument is the point. A closed mix cannot be argued with except as a vibe. BLOOM’s data story is incomplete and still more complete than a 2023 vendor blog that says “publicly available data.”

Multilingualism as a design goal — 46 natural languages plus 13 programming languages in the BLOOM card’s telling — is why the model existed. English-only benches punished it. A history that uses only those benches will call BLOOM a failure. A history that cares about the collaboration will not.

## RAIL in practice

A shop that wanted to ship BLOOM had to read a use-restriction list. Some shipped anyway and hoped. Some picked Llama 2’s community license instead, which is a different list. Some picked Mistral’s Apache. RAIL did not become the industry default. It became a cited alternative. That is a real outcome for a 2022 experiment.

## Why to keep the card bookmarked

Because students think large open models began in March 2023. BLOOM is July 2022. Because “open science” and “open source” are not the same, and this collaboration used the first on purpose. Because the Hub proved it could hold a 176B collaboration file without being a company dump. The file is still there. The default moved. Both facts stay.

## Jean Zay as a public furnace

A national supercomputer in a paper author list is a different funding story from a company cluster. BLOOM’s French compute is part of the artifact. So is the participant list. A student who thinks large models only come from one coast of one country should read the author block. Then read the RAIL. Then decide whether they still want to say open source.

## Sources

BigScience, BLOOM, arXiv:2211.05100. ROOTS corpus paper. BLOOM model card and RAIL license text on the Hub. Hugging Face blog posts on BigScience (company view; pair with the paper).

See: `hub-as-distribution`, `licenses-that-are-not-open`, `redpajama-dolma-open-data`, `llama-february-2023`.
