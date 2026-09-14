---
id: mmh-readme
title: "Public multimodal AI history — staged draft set"
slug: readme
series: multimodal-ai-public-history
stage: draft
status: staged
publish: false
novelty: public-record
voice_check: edited
voice_check_date: 2026-09-14
---

# Public multimodal AI history — staged draft set

This folder is a **staged educational draft set**. It is not a textbook, not a
survey paper, and not a claim of original research.

The job is modest and specific: walk a general technical reader through the
**public record** of multimodal AI — especially vision-language models and
the diffusion systems whose papers, code, or weights actually left the lab.
The spine is three public objects:

1. **Vision-language as a task.** Captioning, visual question answering, and
   the 2019–2021 pretrained two-stream models.
2. **CLIP and its cousins.** Contrastive image-text matching at web scale,
   then the public reproductions and the frozen encoder that other papers
   treated as infrastructure.
3. **Diffusion in public.** Denoising diffusion as a 2020 paper, latent
   diffusion as a 2022 paper, and the 22 August 2022 weight release that
   turned a method into a default.

Around that spine sit the tools people actually ran (ControlNet, LoRA,
DreamBooth), the open visual-language assistants (BLIP-2, LLaVA and their
copies), and the later public video and unified-token papers. Speech models
appear only as neighbors: they are multimodal, and they changed what
"alignment between a waveform and a sentence" meant.

## What "staged" means

Every essay carries `stage: draft`, `status: staged`, and `publish: false`.
Nothing here is cleared for a homepage, a syllabus as-is, or a press quote.
A later editor can cut, merge, fact-check against the PDF, or throw a piece
out. Staging is the point. Folders are **historical stages**, not a live site.

## What "novelty-safe" means

These drafts **recap documents already in public circulation**. They do not
propose a new architecture, a new training recipe, or a new evaluation
harness. They do not describe any private system. They do not treat a blog
post as a theorem. See `NOVELTY.md`.

Where two public stories disagree, the draft names the disagreement and
stops. Dates are given as they appear on arXiv stamps, official blogs,
repository licenses, or widely reported announcements. When a date is fuzzy,
the draft says so.

## What "human voice" means here

The pieces are written as if one careful adult is walking another through a
stack of papers and release notes. Short sentences sit next to longer ones.
A checkpoint filename is allowed to be dull. A famous demo is not treated as
a plot twist. First person appears only when a judgment needs an owner.

## What this set is not

It is not a history of any private software project. It is not a vendor
brief. It is not a ranking of labs. It does not mention internal tools,
house names, or unpublished work. It does not file a patent and it is not a
novelty opinion.

## How to read

Start with `stage-01-seeing-and-saying/01-imagenet-as-a-visual-curriculum.md`,
or jump by era using `INDEX.md`. Public URLs live in `SOURCES.md`. Counts
live in `MANIFEST.md`. The novelty fence is `NOVELTY.md`.

## Stage map

| Folder | Era | What it holds |
| --- | --- | --- |
| `stage-01-seeing-and-saying` | 2012–2018 | ImageNet on-ramp, DeViSE, captioning, VQA, web captions |
| `stage-02-two-stream-pretrain` | 2019–2021 | ViT, ViLBERT family, contrastive vision without language |
| `stage-03-clip-and-align` | 2021–2022 | CLIP, ALIGN, OpenCLIP, LAION, the frozen encoder |
| `stage-04-diffusion-public` | 2020–2022 | DDPM, guidance, DALL·E/GLIDE, latent diffusion, weight day |
| `stage-05-open-image-tools` | 2022–2024 | Personalization, ControlNet, SDXL, DiT, flow |
| `stage-06-visual-language-models` | 2021–2024 | Frozen, Flamingo, BLIP-2, LLaVA, open VLMs |
| `stage-07-video-audio-unified` | 2022–2025 | Whisper, ImageBind, public video, unified tokens |
| `stage-08-data-eval-friction` | across | Benchmarks, consent fights, what this set refuses |

There are **fifty-two** numbered essays (`01`–`52`). House files are not
essays. The assignment floor was forty.

---

**Stage:** draft. **Claim type:** public-record recap. This piece does not
propose a new method or a new research result.
