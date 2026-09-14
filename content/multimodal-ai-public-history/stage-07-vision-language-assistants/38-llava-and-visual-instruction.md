---
id: "38"
slug: llava-and-visual-instruction
title: LLaVA and visual instruction
stage: 07-vision-language-assistants
stage_title: Vision–language assistants
status: draft
voice: human
novelty_safe: true
public_record_only: true
primary_public_sources:
  - "Liu et al., Visual Instruction Tuning (LLaVA), arXiv:2304.08485, April 2023"
  - "LLaVA-1.5 and follow-on public reports / code"
  - "Vicuna / LLaMA as the public language backbones named in the work"
does_not_claim:
  - "that LLaVA matches GPT-4V"
  - "unpublished GPT-4 data-generation prompts beyond the paper"
last_reviewed: 2026-09-14
---

# LLaVA and visual instruction

April 2023. Liu, Li, Wu, Lee. A paper with a short architecture and a loud idea. Take a CLIP visual encoder. Take an open language model (Vicuna, in the story that spread). Connect them with a **linear projection** (later, a small MLP). Train on **instruction data** that you got by asking GPT-4 to talk about images it cannot see, given captions and boxes. Release the result. Call it a Large Language and Vision Assistant.

The loud idea is not the linear map. The loud idea is **the data genre**. Visual instruction following: not “caption this” as a dataset format, but “do this with this image” in the chat format people already used for Alpaca and Vicuna. Once the format matches the product, the model *is* a little product. City B could run it. City A suddenly had open cousins.

GPT-4 as a data engine is the part I want handled carefully. The authors did not, in the public telling, feed GPT-4 the pixels. They fed it the *already-extracted language of the image* — captions, bounding boxes — and asked it to invent conversations. So the teacher is a language model imagining vision. That is a strange teacher. It is also, if you are honest about 2023, one of the only teachers you could afford. The result is a dataset that sounds like an assistant. It may hallucinate objects the boxes never named. It may be fluent about emptiness. The paper reports impressive multimodal chat. I believe the chat was impressive. I also believe the banana is yellow.

The linear map is a historical joke in the best sense. Flamingo’s gated xattn, BLIP-2’s Q-Former, and then a matrix. Sometimes the rude thing is enough if the speaker is strong and the visual tower is CLIP. LLaVA-1.5’s public follow-on made the map an MLP and improved the data mix and suddenly a lot of open VLMs were “LLaVA-shaped.” Shaped means: prefix visual tokens, instruction-tune, hope. I prefer that honesty to a new module name every month.

Why this is a hinge, not just a popular repo:

Because it **closed a loop with City A**. GPT-4 (text) invents the supervision. An open stack trains on the invention. The open stack is then compared, in the paper, to multimodal GPT-4 as a relative score. The closed model is parent and rival. That loop will define 2023–2024 open multimodal work. It is not clean. It is not independent. It is how a lot of capability actually moved.

The evaluation culture shifted with it. MMBench, MM-Vet, LLaVA-Bench, later MMMU — a sport again, but a sport of *assistants*, not of short-answer VQA only. The sport has the old vices (priors, contamination, English) and new ones (judge models grading judge-model prose). I will not tour the benches. I will say LLaVA made a bench *necessary* because a chat demo is too easy to love.

A human beat. The reason this paper felt like a weekend — it was not, not really, but it felt like one — is that the pieces were already on the table: CLIP (2021), open LLMs (2023), instruction tuning as a genre (2023), a cheap projector. The authors assembled a verb: **visual instruct**. Once a verb exists, a field can conjugate it. Video-LLaVA, LLaVA-NeXT, a hundred workshop papers. Conjugation is not bloat by itself. It is what happens when a joint is simple enough to reuse.

Limits, public: weak OCR relative to later specialists; a tendency to long, agreeable answers; a visual tower that never saw the instruction text during CLIP pretraining. The later specialist models (document VLMs, OCR-heavy stacks) are a confession of those limits. LLaVA is a generalist starting gun, not a finish.

Next: the rival/parent in product form. September 25, 2023. GPT-4 with vision. A system card. A public proof that the assistant can look — and a reminder that a proof is not a paper.
