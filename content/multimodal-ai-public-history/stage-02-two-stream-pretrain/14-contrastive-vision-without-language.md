---
id: mmh-14
title: "SimCLR and MoCo: contrastive vision before the captions"
slug: contrastive-vision-without-language
series: multimodal-ai-public-history
stage: draft
status: staged
publish: false
novelty: public-record
era: "2018-2020"
topics: [SimCLR, MoCo, CPC, contrastive]
voice_check: edited
---

# SimCLR and MoCo: contrastive vision before the captions

CLIP looks like a miracle if you have never seen a contrastive
visual loss. It is not a miracle. Oord, Li, and Vinyals' CPC
(2018), He's MoCo (CVPR 2020), Chen's SimCLR (PMLR 2020), Grill's
BYOL, and Caron's SwAV are public papers that taught vision people
to pull two views of the same image together and push other images
apart. No sentence required. The "caption" is another crop, a flip,
a color jitter.

This draft is a neighbor, not a detour. The mechanics CLIP will
publish in 2021 — a batch of pairs, a similarity matrix, a
cross-entropy that treats the right pair as the positive — are the
mechanics of a SimCLR batch, with the second view replaced by a
text tower. Once you have seen the 2020 figure, the 2021 figure is
a substitution. Substitution can still be a breakthrough. It is a
breakthrough that sits on a method the vision community had already
debugged.

What the 2020 contrastive papers contributed to the multimodal
story:

- **A public intuition for negatives.** A batch is a set of
  impostors. Bigger batches, or a memory bank, make the impostors
  harder. CLIP's 32,768-size batches (as reported in the paper) are
  an extreme of a number people were already arguing about.
- **A reason to drop labels.** ImageNet supervision was optional.
  That prepared the psychological ground for dropping ImageNet
  labels in favor of alt-text.
- **A bag of image augmentations.** CLIP's image side still uses
  crops and a standard visual pipeline. The 2020 papers are why
  those choices felt boring instead of exotic.

What they did not contribute: a vocabulary. Two crops of a dog are
still a dog. They do not name the breed, the joke, or the city.
Language is how CLIP escapes the closed set. Contrastive vision
alone can transfer well and still be mute.

I include CPC, MoCo, and SimCLR so that a later draft can say
"CLIP is contrastive" without sounding like a slogan. Contrastive
is a family. One branch stayed inside vision and fought about
whether you need negatives at all (BYOL). Another branch crossed
the modalities and became the 2021 default for open-vocabulary
recognition. Same family resemblance. Different public objects.

If you already know this literature, skip on. If you do not, read
the SimCLR figure, then the CLIP figure. The second file should
feel like a rhyme.

---

**Stage:** draft. **Claim type:** public-record recap. This piece does
not propose a new method or a new research result.
