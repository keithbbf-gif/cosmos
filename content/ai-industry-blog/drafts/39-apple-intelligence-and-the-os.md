---
title: "Apple Intelligence and the OS bet"
slug: apple-intelligence-and-the-os
meta_description: "WWDC 10 June 2024: on-device models, Private Cloud Compute, a delayed Siri. The OS is the product, not the chat portal."
tags: [apple, on-device, pcc, 2024, 2025]
era_start: 2024-06
citations:
  - "WWDC2024 https://www.apple.com/newsroom/2024/06/introducing-apple-intelligence-for-the-iphone-ipad-and-mac/"
  - "PCC https://security.apple.com/blog/private-cloud-compute/"
  - "ABDIN2024 https://arxiv.org/abs/2404.14219"
  - "AI_181 https://www.apple.com/newsroom/2024/10/apple-intelligence-is-available-today-on-iphone-ipad-and-mac/"
status: draft
voice_check: edited
figures:
  - topology-open-vs-closed-deployment
  - diagram-multimodal-pipeline
---

On 10 June 2024, Apple's WWDC newsroom post introduced Apple Intelligence: writing tools, a notification summary, a more visual Siri, an image playground, and a split that mattered more than the demos. A small model on the device. A larger model in what they called Private Cloud Compute, on Apple silicon in a data center they claimed you could inspect more than a typical VM. The first consumer slice landed 28 October 2024 with iOS 18.1 / iPadOS 18.1 / macOS Sequoia 15.1 (US English, device cuts attached). Later languages and the deeper Siri work slipped into 2025. The internet had a good time. The architecture still deserves a sober look.

This is the consumer-OS version of the small-models draft. Phi-3 (April 2024) and Llama 3.2 1B/3B (25 September 2024) are the open cousins. Apple's difference is distribution: a billion devices and a review process that will kill a feature rather than ship a public hallucination into Messages.

<!-- ai-blog-figures:begin -->
<figure class="blog-figure">
  <img src="../assets/topology-open-vs-closed-deployment/infographic-topology.svg" alt="Open-weight file deployment versus closed API topology" width="1200" loading="lazy" />
  <figcaption><strong>Figure 1.</strong> Open weights shift spend to your hardware; closed APIs shift it to vendor meters — controls can be shared.</figcaption>
</figure>

<figure class="blog-figure">
  <img src="../assets/diagram-multimodal-pipeline/fig-02-multimodal-pipeline.svg" alt="Generic multimodal fusion pipeline across text, vision, and audio" width="1200" loading="lazy" />
  <figcaption><strong>Figure 2.</strong> Multimodal products align encoders, fuse in a shared core, then decode to text or media.</figcaption>
</figure>

<!-- ai-blog-figures:end -->

## What they actually claimed

On-device first. If the request fits the small model, it does not leave the phone. If it does not, PCC: stateless, attested, no persistent customer data, in their security write-up (Apple Security Research, *Private Cloud Compute*, 2024). Independent researchers will argue about how closed the attestation story is. `[CITE NEEDED]` before you repeat a specific audit. The *product* claim is the interesting one: a consumer company admitted that not every token should go to a frontier API.

ChatGPT appeared as an optional escalation, behind a permission, with OpenAI as a named third party. That is a routing diagram, not a conversion to "Apple is an OpenAI wrapper." The wrapper is the OS. The model is a component. Most of this pack's vendors reversed that.

## Hardware as a model card

Apple Intelligence's device cut (iPhone 15 Pro and later, M-series Macs, in the 2024 telling) is a RAM and NPU cut. A 7B-class 4-bit model wants memory the SKU ladder does not give every phone. That is why "on-device for everyone" is a lie unless the model is tiny or the OS is willing to skip features. Llama 3.2 1B/3B exists for this reason. Phi-3 mini exists for this reason. If you spec "on-device" for an Android app, name the RAM floor or you will support a fiction.

MLX on a MacBook is how developers live in Apple's hardware without living in Apple's garden. That split — good silicon, closed assistant — is the 2025–26 developer mood.

## Why the delays were information

Summarizing notifications is easy to demo and easy to get legally and socially wrong (a missed hospital text, a joke flattened into an insult). Siri's deeper "do the thing across apps" promise is computer-use without calling it that, on a sandbox that Apple has spent a decade tightening. Of course it slipped. Computer-use (Anthropic, 22 October 2024) slipped in public as a Docker warning. Apple slipped in public as a "coming later" slide. Same class of hardness: actions plus identity plus a user who will not forgive a wrong send.

If you are copying Apple, copy the willingness to *not ship*. If you are mocking Apple, keep a list of the chat portals that shipped and then walked back a voice or a memory feature.

## What this does to the industry

It normalizes on-device as a default for the dumb 80%, which is the efficiency draft's punchline. It puts a hardware loop (NPU, RAM, thermal) in the same meeting as the model card. It makes "our assistant" a settings pane, not a URL. Google's Gemini-on-Android and the OEM NPU zoo are the other phone ecosystem doing the same fight with more model names and less control.

It also sets a privacy marketing bar that enterprise vendors now have to speak. "We never train on your data" is 2023 language. "This request did not leave the device, and here is the attestation" is 2025 language. Most enterprise RAG cannot say that. They should stop pretending the Apple sentence applies to them.

## Limits

Apple does not give you the weights. Researchers cannot LoRA the on-device model as a community. The open stack (MLX, llama.cpp on a Mac) is how tinkerers live next to Apple Intelligence without being it. A walled garden that is also a good ML laptop is a tension, not a paradox.

Siri's quality, as of this writing, is a product-by-product question. Do not freeze a 2025 review in a 2026 post without a re-check.

## Opinion

WWDC 2024 was the first time a consumer OS treated the model as a privilege-separated component instead of a destination. The delays were the honest part.

If you ship an assistant in 2026, steal the split (local / attested-cloud / named third party) and the permission prompt. Leave the playground image of a glowing Siri on the cutting-room floor.
