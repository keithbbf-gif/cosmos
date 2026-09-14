---
id: mmh-24
title: "DALL·E 1: discrete tokens, a paper, and a withheld stack"
slug: dalle1-discrete-tokens
series: multimodal-ai-public-history
stage: draft
status: staged
publish: false
novelty: public-record
era: "2021"
topics: [DALL-E, Ramesh, discrete-VAE, transformer]
voice_check: edited
---

# DALL·E 1: discrete tokens, a paper, and a withheld stack

Ramesh, Pavlov, Goh, Gray, Voss, Radford, Chen, and Sutskever's
*Zero-Shot Text-to-Image Generation* (arXiv:2102.12092; the
5 January 2021 blog shares CLIP's dateline) is the first time
a wide public met text-to-image as a *named demo*. The method,
as published: a discrete VAE compresses the image; a
transformer models the joint stream of text tokens and image
codes; you sample codes and decode. The name is a pun. The
pun traveled farther than the architecture diagram.

What was public: the paper, the blog, cherry-picked and also
some systematically prompted figures, and a research
conversation about prompt sensitivity and bias. What was not
public: the full trained stack as a hobbyist weight dump.
That split is the same lesson as CLIP's locked WIT, inverted.
Here the *task* went viral and the *file* did not.

Why the draft still belongs on a diffusion timeline:

- It established **text-to-image as a consumer sentence**
  before diffusion won the open-weights race. People who
  later used Stable Diffusion already knew the desire.
- It kept **discrete generation** in the running. Parti (Yu
  et al., 2022) is a later, also mostly closed, transformer-
  on-codes system from Google. The 2021 DALL·E paper is the
  ancestor journalists could name.
- It sat next to CLIP on purpose. The same organization, the
  same week, published a matcher and a generator. The later
  unCLIP paper will marry them more tightly.

I will not narrate sample images as if they were a
benchmark. The 2021 figures are a demo genre. Demos recruit.
They also hide failure modes that a COCO FID table at least
tries to average. When the 2022 papers start quoting FID and
human preference on MS-COCO, they are answering a credibility
problem this demo created: *pretty* is not a method.

Read DALL·E 1 as a **public desire object**. The method is
real and citable. The cultural fact is that "type a sentence,
get a picture" left the specialist workshop in January 2021.
Diffusion did not invent the sentence. Diffusion, plus a
latent, plus a license, plus a 6.9 GB file, is how the
sentence became something you could run.

---

**Stage:** draft. **Claim type:** public-record recap. This piece does
not propose a new method or a new research result.
