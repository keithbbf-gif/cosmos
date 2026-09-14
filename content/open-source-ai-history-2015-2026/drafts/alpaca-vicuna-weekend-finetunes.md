---
title: Alpaca, Vicuna, and the weekend fine-tunes
slug: alpaca-vicuna-weekend-finetunes
series: open-source-ai-history-2015-2026
status: draft
voice_check: human
reading_order: 25
word_target: 600-1800
era: "2023"
stack:
  - llama
---

# Alpaca, Vicuna, and the weekend fine-tunes

Stanford CRFM’s Alpaca post (13 March 2023) described a 7B LLaMA fine-tune on 52,000 instruction examples produced with OpenAI’s `text-davinci-003`, in the Self-Instruct style, for a cost they put near $600. The repo shipped the recipe and the data. The weights waited on Meta’s permission; a live demo stood in. LMSYS’s Vicuna (30 March 2023) fine-tuned LLaMA-13B on about 70,000 ShareGPT conversations and used GPT-4 as a judge. Around them, in the same weeks: GPT4All, Koala, OpenAssistant, Dolly (Databricks, on a different base), a Discord full of LoRAs.

This is not a biology metaphor. It is a month of public repos on a leaked base (`llama-february-2023`) plus cheap adapters (`peft-lora-adapters`).

## Alpaca’s careful half-measure

Rohan Taori and colleagues named the harms, named the cost, and did not toss 7B weights onto a public CDN on day one. That caution is part of the artifact. The data-generation prompt is part of the artifact. So is the dependence on OpenAI: the “open” assistant was distilled from a closed model’s outputs. Later license fights about using model outputs to train other models (`llama-3-1-405b`) start here, in a $600 bill.

Alpaca’s quality claim was modest and qualitative: similar to `text-davinci-003` on a certain vibe, with the usual instruction-tune failures. People heard “ChatGPT at home.” The post did not say that. The internet said that.

## Vicuna and the conversation

ShareGPT was a Chrome extension that let users publish ChatGPT transcripts. Vicuna trained on those transcripts. The data is other people’s chats with a closed model, re-hosted as a fine-tune. The eval was a closed model judging an open fine-tune. The 90 percent-of-ChatGPT figure that traveled was a LMSYS number under that judge. Treat it as a 30 March press fact, not as a law of nature.

Vicuna mattered because multi-turn data is a different object from Alpaca’s single-turn instructions. Chat is a style. Instruction is a style. The weekend crowd learned both names.

## The rest of the month

GPT4All packaged a runnable desktop object. Koala (Berkeley) was another instruction tune. Dolly (12 April) is the reminder that not every 2023 assistant sat on LLaMA: Databricks used Eleuther’s Pythia and a different license story. Open-LLaMA and RedPajama (`redpajama-dolma-open-data`) later tried to rebuild a Llama-shaped model from public data so the base itself was not a leak.

The quality spread was wide. The social fact was narrow: a person with one GPU believed they could make an assistant. Whether they could make a *good* assistant is a later, ruder question.

## What the weekends did to Meta

They created a user base for a file Meta had meant for applicants. Llama 2 (`llama-2-july-2023`) reads, in part, as an attempt to put a community license under a party that had already started. That is not a mind-read. It is a sequence: leak, fine-tunes, then a commercial-friendly license in July.

They also created a mess of cards that said “Apache 2.0” on a LLaMA derivative. The Hub’s social layer rewarded the upload. The license file did not.

## 2026 look

Instruction data from a stronger model is still how a lot of open assistants are born. The nouns changed (teacher models, distillation, R1-distill). The $600 story stayed as folklore. Read the CRFM post if you want the actual claims. Read the Vicuna repo if you want the ShareGPT dependency. Do not flatten them into one “Alpaca effect” slide.

This chapter names people and dates because the month is over-narrated. The objects are two blog posts, two repos, and a pile of LoRAs that assumed a base you were not supposed to have.

## Distillation from a closed teacher as a standing pattern

Alpaca’s $600 was a bill to OpenAI. Vicuna’s judge was OpenAI. The open assistant was a student of a closed teacher. 2025’s R1 distillations are a student of an open teacher. 2024’s Llama 3.1 405B invitation is a teacher that asked to be used. The pattern stayed. The teacher’s license changed. That change is the history.

ShareGPT as a data source is other people’s chats. Consent is a mess. The Vicuna repo is a 30 March object, not a consent seminar. A 2026 shop that scrapes a chat UI is repeating 2023. Knowing you are repeating it is the minimum.

## Dolly and the other base

Databricks’ Dolly (April 2023) on Pythia is the control: you could make a weekend assistant without LLaMA. People still used LLaMA because it was stronger. The control matters so the month is not a single-base myth.

Open-LLaMA and RedPajama trains tried to make the base itself clean. They were not as strong, at first, as the leaked file. Purity and strength traded. The trade is still the open-data chapter’s subject.

## How to read a 2023 LoRA card now

If it does not name the base, discard it. If it says Apache on a LLaMA-1 delta, discard the license line. If it has no eval except a vibe, treat it as a vibe. The month produced too many cards for reverence. It produced a habit: instruction data plus a small delta plus a Hub upload. The habit is 2026’s fine-tune industry.

## GPT4All and the desktop object

Nomic’s GPT4All (late March 2023) packaged a runnable assistant for people who did not want a trainer. It is a distribution object, like Ollama later. The month was not only papers. It was installers. Installers change who is in the room. The room after March included people who would never open a repo. That is a historical fact even if the first installers were rough.

## Sources

Stanford CRFM, “Alpaca,” 13 March 2023; tatsu-lab/stanford_alpaca. LMSYS Vicuna announcement, 30 March 2023. Self-Instruct (Wang et al.). Databricks Dolly post, April 2023.

See: `llama-february-2023`, `peft-lora-adapters`, `llama-2-july-2023`, `redpajama-dolma-open-data`.
