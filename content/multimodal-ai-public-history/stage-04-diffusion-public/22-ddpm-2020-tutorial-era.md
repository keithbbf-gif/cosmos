---
id: mmh-22
title: "DDPM, 2020: the tutorial that remade generation"
slug: ddpm-2020-tutorial-era
series: multimodal-ai-public-history
stage: draft
status: staged
publish: false
novelty: public-record
era: "2020-2021"
topics: [DDPM, Ho, Sohl-Dickstein, Nichol, ADM]
voice_check: edited
---

# DDPM, 2020: the tutorial that remade generation

Ho, Jain, and Abbeel's *Denoising Diffusion Probabilistic
Models* (NeurIPS 2020, arXiv:2006.11239) is not the first
diffusion paper. Sohl-Dickstein et al. 2015 is. Song and
Ermon's NCSN work is in the same late-2010s cluster. The
reason DDPM is the public hinge is pedagogical. The paper
gives a training loss that looks like denoising score
matching, a sampling loop a competent engineer can type, and
pictures of 32×32 CIFAR and 256×256 LSUN that made people
stop treating diffusion as a curiosity.

Nichol and Dhariwal's improved DDPMs, and Dhariwal and
Nichol's *Diffusion Models Beat GANs on Image Synthesis*
(NeurIPS 2021), turned the tutorial into a competitive
generator. Classifier guidance appears there as a way to
steer the sampler with an ImageNet classifier. The ADM
architecture (UNet, attention at certain resolutions) becomes
a reference. None of this is yet "type a sentence, get a
poster." It is **unconditional and class-conditional
pictures**, released with enough code that other labs could
play.

Why this set spends a whole draft on a paper without
captions:

- Text-to-image diffusion is DDPM plus a conditioner. If you
  skip DDPM, Stable Diffusion looks like a brand.
- The 2020–2021 papers established **step count, noise
  schedules, and UNet inductive bias** as the knobs. Later
  latent and flow papers still argue with those knobs.
- A lot of public explanation culture — blog derivations,
  "the math of diffusion" threads — is a response to DDPM's
  readability. That culture is how the method left the
  specialist circle before the weights of a text model did.

Limits that were obvious then and remain useful. Sampling is
slow relative to a GAN-forward pass. Likelihoods and FID can
disagree. 256×256 ImageNet is not a design tool. And guidance,
in the 2021 ADM form, still wanted a classifier trained on
the same space. The next draft is the trick that dropped the
classifier.

I trust DDPM as a **shared language**. When a 2024 paper says
"we train a diffusion transformer with a v-prediction loss,"
it is speaking a dialect of 2020. Readers who only met
diffusion as a product slider are meeting the dialect's
consumer interface, not the paper that made the slider
possible.

---

**Stage:** draft. **Claim type:** public-record recap. This piece does
not propose a new method or a new research result.
