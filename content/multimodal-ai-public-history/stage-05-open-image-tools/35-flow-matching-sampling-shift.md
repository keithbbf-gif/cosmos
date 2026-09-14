---
id: mmh-35
title: "Flow matching: a different ODE story in public"
slug: flow-matching-sampling-shift
series: multimodal-ai-public-history
stage: draft
status: staged
publish: false
novelty: public-record
era: "2022-2024"
topics: [flow-matching, Lipman, rectified-flow, Liu]
voice_check: edited
voice_check_date: 2026-09-14
---

# Flow matching: a different ODE story in public

Lipman, Chen, Ben-Hamu, Nickel, and Le's *Flow
Matching* (ICLR 2023, arXiv:2210.02747) and Liu,
Gong, and Liu's *Rectified Flow* (2022–2023) are
the public papers that let people say "we are not
exactly doing DDPM anymore" without leaving the
continuous-time generative family. Train a network
to match a velocity field that pushes noise to
data along (often straight) paths. Sample by
integrating an ODE. Fewer steps become a design
goal instead of a distillation afterthought.

I am not going to teach the derivations. Other
people already did, in public, at length. The
historical fact is that **2023–2024 open image
models started speaking this dialect**. Stability's
SD3 paper (Esser, Kulal, Blattmann, et al.,
arXiv:2403.03206, March 2024) discusses rectified
flow objectives. Later open checkpoints advertised
few-step sampling as a feature, not a hack. The
consumer slider labeled "steps" changed meaning
under the user's hand.

Why this belongs next to CLIP and latent
diffusion:

- It is a reminder that **the 2020 DDPM tutorial
  was a beginning, not a canon**. The field kept
  rewriting the path from noise to image.
- It is mostly **architecture-agnostic**. UNets
  and DiTs can both be trained this way. The
  sampling-shift is a training-and-integrator
  shift.
- It created a new way to be confused. A
  "diffusion model" in 2024 casual speech might
  be a flow model. Casual speech is not a
  citation. This draft exists so a reader
  notices the fork.

Consistency models (Song et al., 2023) are a
neighbor: distill or train for few-step maps.
I will not flatten them into flow matching.
They share a desire (cheap sampling) and not
always a math.

If August 2022 made diffusion runnable, 2023–
2024 tried to make it **fast**. Speed is not a
footnote. Speed decides who uses the model
interactively. Interactive use decides which
failure modes get famous. Famous failure modes
decide the next paper. That loop is public even
when the loss equation is not dinner-table
talk.

---

**Stage:** draft. **Claim type:** public-record recap. This piece does
not propose a new method or a new research result.
