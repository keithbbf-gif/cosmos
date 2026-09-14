---
id: "42"
slug: video-from-papers-to-sora
title: Video, from papers to Sora
stage: 08-beyond-still-images
stage_title: Beyond still images
status: draft
voice: human
novelty_safe: true
public_record_only: true
primary_public_sources:
  - "Singer et al., Make-A-Video (Meta), 2022"
  - "Ho et al., Imagen Video (Google), 2022"
  - "Blattmann et al. / Stability, Stable Video Diffusion, 2023 (open-weight neighbor)"
  - "OpenAI Sora research preview, 15 February 2024; later public product notes"
does_not_claim:
  - "unpublished Sora architecture"
  - "that 2022 video papers were secretly Sora"
last_reviewed: 2026-09-14
---

# Video, from papers to Sora

Video is the obvious next noun after a pretty still, and it is a different physics. Time can break. Objects can flicker. A walk can slide. The 2022 papers knew this and still had to publish, because the stills had already happened.

**Make-A-Video** (Meta, 2022) and **Imagen Video** (Google, 2022) are the public research objects I want on the table first. Both are text-to-video in a diffusion world. Both, in the public telling, lean on image models and then ask time to behave. Neither handed City B a file that felt like August 22. They handed City A-of-papers a set of clips. The clips were short and astonishing and a little sick if you stared at the continuity. That sickness is the research object.

I will not flatten their methods into one cartoon. The cartoon the press used — “like DALL·E but moving” — is the cartoon I want to refuse. Temporal layers, cascaded samplers, frame interpolation, image-model priors: the stack is a stack. A still model’s joint with text does not automatically become a video model’s joint with text. The sentence now has to bind to a *duration*. “Walking” is easy to paint and hard to play.

**Stable Video Diffusion**, late 2023, is the City B neighbor: image-to-video and related tasks, weights you could poke, a continuation of the latent-diffusion city. It did not end the story. It made a file. Files, in this series, are events.

**Sora**, February 15, 2024, is a different kind of event: a research preview with clips that looked like a camera. OpenAI showed a world with duration, with a kind of physical gossip that earlier clips had lacked. The public technical language that later accompanied it talked about video generation models as world simulators — a claim, a slogan, a research report. I will not promote the slogan to a fact. I will say the *clips* were a public fact, and that they reorganized the conversation the way the avocado armchair had, with more lawyers in the room.

Architecture? Not in the way LDM is public. Treat Sora like GPT-4V: behavior public, method thin. Later reporting and a technical report exist as City A documents. They are not a GitHub. People who write “Sora is a diffusion transformer” as if they trained it are doing fan fiction unless they are citing a specific public sentence. Cite the sentence.

The ethics edge is sharper than stills. A still fake is a poster. A video fake is a *clip you can drop in a timeline*. 2024–2025 productization (Sora’s later wider release, plus a crowd of named video models from other labs) is a distribution story I will not try to finish. This draft’s job is the hinge: **2022 proved the noun, 2023 opened a file, 2024 made a preview that civilians treated as a medium.**

Understanding video — not generating it — is the quieter twin. Flamingo already ate video in 2022. Gemini’s report cares about video QA. A model that *watches* is closer to the assistant job. A model that *renders* is closer to the 2022 job. They share datasets in the ugly sense (the web is full of both) and they do not share a user. I split them on purpose. This draft is the renderer. The watcher is stage 07 with a time axis.

A human memory I will allow: the first generated clips that impressed me still felt like a GIF with a degree. Sora’s first clips felt like a take. Whether that feeling is physics or better data or a transformer over spacetime patches, I cannot say from here. The feeling is part of the public record. Feelings are allowed when they are labeled. That one is labeled.

Next: a quieter rhyme — music and audio generation, spectrograms and tokens, the year the ear got a generator and not only a transcriber.
