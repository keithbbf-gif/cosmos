---
title: "Multimodal models arrive"
slug: multimodal-models-arrive
meta_description: "GPT-4 in March 2023 took images; GPT-4o in May 2024 made text, vision, and voice feel like one model. The stack is still glued."
tags: [multimodal, gpt-4, gpt-4o, gemini, 2023, 2024]
era_start: 2023-03
citations:
  - "GPT4 https://openai.com/index/gpt-4-research/"
  - "GPT4O https://openai.com/index/gpt-4o-and-more-tools-to-chatgpt-free/"
  - "GEMINI https://blog.google/technology/ai/google-gemini-ai/"
  - "CLAUDE3 https://www.anthropic.com/news/claude-3-family"
status: draft
voice_check: human
---

On 14 March 2023, OpenAI posted the GPT-4 research announcement. The first sentence called it a large multimodal model: image and text in, text out. The text-only endpoint opened first. Image inputs sat in a limited alpha. The bar-exam clip (GPT-4 around the top 10% on a simulated exam; GPT-3.5 around the bottom 10%) ate the press cycle. The multimodal clause was the longer-lived change.

If GPT-3 taught people to type at a model, GPT-4 started teaching them to *show* it things. A photo of a fridge. A screenshot of a failing UI. A handwritten homework set. That is a different product than a chat box, even when the chat box is the shell.

## What "multimodal" meant in 2023

Mostly: a vision encoder bolted onto a language model, trained so that picture tokens and word tokens live in a shared enough space to talk. The public did not get a full GPT-4 technical report with architecture tables. The March post is a capability and eval dump, plus a six-month adversarial-testing note. Treat missing diagrams as missing. Do not invent a block count.

Google's Gemini 1.0 (6 December 2023) was sold as "natively multimodal" from the start — text, code, audio, images, video — in a way that was partly architecture and partly a branding correction after Bard's rough year. Anthropic's Claude 3 family (4 March 2024) shipped vision on Haiku, Sonnet, and Opus and made screenshot-to-code a default demo. Meta's later Llama 3.2 vision models (25 September 2024) and Llama 4 (5 April 2025) pulled the same capability into open weights, with the usual license asterisks.

"Native" versus "bolted on" is a real training distinction and a marketing fog machine. Users cannot see your joint training run. They can see whether the model reads a chart axis or just captions "a graph." Early GPT-4 vision was already useful on documents and UI. It still hallucinated small text and invented numbers from photos. That class of error is worse than a wrong paragraph, because the photo feels like evidence.

## 13 May 2024

GPT-4o ("o" for omni) is the first time a frontier lab's demo *felt* like one model across text, vision, and voice. OpenAI's post said GPT-4-level intelligence, faster, better on images, with a voice mode to follow. The live demo — interruption, tone, a camera pointed at a desk — did more for public expectation than the bench table.

Two caveats, both public. The advanced voice path was not in everyone's hands on day one; it rolled through alpha and Plus. And "one model" in a keynote can still be a cascade in production (a speech-to-text front, a text model, a TTS tail). OpenAI later moved more of that stack on-model. Other vendors stayed cascaded because latency and safety filters are easier to manage as stages. If a vendor will not say which they run, assume a cascade. You can hear it in the pause.

Google's Gemini apps, Apple's 2024–25 Intelligence features, and a wave of "talk to your glasses" hardware all chased that May demo. Most of the hardware was not ready. The model side was close enough that product managers started writing specs with a camera in the loop.

## Precursors people skip

Flamingo (Alayrac et al., DeepMind, April 2022) already interleaved images and text in a frozen-LM-plus-perceiver design. Google's PaLI papers did similar work. GPT-4's March 2023 vision was not the first research multimodal model. It was the first one a lot of developers could call, once the alpha opened — and the first one a lot of consumers could use when GPT-4V went wider in ChatGPT (September–October 2023).

CLIP (Radford et al., January 2021) is the other parent. Contrastive image-text pretraining gave everyone a joint space. DALL·E 2 used it to generate. GPT-4-class models used related ideas to *understand*. If you skip CLIP you cannot explain 2021–24.

LLaVA and the 2023–24 open vision-language finetunes (often on Llama) put screenshot-to-JSON on a hobby GPU. They were messy. They were also how a lot of document-AI startups stopped paying a closed vision endpoint for every page.

## What got easier

Document work. A PDF is an image problem pretending to be a text problem. Tables, stamps, handwritten margin notes — OCR-plus-LM beats OCR alone, and a single multimodal model beats a brittle pipeline if you can stand the error rate.

UI work. "What is this dialog asking me?" is a support ticket. "Click the red button" is an agent (see the computer-use piece). Vision is the bridge.

Science and industry inspection. A photo of a gauge, a board, a rash. Useful, and legally radioactive. A wrong read on a rash is not a wrong haiku. Anyone shipping this into medicine or industrial safety without a human sign-off is not bold. They are underinsured.

## What stayed hard

Video is not "images, but more." Temporal binding, long clips, audio sync, cost per minute — 2024–26 video models are impressive and still bad at "what happened in minute 17, exactly." Audio-in for music and overlapping speech is its own mess.

Also hard: evals. A text bench can be a JSON file. A vision bench that is not contaminated, not English-only, and not a meme set is expensive to build. Vendor slides will show you MMMU and MathVista. Ask what the contamination check was. Ask whether the images are in the crawl.

## Opinion

Multimodal is not a feature flag. It is a claim about what counts as context. Once a camera is a legal input, your threat model includes every room the user points it at, and your UX has to say when the model is *looking* versus *guessing*.

The 2023–24 ships (GPT-4, Gemini, Claude 3, GPT-4o) made that claim ordinary. 2026 products that still treat an upload as a cute extra have not been paying attention.
