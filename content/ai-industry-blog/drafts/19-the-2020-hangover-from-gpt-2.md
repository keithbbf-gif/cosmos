---
title: "The 2020 hangover from GPT-2"
slug: the-2020-hangover-from-gpt-2
meta_description: "January 2020 did not start from zero. GPT-2's staged release, BERT, and T5 were already in the room when Kaplan and GPT-3 arrived."
tags: [gpt-2, bert, 2019, 2020, staged-release]
era_start: 2020-01
citations:
  - "RADFORD2019 https://openai.com/index/better-language-models/"
  - "DEVLIN2018 https://arxiv.org/abs/1810.04805"
  - "RAFFEL2020 https://arxiv.org/abs/1910.10683"
  - "KAPLAN2020 https://arxiv.org/abs/2001.08361"
status: draft
voice_check: edited
---

On 14 February 2019, OpenAI posted *Better Language Models and Their Implications* and held back the 1.5-billion-parameter GPT-2 checkpoint. They released a 124-million-parameter tease, then larger slices through the year, and the full model in November 2019. The stated reason was misuse: fluent propaganda, spam, impersonation. The stated method was "staged release." By 1 January 2020 that experiment was already a year old, and the field was already split about whether it had taught anyone anything.

This pack starts on that date on purpose. The transformer breakout did not begin with ChatGPT. It began with a pile of 2018–19 papers that 2020 then industrialized.

## What was already on disk

BERT (Devlin et al., 11 October 2018) had made "pretrain, then fine-tune" the default for NLP. Bidirectional, encoder-only, a weekend of GLUE climbing. Every 2019 startup that sold "NLP as a service" was a BERT wrapper with a better landing page. T5 (Raffel et al., 23 October 2019) recast every text problem as text-to-text and showed that a big encoder-decoder plus a cleaned crawl (C4) beat a lot of clever task heads. XLNet, RoBERTa, ALBERT — the leaderboard year. Useful. Also a trap. People learned to chase SuperGLUE points that GPT-3 would later shrug at.

GPT-2 was the other parent: decoder-only, trained to write the next token, no task head. The samples were the product. People who only remember the "unicorn" press miss the engineering fact. A 1.5B model, openly discussed, with a public smaller sibling, was already good enough for story spam and already bad enough that OpenAI's staged-release blog became a template for later "we will not release weights" arguments.

Google, Facebook, and a long list of universities kept publishing checkpoints. Hugging Face's `transformers` library (2018–19) made those checkpoints a `from_pretrained` call. That library, more than any lab blog, is why January 2020 researchers were not starting from a GitHub of random training loops.

## What staged release actually did

It bought OpenAI a year of press and a reputation as the lab that thought about release. It did not stop the 1.5B file from existing elsewhere; similar models were trained. It did not produce a public, measured harm reduction. The 2019–20 debate (Grover detectors, "AI-generated news" scare pieces, the first detection arms races) was mostly qualitative. That vacuum is why 2023–26 authenticity work (C2PA, SynthID) had to start from standards, not from the GPT-2 playbook.

It also trained the press to treat a language-model release as a safety event. That habit helped later, when GPT-4's system card existed. It also licensed a style of announcement where "we didn't ship the file" stands in for "we measured the harm." Those are different sentences.

## January 2020, the actual room

Kaplan's scaling-laws paper (23 January 2020) lands in a field that already believes pretraining works and is arguing about *how to publish*. GPT-3 (28 May) and the API (11 June) settle the argument in one direction: do not publish the 175B file; sell the completions. BERT-style fine-tunes do not die. They become the cheap path for classification while the expensive path becomes few-shot davinci.

If you skip 2018–19 you will misread 2020. You will think few-shot was a miracle instead of a bet that scale would make task heads optional. You will think "open vs closed" started with Llama. It started with GPT-2's missing checkpoint and BERT's public one, in the same eighteen months.

## The other 2019 files people actually ran

ELECTRA, DistilBERT, and the "tiny and fast" race were already a product line for mobile and search ranking. That line did not die in 2020. It became the cheap classifier sitting in front of the expensive davinci call — the first mixture-of-models, before anyone used the phrase. If your 2026 router has a small encoder for "is this even a question we should spend money on," you are still in that 2019 job.

Common Crawl plus WebText plus Books3-class mixes were already the unspoken corpus. The later lawsuits (see the copyright draft) are about a habit that predates GPT-3. GPT-2's paper was blunter about WebText than a lot of 2023 blogs were about their own stews.

Detection, 2019-style: Grover (Zellers et al., 2019) and GLTR tried to spot machine text before the text was good. They worked until the generators moved. That cycle is the same one SynthID and classifiers are still in. Starting the authenticity story in 2024 is how you miss the scar.

## What did not survive

The GLUE-era career path. A 2020 PhD who only fine-tuned BERT for another leaderboard arrived at 2023 interviews speaking a dead dialect. The skills that transferred were data hygiene, eval honesty, and knowing when a metric was saturated. The skills that did not were "design a clever classification head."

Also gone: the idea that 1.5B was "too big to release." By 2023 a 7B chat model was a weekend finetune. The 2019 threshold aged like a software license.

## Opinion

GPT-2's hangover is a release-policy hangover. The science of 2018–19 was solid. The publication politics were improvisational. 2020 solved distribution (the API) without solving measurement of misuse. We are still in that gap.

Read the February 2019 post before you write a 2026 "responsible release" paragraph. Ask what they measured, not what they withheld.
