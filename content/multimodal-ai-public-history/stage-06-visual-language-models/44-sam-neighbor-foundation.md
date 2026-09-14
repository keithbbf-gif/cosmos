---
id: mmh-44
title: "Segment Anything: a neighbor foundation, not a captioner"
slug: sam-neighbor-foundation
series: multimodal-ai-public-history
stage: draft
status: staged
publish: false
novelty: public-record
era: "2023-2024"
topics: [SAM, Kirillov, masks, SA-1B]
voice_check: edited
---

# Segment Anything: a neighbor foundation, not a captioner

Kirillov, Mintun, Ravi, Mao, Rolland, Gustafson,
Xiao, Whitehead, Berg, Lo, Dollár, and Girshick's
*Segment Anything* (arXiv:2304.02643, 5 April
2023; ICCV 2023) is not a vision-language model
in the CLIP or LLaVA sense. It is a promptable
mask model: click, box, or coarse mask in; mask
out. The SA-1B dataset release and the weights
made it a **part**, the way CLIP was a part.
SAM 2 (2024) extended the story to video.

Why a multimodal history keeps a neighbor:

- **Grounding needs a noun and a region.** SAM
  became the region machine in other people's
  pipelines: Grounded-SAM, editor UIs,
  dataset generation. Language proposes.
  SAM cuts.
- **Promptable vision** is a parallel interface
  to text-to-image. Here the prompt is spatial
  and sparse. The 2023 field learned both
  interfaces in the same season (SAM in April,
  LLaVA in April, ControlNet in February).
- **SA-1B is a public data event.** A billion
  masks, automatic generation, a research
  license. Different weather than LAION, still
  a scale story.

Florence-2 (Xiao et al., 2023–2024) and
Grounding DINO (Liu et al., 2023) sit on the
same neighbor shelf: sequence-to-sequence
vision, open-vocabulary detection. They are
how "find the red cup" became a downloadable
head again after CLIP had made classification
feel box-free.

I do not want this draft to steal the VLM
stage. SAM does not answer "what is funny in
this meme." It answers "which pixels." A
history that only has chatty models forgets
that a lot of useful multimodal work is
**pointing**. Pointing is older than SAM
(referring expressions, 2010s). SAM is the
moment pointing became a foundation model
other papers would not bother to retrain.

---

**Stage:** draft. **Claim type:** public-record recap. This piece does
not propose a new method or a new research result.
