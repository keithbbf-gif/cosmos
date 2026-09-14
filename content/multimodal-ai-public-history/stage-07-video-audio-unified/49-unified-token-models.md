---
id: mmh-49
title: "Chameleon, Show-o, Transfusion: one sequence, two kinds of tokens"
slug: unified-token-models
series: multimodal-ai-public-history
stage: draft
status: staged
publish: false
novelty: public-record
era: "2024"
topics: [Chameleon, Show-o, Transfusion, Janus]
voice_check: edited
voice_check_date: 2026-09-14
---

# Chameleon, Show-o, Transfusion: one sequence, two kinds of tokens

The 2024 public papers that try to *stop being
a connector* have different names and a shared
restlessness. Meta's Chameleon report (May
2024) trains an early-fusion transformer on
interleaved text and image tokens (discrete
codes again). Show-o (Xie et al., 2024) mixes
autoregressive text with discrete diffusion
for images. Transfusion (Zhou, Le, Kolesnikov,
et al., 2024) mixes next-token prediction for
text with a diffusion loss for continuous
image latents in one model. DeepSeek's Janus
line (late 2024–2025 reports) separates
understanding and generation encoders while
keeping a unified LM. Emu3 (2024) is another
named discrete unification.

I group them so a reader sees a **question**,
not a leaderboard. The question: if ViT already
made images into tokens, and LMs already eat
tokens, why is the production stack still "CLIP
plus projector plus frozen LM" or "CLIP plus
UNet"? The 2024 papers answer: maybe it
should not be. Their results are mixed and
public. Their code availability is mixed and
public.

What to keep, without a fandom:

- **Early fusion versus late fusion** is an
  old 2019 argument (VisualBERT versus
  ViLBERT) at a new scale.
- **Generation and understanding fight over
  the visual tokenizer.** A codebook good for
  reconstruction is not always good for VQA.
  Janus-style splits are an admission.
- **Loss soup returns.** Transfusion's two
  losses in one model is the 2019
  proliferation instinct, now in a
  foundation-model body.

I will not declare unified models the 2025
winner. As of the public record through 2025,
the assistants most people used were still
often a composed stack, and the generators
most people ran were still often a specialist
denoiser. The papers still matter. They are
how a field talks when it is tired of parts.

If this set has a closing technical hinge,
it is here: multimodal AI, in public, is
still arguing whether the right object is a
**part list** or a **single sequence**. CLIP
and Stable Diffusion were a part-list
victory. These 2024 papers are the dissent.

---

**Stage:** draft. **Claim type:** public-record recap. This piece does
not propose a new method or a new research result.
