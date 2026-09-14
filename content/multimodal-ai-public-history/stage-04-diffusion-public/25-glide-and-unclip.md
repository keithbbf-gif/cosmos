---
id: mmh-25
title: "GLIDE and unCLIP: diffusion learns to take a sentence"
slug: glide-and-unclip
series: multimodal-ai-public-history
stage: draft
status: staged
publish: false
novelty: public-record
era: "2021-2022"
topics: [GLIDE, DALL-E-2, unCLIP, Nichol, Ramesh]
voice_check: edited
---

# GLIDE and unCLIP: diffusion learns to take a sentence

Nichol, Dhariwal, Ramesh, Shyam, Mishkin, McGrew, Sutskever,
and Chen's *GLIDE* (arXiv:2112.10741, 20 December 2021) is
the public paper that puts text into a diffusion UNet with
classifier-free guidance and also compares a CLIP-guided
sampler. The title spells out the claim: guided language-to-
image diffusion for generation and editing. A filtered
checkpoint was later released for research. That partial
release is part of the record: not the full training stack,
not nothing.

Ramesh, Dhariwal, Nichol, Chu, and Chen's *Hierarchical
Text-Conditional Image Generation with CLIP Latents* —
the DALL·E 2 paper, arXiv:2204.06125, April 2022 — is the
unCLIP diagram. A text-conditioned prior produces a CLIP
*image* embedding. A diffusion decoder paints pixels from
that embedding. The prior is the new object. The decoder
is a diffusion model that has been taught to invert CLIP
space. The product name traveled. The paper name is the
one to cite if you care what was claimed.

Two public lessons, different from DALL·E 1:

- **Diffusion, not a token transformer, is now the decoder.**
  The field's generator default is shifting in public, in
  months, not decades.
- **CLIP is no longer only a classifier.** It is a latent
  the generator aims at. That is the frozen-encoder story
  in a generative key.

What remained closed: the DALL·E 2 weights, the pair data,
the production stack. What remained open: the papers, the
product's behavior as encountered through an API and a
waitlist, and a wave of academic approximations. This set
does not reconstruct the closed stack. It records the
diagrams.

GLIDE and unCLIP also normalized **editing talk**: inpaint,
variation, "make it more like this embedding." InstructPix2Pix
will later turn editing into a paired-instruction dataset.
The 2021–2022 OpenAI papers are still closer to "condition
the sampler." Both are public. Do not merge them.

If Stable Diffusion is the open event of 2022, these papers
are the **closed-but-cited** event of the same year. A lot
of open work is a reply. Replies need a letter. GLIDE and
unCLIP are two of the letters.

---

**Stage:** draft. **Claim type:** public-record recap. This piece does
not propose a new method or a new research result.
