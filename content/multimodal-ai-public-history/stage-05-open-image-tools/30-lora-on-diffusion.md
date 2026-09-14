---
id: mmh-30
title: "LoRA on diffusion: the adapter that fit in a Discord upload"
slug: lora-on-diffusion
series: multimodal-ai-public-history
stage: draft
status: staged
publish: false
novelty: public-record
era: "2021-2023"
topics: [LoRA, Hu, adapters, Stable-Diffusion]
voice_check: edited
voice_check_date: 2026-09-14
---

# LoRA on diffusion: the adapter that fit in a Discord upload

Hu, Shen, Wallis, Allen-Zhu, Li, Wang, Wang, and Chen's
*LoRA* (arXiv:2106.09685, 2021) is a language-model paper:
low-rank adapters on attention weights, so you do not
finetune the whole stack. The multimodal historical event
is the **2022–2023 migration** of that idea onto Stable
Diffusion. Kohya's scripts, the various UI checkboxes, and
the Civitai-style file culture are public. A few megabytes
could hold a style, a character, or a badly overfit face.

This is not a claim that LoRA was invented for images. It
is a claim that **file size is a distribution channel**.
DreamBooth checkpoints were large. LoRAs were small. Small
files move. Moving files became a market, a safety
problem, and a folklore about ranks (`rank 8`, `rank 32`)
that most users never derive.

What the adapter genre changed:

- **Composition.** People stacked LoRAs. Stacking is not
  in the 2021 NLP paper as a product feature. It became
  one anyway. Sometimes it works. Sometimes it is two
  styles arguing in one UNet.
- **The meaning of "finetune."** For a year, a lot of
  public "training" on diffusion models meant LoRA. Full
  DreamBooth became the heavy option.
- **Provenance got harder.** A merged LoRA is a worse
  object to audit than a named academic checkpoint. The
  open ecosystem optimized for shareability, not for
  citations.

I am careful here because this set is novelty-safe. I am
not documenting a private trainer. I am documenting a
public migration of a 2021 method onto a 2022 open
denoiser, visible in repositories, papers that cite LoRA
for diffusion (including later SDXL fine-tune notes), and
the obvious fact that consumer UIs grew a LoRA slot.

If CLIP is a frozen encoder and CFG is a scalar, LoRA is
a **patch file for a generator**. The three of them, plus
a prompt box, were the 2023 consumer stack. Academic
papers that ignore the patch-file culture are describing
a cleaner field than the one that existed.

---

**Stage:** draft. **Claim type:** public-record recap. This piece does
not propose a new method or a new research result.
