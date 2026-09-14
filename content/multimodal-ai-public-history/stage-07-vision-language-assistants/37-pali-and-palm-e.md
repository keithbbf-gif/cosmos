---
id: "37"
slug: pali-and-palm-e
title: PaLI and PaLM-E
stage: 07-vision-language-assistants
stage_title: Vision–language assistants
status: draft
voice: human
novelty_safe: true
public_record_only: true
primary_public_sources:
  - "Chen et al., PaLI: A Jointly-Scaled Multilingual Vision-Language Model, 2022"
  - "Driess et al., PaLM-E: An Embodied Multimodal Language Model, 2023"
does_not_claim:
  - "unpublished Google robot deployments"
  - "that PaLM-E is a home robot"
last_reviewed: 2026-09-14
---

# PaLI and PaLM-E

Two public objects, same wider institution, different hungers.

**PaLI** (Chen et al., 2022) is a jointly scaled vision–language model with a multilingual chip on its shoulder. The public thesis I want: do not only scale the language side. Scale the **vision encoder** too, and treat many languages as first-class rather than as a CLIP-English leftover. Image–text, many tasks, a backbone that wants to be reused. This is Florence’s industrial hunger with a Google accent and a translation accent. If your history of multimodal is only English alt-text and ImageNet nouns, PaLI is a useful shove.

I will not pretend I independently verified their multilingual tables. I will say the shove was public and correct as a *direction*. The web is not English. CLIP’s public behavior is English-heavy. Anyone who shipped a product in another language already knew. A paper that makes the vision tower large *on purpose* is also a shove against a 2022 habit of treating the image encoder as a frozen CLIP you bought and the LLM as the only adult in the room.

There is a second PaLI public fact that is easy to skip if you only care about English chat: **OCR and text-in-the-image become a multilingual problem the moment you leave Latin type**. A sign in Hangul, a menu in Arabic, a form in Devanagari — these are the leftover channel from draft 01, and they are not a CLIP-English leftover. PaLI’s jointly scaled vision side is, among other things, an attempt to give that channel a backbone that was not designed only to retrieve stock photos of dogs. Whether it succeeded on any one script is a table I will not launder into a vibe. The attempt is the history.

**PaLM-E** (Driess et al., 2023) is the embodiment paper. Inject continuous observations — pixels, and in the embodied setting, other sensor streams — into a PaLM-like language model. Train so the model can talk *and* propose actions in a robot-language. The demos, in public, are tabletop-ish, impressive, and easy to overread. This is not a home robot. This is a paper that says **the same decoder that writes words can write decisions**, if you put the world into its prefix.

I want the “E” to stay embodied and not become a metaphor. Embodied, in the paper, means a robot (or a simulated one) in a loop: see, say, act, see again. That loop is a different public object from a chat upload. A chat upload has no gripper. A gripper has no “regenerate response.” People who cited PaLM-E as if it were an early GPT-4V were citing a cousin. People who cited it as if Boston Dynamics had been solved were citing a wish. The document sits between those misreadings.

Why these two share a draft: they both refuse the idea that multimodal is *only* “caption this JPEG in a chat window.” PaLI refuses the language parochialism. PaLM-E refuses the desktop parochialism. The later consumer assistants (GPT-4V, Gemini apps) mostly returned to the desktop JPEG. That return is not a verdict against robots. It is a verdict about what was shippable. The papers remain as leftover hunger.

Embodiment also forces a honesty about time. A robot’s image is not a COCO photograph. It is a frame in a closed loop. Failures cost more than a wrong CIDEr. PaLM-E’s public writing understands this more than a VQA leaderboard does. Whether the trained object understood it is a different sentence. I only have the paper.

A joint-map note:

- PaLI: jointly trained (in the public telling) at scale, vision encoder not a afterthought.
- PaLM-E: multimodal **prefixing** into an LLM, embodiment as a task mix, not only a vision–language mix.

Prefixing is the 2023 folk method. LLaVA prefixes. A lot of open VLMs prefix. Flamingo glances (cross-attends) in the stack. Prefix versus insert-xattn is a real fork. Prefix is simpler and ruder. Insert is more Flamingo. Both can work. Both can ignore the image.

I keep these papers in the series so Google is not only Imagen’s photorealism and Gemini’s December launch. The 2022–2023 public record is thicker than a product timeline. PaLI is a backbone paper. PaLM-E is a “what is a token of the world” paper. Gemini will claim natively multimodal in a way that wants both. We will read that claim against these, not against a press release alone.

Next: the paper that made the rude prefix a weekend project and a City B default — LLaVA, GPT-4 as a data engine, a linear map, visual instruction as a genre.
