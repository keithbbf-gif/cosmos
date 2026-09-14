---
title: "Voice and realtime multimodal"
slug: voice-and-realtime-multimodal
meta_description: "GPT-4o's 13 May 2024 demo set the expectation: interruptible voice, a camera, sub-second turns. Most stacks are still a cascade."
tags: [voice, realtime, gpt-4o, multimodal, 2024]
era_start: 2024-05
citations:
  - "GPT4O https://openai.com/index/gpt-4o-and-more-tools-to-chatgpt-free/"
  - "GPT4 https://openai.com/index/gpt-4-research/"
status: draft
voice_check: edited
voice_edited: 2026-09-14
figures:
  - diagram-multimodal-pipeline
  - architecture-inference-stack
---

On 13 May 2024, OpenAI's GPT-4o demo did what live video calls had not done: the model took interruption, changed tone, and talked about what the camera saw without a "please wait while I transcribe" beat you could drive a truck through. The blog post promised an advanced voice mode in alpha, Plus first. The internet promised that every app would feel like that by Christmas.

Christmas was quieter. The expectation stayed.

<!-- ai-blog-figures:begin -->
<figure class="blog-figure">
  <img src="../assets/diagram-multimodal-pipeline/fig-02-multimodal-pipeline.svg" alt="Generic multimodal fusion pipeline across text, vision, and audio" width="1200" loading="lazy" />
  <figcaption><strong>Figure 1.</strong> Multimodal products align encoders, fuse in a shared core, then decode to text or media.</figcaption>
</figure>

<figure class="blog-figure">
  <img src="../assets/architecture-inference-stack/diagram.svg" alt="Generic LLM inference serving stack" width="1200" loading="lazy" />
  <figcaption><strong>Figure 2.</strong> Client request through gateway, scheduler, and workers to streamed tokens.</figcaption>
</figure>

<!-- ai-blog-figures:end -->

## Cascades, and why you can hear them

The 2010s voice stack is a pipeline: ASR (Whisper-class, in the 2023 wave), a text model, TTS. Each stage adds latency and drops information. ASR throws away tone. TTS invents a new one. The text model never hears the sigh.

A "native audio" model takes spectrograms or audio tokens in and emits audio tokens out, with text as a sidecar or not at all. That is what the May 2024 demo *implied*. Vendors have been uneven about saying which they run in production. Early ChatGPT voice (2023–24, before 4o) was a cascade and sounded like one: you finished the sentence, waited, a new voice started.

If you are building, measure time-to-first-audio and barge-in. Users will forgive a wrong fact longer than they forgive a 2.5-second pause after "wait, no."

## What realtime actually demands

**Turn-taking.** Humans overlap. A naive VAD (voice activity detector) cuts people off or waits forever in a noisy kitchen. This is a product problem with 20 years of telephony literature. LLM teams keep rediscovering it.

**State.** A voice session is not a stateless HTTP POST. You need the last 90 seconds, the tool result, the fact that the user is now pointing the camera at a different label. That state is where privacy incidents live.

**Tools.** "What's on my calendar" is a function call in the middle of a spoken sentence. The model must pause, fetch, and resume without sounding like a hold message. Most 2024–25 assistants failed here and covered it with a filler earcon.

**Cost.** Audio tokens are fat. Always-on listening on a phone is a battery and a consent dialog. Always-on listening in a home is a regulatory object (EU, US state wiretap-ish statutes — talk to counsel; do not take this sentence as a map).

## Whisper, the unsung front door

OpenAI's Whisper (21 September 2022) is why a lot of 2023 voice demos existed at all. A reasonably accurate, multilingual ASR you could run locally or call as an API. The cascade became cheap. Podcast transcription, meeting notes, subtitle farms — those products are Whisper-shaped even when the logo says something else. GPT-4o did not make Whisper obsolete. It made the *visible* pause obsolete, when the vendor actually ran audio end-to-end.

The 2023 ChatGPT voice mode (September 2023, Plus) was Whisper plus a chat model plus a TTS (some of it from the "voice engine" research OpenAI showed and then treated cautiously because of cloning risk). Users liked it. They also talked over it and got clipped. That is the barge-in bug in the wild.

## Everyone else's 2024–26

Google had been in the assistant business for a decade and still had to re-fit Gemini into a conversational live mode. Apple's Siri rebuild, announced in pieces across 2024–25, is the conservative version: on-device where possible, delayed where Apple would not ship a hallucination into Messages. `[CITE NEEDED]` for which Siri features actually reached which OS version in your reader's market — Apple's staggered ships are easy to get wrong.

Open-weight voice is behind text. There are Whisper-class ASRs and a growing set of TTS and speech-to-speech projects. Few of them match a frontier demo on barge-in and tool use at once. That gap is an opportunity if you own a narrow domain (warehouse floor, clinic check-in) and a curse if you promised "GPT-4o at home."

Realtime APIs (OpenAI's, and the similar sockets from others) are the 2025 plumbing: a WebSocket, a session object, the ability to inject tool results. They are also how you accidentally stream a patient's name to a log you did not need.

## Failure modes that are not cute

Voice cloning. ElevenLabs and the 2023–25 clone market made "a voice that sounds like you" a consumer SKU. Labs added consent gates and watermark experiments (see SynthID in the authenticity piece). Scams did not wait for the gates.

Emotion theater. A model that sounds empathetic will be used as a therapist. Some of that is fine. Some of that is a crisis line with no license. If you ship a warm voice, you ship a duty to refuse and to point at human help. The text box had this problem. The voice box has it louder.

Kids. A realtime multimodal toy is a recording device. Treat it like one.

Latency budgets worth writing down: under ~300 ms to first audio feels like a person starting to speak; over ~800 ms feels like a call center. Those numbers are telephony folklore, not a paper, so treat them as design targets and measure your own. A beautiful 4o-class voice that starts at 1.4 seconds will lose to a dumber cascade that starts at 250 ms. Users vote with hangups.

## Opinion

The May 2024 demo was a latency and presence demo, not a knowledge demo. That is why it landed. People already believed GPT-4 was smart enough. They did not believe a computer could *keep up*.

If you ship voice in 2026, keep up first. Correctness second, on a path that can fall back to text and a citation. A warm, fast, wrong answer is a more efficient way to lose trust than a slow page of Markdown.
