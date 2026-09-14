---
id: "25"
slug: dalle-2-and-unclip
title: DALL·E 2 and unCLIP
stage: 05-public-t2i
stage_title: Public text-to-image
status: draft
voice: human
novelty_safe: true
public_record_only: true
primary_public_sources:
  - "Ramesh et al., Hierarchical Text-Conditional Image Generation with CLIP Latents, arXiv:2204.06125 (April 2022)"
  - "OpenAI DALL·E 2 blog, 6 April 2022"
does_not_claim:
  - "unpublished DALL·E 2 production changes"
  - "identity with DALL·E 1 or 3"
last_reviewed: 2026-09-14
---

# DALL·E 2 and unCLIP

April 6, 2022 is a door. OpenAI showed a generator that made pictures civilians wanted to argue about, and they put a paper under it with a dry name: *Hierarchical Text-Conditional Image Generation with CLIP Latents*. The system in the paper is unCLIP. The brand on the door is DALL·E 2. I will use both, on purpose. The brand is what the waitlist felt. The paper is what the stack was.

unCLIP, in public, is a two-stage bet on CLIP’s image space.

A **prior** learns to go from a text embedding (CLIP text) to an image embedding (CLIP image). That prior can be autoregressive or diffusion; the paper discusses the choice. The point is the destination: a CLIP picture-vector that *means* the caption, approximately, without yet being pixels.

A **decoder** learns to go from that CLIP image embedding to pixels, as a diffusion model (with extra text optionally). Many pictures can share a CLIP vector. So the decoder is a one-to-many map. That is why DALL·E 2 could feel like it had a *style knob* even when you did not name a style: the same handle, different walks.

This is CLIP’s reception history turned into architecture. Draft 15 said people used CLIP as a critic. unCLIP says: **make the critic’s space the bottleneck**. If CLIP-space is a good summary of “what is depicted,” then generating in that summary should give you controllability and, they argue, some of CLIP’s robustness. I take that as a public claim, not as a law. The pictures were often stunning. The spelling was often bad. The bottleneck that helps you with “a corgi in a beret” can lose you the exact letters on the beret.

Compared to DALL·E 1, the physics changed. No public dVAE-and-transformer-over-indices story as the main event. Diffusion in the decoder. CLIP in the middle. The brand stayed so that civilians would know what to search. Historians should not stay. If you write “DALL·E used discrete tokens” without a version number, you are already wrong about April 2022.

The social object was a **research preview and a waitlist**. People posted their invites. People posted the pictures that survived the safety stack. The safety stack is part of the public object: OpenAI said they would limit certain generations. The generations that escaped still included likenesses and styles that started fights. I will not recap the fights as gossip. I will say that a waitlist is a particular kind of public — a public of screenshots, not of weights. Draft 30 is about that split.

Variations — “give me more like this picture” — made more sense once you believed in a CLIP handle. Take the image embedding of a generation, or of an upload, and decode again. The paper’s hierarchical language is not only marketing. It is a claim that **similarity lives at more than one altitude**. Altitude is a multimodal idea: text is high, CLIP-space is middle, pixels are low. A lot of later “image prompt” UI is this diagram with a nicer coat.

DALL·E 2 did not open the consumer GPU era. It opened the **conversation** era. Editors who had ignored ADM discovered they needed an opinion about generated pictures. That is a historical event even if you dislike the pictures. GLIDE had been a preprint. This was a homepage.

A novelty-safe hedge: the shipped product in late 2022 and 2023 is not guaranteed to be the April paper. Products move. The paper is the snapshot I can footnote. When I say unCLIP, I mean that snapshot.

Next: seven weeks later, another homepage, no waitlist you could really use, a frozen language model as the ears — Imagen — and a bet that the bottleneck was not CLIP-space but *language understanding*.
