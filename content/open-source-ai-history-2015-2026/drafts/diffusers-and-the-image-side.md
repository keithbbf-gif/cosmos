---
title: Diffusers and the image side
slug: diffusers-and-the-image-side
series: open-source-ai-history-2015-2026
status: draft
voice_check: human
reading_order: 22
word_target: 600-1800
era: "2022–2024"
stack:
  - huggingface
  - diffusers
---

# Diffusers and the image side

Stability AI released Stable Diffusion weights in August 2022 (CompVis / Stability / Runway’s public drop that month), with a CreativeML Open RAIL-M license and a UNet that a consumer GPU could run. The model was not a Hugging Face model. The library a lot of people used to run it, a few weeks later, was. `diffusers` took the Transformers habit — pipelines, `from_pretrained`, a Hub card — and applied it to denoising. This series is about language-model infrastructure, but the image side is why the Hub became a place non-researchers lived.

## A pipeline is a sentence

`StableDiffusionPipeline.from_pretrained(...).to("cuda")` then `.images[0]`. That is a sentence a designer could run. The library hid schedulers, VAEs, text encoders. You could unhide them. The unhiding is why researchers stayed. The hiding is why everyone else arrived.

Checkpoints on the Hub — `runwayml/stable-diffusion-v1-5` and then a flood of fine-tunes — made “a model” a JPEG of a product and a file. LoRA on UNets (`peft-lora-adapters`) made a style a 50-megabyte add-on. The social layer of the Hub (`hub-as-distribution`) grew on these files as much as on BERT.

## RAIL again

Stable Diffusion’s license is a RAIL cousin: use restrictions, not Apache. The same flattening happened. People said open source. They meant they had a `.safetensors` and a GUI. Automatic1111, ComfyUI, and a pile of Gradio Spaces were the real distribution system for a year. `diffusers` was the Python-native one.

This series will not litigate image-model training data. The public fact is that the license and the data argument traveled together, loudly, in 2022–2023, and that language-model debates inherited the nouns.

## Why a language-model history keeps this chapter

Because the Hub’s product sense was trained on diffusion users: widgets, Spaces, likes, GGUF-like unofficial mirrors, a culture of remix. When Llama fine-tunes arrived in 2023, the audience already knew how to click a card. The image side taught the website how to be popular. The language side taught it how to be gated.

ControlNet, SDXL, and later video pipelines are in-scope only as library milestones. This is not a history of generative art. It is a history of a pip package that made UNets look like BERT.

## 2026 look

`diffusers` still exists. So do UIs that never import it. So do video models that use the same Hub nouns. A shop that only does LLMs can skip the API and still needs the lesson: a pipeline object plus a RAIL license plus a social Hub is a different stack from Apache TensorFlow.

If you want objects: Stability’s 2022 announcement, the RAIL-M text, the `diffusers` README, and an early SD 1.5 card. The JPEG on the card is part of the artifact. So is the license people scrolled past.

## UIs as the other distribution system

Automatic1111’s WebUI and later ComfyUI taught millions of people what a checkpoint and a LoRA were before they heard of `transformers`. The Hub stored the files. The UIs ran them. `diffusers` was the Python-native path for people who wanted a pipeline in a script. Three distribution systems, one UNet family.

ControlNet, IP-Adapter, and the rest are adapter-era objects on the image side. They trained the Hub’s social graph to expect a small file that changes a big file. Language LoRAs arrived to an audience that already had the habit.

## Legal noise, recorded not settled

Artists sued. Companies claimed fair use. RAIL tried to name harms. This series will not settle a court. It will say: the image side made the license argument loud a year before Llama 2’s PDF. Language-model lawyers inherited nouns.

## Why a language pack still ships this chapter

Because the Hub’s product managers learned on diffusion. Because `from_pretrained` on a pipeline is the same verb. Because a 2026 multimodal Llama 4 card is an image card and a language card in one. The image side is not a detour. It is a wing of the same house.

## Schedulers as the unglamorous API

DDPM, DDIM, Euler, a pile of names. `diffusers` made the scheduler a swappable object. That is the library’s real kindness after `from_pretrained`. People who only move sliders in a UI still depend on that object. People who write a paper about a new sampler should start here, not in a UI fork.

## Sources

Stability AI, Stable Diffusion release, August 2022. CreativeML Open RAIL-M. Hugging Face `diffusers` documentation. Hub cards for SD 1.5 / SDXL as examples.

See: `hub-as-distribution`, `peft-lora-adapters`, `licenses-that-are-not-open`, `bloom-and-bigscience`.
