---
id: mmh-32
title: "InstructPix2Pix: edit the picture with a sentence"
slug: instructpix2pix
series: multimodal-ai-public-history
stage: draft
status: staged
publish: false
novelty: public-record
era: "2022-2023"
topics: [InstructPix2Pix, Brooks, Holynski, Efros]
voice_check: edited
voice_check_date: 2026-09-14
---

# InstructPix2Pix: edit the picture with a sentence

Brooks, Holynski, and Efros's *InstructPix2Pix*
(arXiv:2211.09800, November 2022; CVPR 2023) turns
editing into a supervised pair problem. The authors
generate teaching data: a source image, an instruction
("make it sunset"), and a target image, using GPT-3
to propose edits and Stable Diffusion (plus Prompt-to-
Prompt) to realize them. Then they train a diffusion
model that, given an image and an instruction, denoises
toward the edit. At inference there is no GPT-3 in the
loop. There is a model that has seen a lot of fake
before-and-afters.

The public charm is the interface. You do not engineer
a prompt that describes the whole new scene. You talk
to the existing picture. That is closer to how people
already talked to image tools ("remove the tourist,"
"make the sky more dramatic") than the 2022 empty-box
prompt was.

Two facts a recap should not blur:

- **The training data is synthetic.** The paper is
  honest. Errors in the data generator become styles
  of error in the editor. This is not a human-annotated
  edit corpus of the Visual Genome expense class.
- **Two guidances appear.** Image guidance and text
  guidance are separate knobs in the released model.
  Users learned a dance. The dance is applied CFG
  culture, now with two scalars.

InstructPix2Pix sits next to ControlNet without being
its rival. ControlNet pins structure with a map.
InstructPix2Pix pins an *operation* with a sentence.
Professional pipelines used both. Academic citations
used both. A history that only has "text-to-image"
and not "text-to-edit" is missing how the 2023 tools
were actually used.

I will not claim the model understands instructions
the way a person does. It associates edit-language
with pixel changes that its synthetic teacher liked.
When the instruction is out of distribution ("apply
the 19th-century printmaking workflow of…"), you see
the teacher. That visibility is useful. It keeps the
demo from becoming a mind.

---

**Stage:** draft. **Claim type:** public-record recap. This piece does
not propose a new method or a new research result.
