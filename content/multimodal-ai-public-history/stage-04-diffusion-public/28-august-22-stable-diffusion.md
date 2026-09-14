---
id: mmh-28
title: "22 August 2022: Stable Diffusion leaves the lab"
slug: august-22-stable-diffusion
series: multimodal-ai-public-history
stage: draft
status: staged
publish: false
novelty: public-record
era: "2022"
topics: [Stable-Diffusion, Stability, Runway, CompVis, RAIL]
voice_check: edited
voice_check_date: 2026-09-14
---

# 22 August 2022: Stable Diffusion leaves the lab

On 22 August 2022, Stability AI posted a public-release
note for Stable Diffusion. The CompVis repository and
Hugging Face model card for `stable-diffusion-v1-4`
carried the weights. The license file is dated the same
day: CreativeML Open RAIL-M. The recommended checkpoint
in the release note is v1.4, described as a few extra
steps from the v1.3 weights that had gone to researchers
first. Those sentences are the event.

Collaboration, as the repository states it: CompVis
(LMU Munich / the Ommer lab lineage), Stability AI, and
Runway, with compute acknowledged from Stability and
data support from LAION. The model card's training
story is unusually explicit for a celebrity file:
initialization from v1.2, 225,000 steps at 512×512 on
"laion-aesthetics v2 5+," 10% text-conditioning dropout
for classifier-free guidance. A frozen CLIP ViT-L/14
text encoder. A latent UNet. About seven gigabytes.

Why this date, not the CVPR oral, is the cultural hinge:

- **A single GPU became enough.** That is a social fact
  about who could participate. Discord, AUTOMATIC1111,
  ComfyUI, and a thousand blog tutorials are downstream
  of a memory budget, not of a theorem.
- **The license tried to be a brake and a door.** RAIL
  is not MIT. It names use restrictions. Whether those
  restrictions are enforceable is a legal argument this
  set will not settle. That a generative weight file
  shipped with a behavioral license is a 2022 public
  fact.
- **The closed 2022 papers suddenly had an open
  counterpart.** Imagen remained a PDF. This was a
  file. Comparisons became possible, unfair, and
  inevitable.

I am not going to narrate the first weekend's memes as
if they were a benchmark. I will say the weekend
happened, that artists noticed, and that the later
consent fights are about this file and its descendants
as much as they are about LAION as an index. A weight
release is not only a research communication. It is a
distribution event.

Read the model card before you read a thread. The card
is dull. Dull is the point. History that starts from
the dull page is harder to turn into a myth of a lone
lab or a lone slider.

---

**Stage:** draft. **Claim type:** public-record recap. This piece does
not propose a new method or a new research result.
