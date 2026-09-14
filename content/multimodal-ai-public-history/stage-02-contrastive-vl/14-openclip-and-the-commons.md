---
id: "14"
slug: openclip-and-the-commons
title: OpenCLIP and the attempt to rebuild the commons
stage: 02-contrastive-vl
stage_title: Contrastive vision–language
status: draft
voice: human
novelty_safe: true
public_record_only: true
primary_public_sources:
  - "Ilharco et al., OpenCLIP (GitHub / technical reports, LAION collaboration)"
  - "Schuhmann et al., LAION-400M, 2021; LAION-5B, NeurIPS Datasets 2022"
  - "Cherti et al., Reproducible scaling laws for contrastive language-image learning, 2022/2023"
does_not_claim:
  - "that open replicas match unreleased WIT"
  - "legal status of any URL collection"
last_reviewed: 2026-09-14
---

# OpenCLIP and the attempt to rebuild the commons

A closed dataset plus an open weight is an unstable object. People can build on it. People cannot *repeat* it. That bothered a specific kind of researcher more than it bothered a specific kind of product manager. Out of that bother came a public project with a plain name: OpenCLIP.

The idea is not subtle. Write a training codebase that looks like the CLIP paper’s recipe. Point it at a pair dataset you are allowed to distribute as a URL list. Train models in the open. Publish the curves. See whether the celebrity results were a magic scrape or a reproducible shape.

LAION-400M was the first widely used public rhyme: hundreds of millions of image–text pairs, CLIP-filtered, downloadable as metadata. LAION-5B was the later giant — billions of pairs, language slices, extra scores for watermark and NSFW in the public writeup. I will not recite their exact 5.85 billion as if I had counted. I will say: the order of magnitude became public, and with it a new ability to *be wrong in public* about what scale does.

Cherti et al.’s scaling-law paper is the adult in the room. It treats OpenCLIP training runs as a dataset about datasets. Compute, samples, scale. The claim, in the open, is that you can watch contrastive language-image learning obey the same kind of regularity language people had been drawing for GPT-like models. Whether every line on those plots is destiny I leave to the paper. The historical fact is that **the curve was drawn where other people could see the ink**.

I have a soft spot for this attempt and I do not want the soft spot to become a hymn. The commons was messy. URLs rot. Images disappear. The filter that decided what was a “good” pair was, for a long stretch, OpenAI’s CLIP. So the open dataset is not an independent measurement of the web. It is the web as seen by a closed model, then frozen into a list. If CLIP disliked a kind of picture, LAION could under-represent it. If CLIP liked watermarks or English marketing syntax, those could be over-represented. A commons with a closed critic at the gate is still a commons. It is not a state of nature.

There were also safety and legal events that belong to draft 31: takedowns, criticism of CSAM handling, dataset versions withdrawn or replaced, arguments about whether a URL list is a dataset. I will not try a verdict. I will say that OpenCLIP’s history is not only a GitHub star count. It is a lesson in what “open” costs when the web is the corpus.

Why this belongs in a CLIP stage, not only in a data stage: **OpenCLIP became the default noun for a lot of later open work.** Stable Diffusion’s public story is tangled with LAION. LLaVA’s public visual tower is a CLIP, often an OpenAI CLIP, sometimes an open cousin. When I say “CLIP-space” in later drafts I may mean the original weights or the open rhyme. I will try to say which when it matters. When a paper is sloppy about which, I will call the sloppiness out.

A human beat. Replicating a foundation model is unglamorous in the way DeViSE was unglamorous. It is logging, throughput, a loss that will not go down on a Friday. The people who did it in public gave the rest of us a way to argue with the 2021 blogs using something other than vibes. That is a civic good even when the replica is imperfect. Especially when it is imperfect. Imperfection is information.

If CLIP was a tool, OpenCLIP was a tool-and-a-mirror. The next draft is about the other thing people did with the tool: they stopped asking it to classify, and started asking it to *choose*.
