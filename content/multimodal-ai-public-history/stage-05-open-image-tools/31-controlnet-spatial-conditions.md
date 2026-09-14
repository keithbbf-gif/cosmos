---
id: mmh-31
title: "ControlNet: edges, poses, and a second encoder"
slug: controlnet-spatial-conditions
series: multimodal-ai-public-history
stage: draft
status: staged
publish: false
novelty: public-record
era: "2023"
topics: [ControlNet, Zhang, Canny, OpenPose]
voice_check: edited
voice_check_date: 2026-09-14
---

# ControlNet: edges, poses, and a second encoder

Zhang, Rao, and Agrawala's *Adding Conditional Control to
Text-to-Image Diffusion Models* (arXiv:2302.05543, 10
February 2023; later ICCV) is the paper that made "draw
the edges first" a default. Clone the UNet encoder into a
trainable copy. Lock the original weights. Connect with
zero-initialized convolutions so training does not wreck
the locked generator on day one. Feed the clone a spatial
condition: Canny edges, depth, normals, OpenPose skeletons,
scribbles, segmentation maps. The text prompt still works.
The map decides where things sit.

The public artifact was immediate: code, ControlNet
checkpoints for popular conditions, and UI tabs. For a
year you could not look at an open image-generation
screenshot without a pose stick-figure in the corner.
That is not a joke about users. It is evidence that
**spatial control was the missing handle**. Text is bad
at "the cup is two inches left of the lamp." An edge map
is not.

Why it belongs on a vision-language timeline:

- It is a **multimodal conditioner that is not a
  sentence**. The second modality is a tensor aligned
  with the image grid. Language shares the stage.
- It rehabilitated **classical vision outputs** (Canny,
  1986; OpenPose) as interfaces. Old tools became new
  prompts.
- It is composition again. The locked Stable Diffusion
  is a part. ControlNet is an adapter with a spatial
  opinion.

T2I-Adapter and other cousins landed in the same season.
This draft keeps ControlNet as the named public object
because its zero-convolution story and its checkpoints
were the ones most widely rerun. A recap is allowed to
pick a representative. It should say so.

Limits that showed up in public use: over-constraint
(the model obeys the edges and loses lighting), pose
errors that look like horror-film joints, and a
temptation to treat ControlNet as truth. A depth map
from a monocular estimator is an opinion. The UNet will
treat it as geometry anyway.

If August 2022 was "type a sentence," February 2023 was
"type a sentence and pin the layout." The second
sentence is how a lot of professional use actually
happened.

---

**Stage:** draft. **Claim type:** public-record recap. This piece does
not propose a new method or a new research result.
