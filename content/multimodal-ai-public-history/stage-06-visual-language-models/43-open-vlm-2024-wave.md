---
id: mmh-43
title: "The 2024 open VLM wave: named weights, shared skeleton"
slug: open-vlm-2024-wave
series: multimodal-ai-public-history
stage: draft
status: staged
publish: false
novelty: public-record
era: "2023-2024"
topics: [Qwen-VL, PaliGemma, Molmo, Pixtral, Llama-3.2]
voice_check: edited
---

# The 2024 open VLM wave: named weights, shared skeleton

By late 2024 a reader could download several
visual-language models that were not LLaVA
finetunes of a 13B chat LM. Bai et al.'s Qwen-VL
(2023) and Qwen2-VL (2024) reports. Chen et al.'s
InternVL family. Wang et al.'s CogVLM. Google's
PaliGemma (Beyer, Steiner, Pinto, et al., 2024),
built on SigLIP and Gemma, with an academic-friendly
card. Ai2's Molmo (Deitke, Clark, et al., 2024),
with a public story about PixMo data. Mistral's
Pixtral 12B (September 2024). Meta's Llama 3.2
vision models (September 2024). NVIDIA's NVLM
report. DeepSeek-VL. The list will rot. The
**skeleton** is the history.

The skeleton, in public, looks like this:

1. A visual encoder (CLIP, SigLIP, or a custom
   ViT) that may now accept dynamic resolution.
2. A connector (linear, MLP, perceiver, resampler).
3. A decoder LM, often already instruction-tuned.
4. A mixture of caption data, interleaved
   documents, OCR, grounding boxes, and
   conversation.

Papers differ in which of those they emphasize.
Molmo emphasizes data transparency. PaliGemma
emphasizes a clean research baseline. Qwen2-VL
emphasizes native dynamic resolution and
document tasks. Llama 3.2 emphasizes a product
stack and a license. A recap that crowns one
winner in September 2024 is a magazine cover.

What changed versus 2023:

- **OCR and documents** became a selling point,
  not a failure mode you apologized for.
- **Grounding** (pointing, boxes) returned as
  an official head, after CLIP had made box-free
  fashionable.
- **Licenses split** the wave into "you can
  study this" and "you can ship this."

Huang, Peng, et al.'s February 2023 paper
*Language Is Not All You Need* (arXiv:2302.14045)
belongs in this neighborhood as an earlier
multimodal LM report from Microsoft Research.
This set cites it by title so a later scan
does not trip on a look-alike house word.

I will not pretend I evaluated these models
for this draft. I read cards, papers, and
release notes. That is the honest method for
a staged public history. If your use case is
a leaderboard, open the leaderboard. If your
use case is understanding the stack, the
skeleton above is the durable object.

---

**Stage:** draft. **Claim type:** public-record recap. This piece does
not propose a new method or a new research result.
