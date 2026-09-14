---
id: mmh-04
title: "Show and Tell, 2015: captioning as translation"
slug: show-and-tell-captioning
series: multimodal-ai-public-history
stage: draft
status: staged
publish: false
novelty: public-record
era: "2014-2015"
topics: [Show-and-Tell, Vinyals, NIC, COCO, captioning]
voice_check: edited
---

# Show and Tell, 2015: captioning as translation

Vinyals, Toshev, Bengio, and Erhan's *Show and Tell* (the Neural Image
Captioner; arXiv:1411.4555, CVPR 2015) is the public paper a lot of
people actually ran. An ImageNet-pretrained convolutional net encodes
the photograph. An LSTM decoder writes a sentence, trained on paired
image-caption data, especially Microsoft COCO. The authors say, in
plain language, that this is the same encoder-decoder idea that had
just started to work for machine translation.

That analogy is the education. Captioning, in this framing, is not
"understanding." It is **sequence generation conditioned on a vector**.
The photograph becomes a thought vector the way a source sentence
became a thought vector in Sutskever, Vinyals, and Le 2014. If you
already know that paper, Show and Tell is a transfer of a training
story from one community to another. If you do not, this is the moment
vision-language work stopped being a handful of retrieval tricks and
became a generator people could demo.

COCO matters as much as the net. Lin and colleagues' 2014 dataset gave
the field five human captions per image and a shared evaluation
script. BLEU, METEOR, CIDEr — the rulers are public, and they are
also a trap. A model can climb CIDEr by sounding like the reference
committee. Karpathy and Fei-Fei's parallel 2015 work, and the
associated neuraltalk code, made the demo reproducible for students
who were not at Google. Reproducibility is part of the history.
Captioning became a homework assignment.

What the 2015 papers did not solve, and did not need to pretend to
solve:

- **Hallucinated objects.** Decoders invent chairs because chairs are
  common in the caption prior.
- **Composition.** "A red cube on a blue cube" is not the same problem
  as "a dog sitting on a couch."
- **Faithfulness.** A fluent sentence can be wrong. Fluency is what
  the LSTM is good at.

Later visual-language models will still be scored, in part, on COCO
captions. That continuity is why this draft exists. When a 2023
assistant describes a screenshot, it is sitting on a task the field
named in public in 2014–2015. The architecture changed. The desire did
not: turn pixels into a sentence another human will accept.

Read Show and Tell as a **public interface definition**. Encoder in,
tokens out, leaderboard in the middle. CLIP will later offer a
different interface (two towers, a similarity). Diffusion will offer a
third (text in, pixels out). Captioning is the oldest of the three
that a journalist could see without a paper.

---

**Stage:** draft. **Claim type:** public-record recap. This piece does
not propose a new method or a new research result.
