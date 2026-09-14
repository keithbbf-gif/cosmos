---
id: mmh-29
title: "DreamBooth and textual inversion: personalization as a recipe"
slug: dreambooth-textual-inversion
series: multimodal-ai-public-history
stage: draft
status: staged
publish: false
novelty: public-record
era: "2022"
topics: [DreamBooth, textual-inversion, Ruiz, Gal]
voice_check: edited
---

# DreamBooth and textual inversion: personalization as a recipe

Gal, Alaluf, Atzmon, Patashnik, Bermano, Chechik, and
Cohen-Or's *An Image is Worth One Word* (textual
inversion, arXiv:2208.01618, 2 August 2022) and Ruiz,
Li, Jampani, Pritch, Rubinstein, and Aberman's
*DreamBooth* (arXiv:2208.12242, 25 August 2022) landed
on top of the new open denoisers like a second
explosion. The desire is ordinary: put *this* dog, *this*
face, *this* chair into new scenes. The 2022 contribution
is that the desire became a **public fine-tune recipe**
instead of a closed product feature.

Textual inversion learns a new embedding vector for a
rare token, keeping the UNet mostly still. DreamBooth
finetunes the UNet (and talks about a unique identifier
plus a class-specific prior-preservation loss so the
word "dog" does not collapse onto your dog). Both papers
are readable. Both were reimplemented immediately on
Stable Diffusion weights. The gap between PDF and Discord
was days, not years.

Why this is multimodal history, not only a trick:

- It is **few-shot adaptation of a text-to-image model**.
  The text handle is being specialized. That is a
  vision-language operation even when the user never
  says the word "language."
- It relocated **identity** into a file you could share.
  Embedding files and later LoRA files became a genre.
  Sharing them became a consent problem of its own.
- It made **overfitting visible**. A DreamBooth of a
  face that cannot turn its head is a public failure
  mode. Users learned the failure faster than a
  workshop could name it.

I will not give you a hyperparameter that "just works."
That would be a recipe blog, and it would rot. The
historical claim is smaller: August 2022 did not only
release a generalist generator. It released a generalist
that the public immediately turned into a **specializer**.
The papers are dated around the weight dump on purpose
in this set's memory, even though textual inversion's
arxiv stamp is slightly earlier. The culture needed an
open UNet to become a culture.

Prior-preservation, rare-token tricks, and the later
LoRA turn (next draft) are the technical residue. The
social residue is that "train on a dozen photos of a
person" left the research PDF and became a button. Buttons
inherit the paper's limits and none of the paper's
caution section unless someone pastes it.

---

**Stage:** draft. **Claim type:** public-record recap. This piece does
not propose a new method or a new research result.
