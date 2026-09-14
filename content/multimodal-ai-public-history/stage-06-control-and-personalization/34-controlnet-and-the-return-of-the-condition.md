---
id: "34"
slug: controlnet-and-the-return-of-the-condition
title: ControlNet and the return of the condition
stage: 06-control-and-personalization
stage_title: Control and personalization
status: draft
voice: human
novelty_safe: true
public_record_only: true
primary_public_sources:
  - "Zhang, Rao, Agrawala, Adding Conditional Control to Text-to-Image Diffusion Models (ControlNet), 2023"
  - "Public ControlNet checkpoints (Canny, OpenPose, depth, etc.)"
does_not_claim:
  - "unpublished production control stacks"
  - "that ControlNet ended promptcraft"
last_reviewed: 2026-09-14
---

# ControlNet and the return of the condition

Text is a terrible way to say “the hand goes here.”

Everyone who used a 2022 generator learned this in the body. You can write `left` and get right. You can write `holding a cup` and get a cup nearby. Spatial intent is not what alt-text was for. Alt-text was for *what*, and sometimes *how it looks*, and almost never a skeleton.

ControlNet, Zhang, Rao, Agrawala, 2023, is a public admission of that failure and a fix that City B could actually train. You lock the big diffusion model. You attach a trainable copy of its encoder-side, tied with zero-initialized convolutions so the locked model does not explode on day one. You feed the copy an extra image: Canny edges, a pose stick-figure, a depth map, a scribble, a segmentation. The extra image is the condition. The sentence can stay. The sentence is no longer alone.

I like this paper because it **returns a condition the field used to have**. Older generative work was full of spatial conditions — pix2pix, SPADE, every layout-to-image paper. The 2022 boom threw a lot of that away for a text box, because the text box was the miracle. A year later the miracle was not enough. The old condition came back wearing a residual adapter and a CLIP prompt.

The public checkpoints taught the verbs:

- **Edges.** A line drawing as a law. The model fills the law with texture the prompt chooses.
- **Pose.** OpenPose-style bodies. The internet’s dance videos suddenly made sense as inputs.
- **Depth / normals.** A scene’s geometry as a law. Useful, less memeable.
- **Scribble.** The honest amateur condition. A bad drawing as a request.

Each verb is a different multimodal joint. Edges-to-image is almost image-to-image. Pose-to-image is a sparse skeleton talking to a dense UNet. In all of them, **the extra channel is not language**. That is the point of this stage. Personalization added a noun. ControlNet added a map.

Zero-initialization is the kind of detail a historian should keep because it is how the paper made finetuning *safe* for people who only had one GPU and one precious checkpoint. A method that destroys the base model is not a community object. A method that can fail closed on step zero is.

Did this end promptcraft? No. People still wrote novels in the box. They wrote novels *plus* a pose. The folk stack got taller: base checkpoint, VAE, LoRA, ControlNet, IP-Adapter, face restore, a sampler from draft 22. Illegibility grew. Power grew. The picture became a pipeline, which is how professional tools always looked, and which the 2022 miracle had briefly pretended not to be.

A research reading, labeled: ControlNet is a thesis about **where to put a new modality**. Not in the text encoder. Not only in a concatenated channel at the start (though that exists in cousins). In a locked clone that can speak at many resolutions. Whether that thesis is optimal is a 2023–2024 literature. That the thesis was *usable* is the historical fact.

I also want the humility. A pose model is only as good as the pose estimator. Garbage skeleton, garbage law. Multimodal systems fail at the *interface between* pretrained experts. ControlNet did not remove that. It made the interface a picture you can look at, which is already more honest than a sentence you hoped the model parsed.

Stage 06 is the year (and a bit) when City B taught the generator to take orders from things other than folklore. Stage 07 leaves generation as the main verb. The picture becomes an *input* again. The model talks. Flamingo first, in a paper without a chat app, then a rush of adapters, then a September 2023 assistant that looks.
