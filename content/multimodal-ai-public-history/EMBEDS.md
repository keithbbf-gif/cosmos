# Figure embeds — SEO-ready HTML

Use paths relative to site root `content/multimodal-ai-public-history/`. Each block includes:

- Semantic `<figure>` + `<figcaption>` (citable figure numbers)
- Descriptive `alt` (accessibility + image SEO)
- Explicit `width` / `height` (layout stability)
- `loading="lazy"` and `decoding="async"` on non-hero images
- `itemprop` hooks for structured data when the page wrapper sets `itemscope` on the article

Rights: see `RIGHTS.md` (CC0 SVGs, no AI faces).

---

## Fig. 01 — Public timeline (hero)

```html
<figure class="mmh-figure mmh-figure--spread" itemprop="image" itemscope itemtype="https://schema.org/ImageObject">
  <meta itemprop="name" content="Public milestones in multimodal AI (2012–2024)"/>
  <meta itemprop="license" content="https://creativecommons.org/publicdomain/zero/1.0/"/>
  <img src="content/multimodal-ai-public-history/graphics/fig-01-public-multimodal-timeline.svg"
       alt="Timeline of public multimodal AI milestones from Show and Tell through GPT-4V and Whisper"
       width="1200" height="520" decoding="async" fetchpriority="high"/>
  <figcaption itemprop="caption"><strong>Fig. 1.</strong> Selected public doors in multimodal AI — captions and VQA, CLIP and DALL·E, latent diffusion, the Stable Diffusion weights drop, vision-language assistants, and speech models on the record. Editorial schematic; not exhaustive.</figcaption>
</figure>
```

---

## Fig. 02 — Series stage map

```html
<figure class="mmh-figure mmh-figure--column" itemprop="image" itemscope itemtype="https://schema.org/ImageObject">
  <meta itemprop="name" content="Editorial stages of the public multimodal history series"/>
  <img src="content/multimodal-ai-public-history/graphics/fig-02-series-stage-map.svg"
       alt="Flowchart of editorial stages from how-to-read through precursors, CLIP, diffusion, public T2I, control, assistants, and aftermath"
       width="960" height="640" loading="lazy" decoding="async"/>
  <figcaption itemprop="caption"><strong>Fig. 2.</strong> How this draft series is staged (folders 00–09). Stages organize reading; they are not a strict causal graph.</figcaption>
</figure>
```

---

## Fig. 03 — Contrastive joint space

```html
<figure class="mmh-figure mmh-figure--column" itemprop="image" itemscope itemtype="https://schema.org/ImageObject">
  <meta itemprop="name" content="CLIP-style contrastive joint embedding space"/>
  <img src="content/multimodal-ai-public-history/graphics/fig-03-contrastive-joint-space.svg"
       alt="Diagram of image and text encoders mapping paired samples into a shared embedding space with contrastive loss"
       width="960" height="520" loading="lazy" decoding="async"/>
  <figcaption itemprop="caption"><strong>Fig. 3.</strong> CLIP-shaped contrastive training: two encoders, one joint space, batch retrieval loss — plus common public uses that are not in the methods section.</figcaption>
</figure>
```

---

## Fig. 04 — Latent diffusion loop

```html
<figure class="mmh-figure mmh-figure--column" itemprop="image" itemscope itemtype="https://schema.org/ImageObject">
  <meta itemprop="name" content="Latent diffusion denoising loop with text conditioning"/>
  <img src="content/multimodal-ai-public-history/graphics/fig-04-latent-diffusion-loop.svg"
       alt="Schematic of latent diffusion: encoder, noisy latent, denoising U-Net with text embeddings, decoder to pixels"
       width="960" height="480" loading="lazy" decoding="async"/>
  <figcaption itemprop="caption"><strong>Fig. 4.</strong> Latent diffusion (LDM-shaped): denoise in a smaller latent room, conditioned on text — the public stack behind Stable Diffusion.</figcaption>
</figure>
```

---

## Fig. 05 — Two publics

```html
<figure class="mmh-figure mmh-figure--column" itemprop="image" itemscope itemtype="https://schema.org/ImageObject">
  <meta itemprop="name" content="API products versus downloadable model weights in 2022"/>
  <img src="content/multimodal-ai-public-history/graphics/fig-05-two-publics-api-vs-weights.svg"
       alt="Split diagram comparing gated API image products with locally runnable weight checkpoints"
       width="960" height="520" loading="lazy" decoding="async"/>
  <figcaption itemprop="caption"><strong>Fig. 5.</strong> Two publics that shared vocabulary in 2022: City A (API, waitlist, Discord) versus City B (checkpoints, local inference, community forks).</figcaption>
</figure>
```

---

## Fig. 06 — Modality fanout

```html
<figure class="mmh-figure mmh-figure--column" itemprop="image" itemscope itemtype="https://schema.org/ImageObject">
  <meta itemprop="name" content="Modalities branching from text-image joint spaces"/>
  <img src="content/multimodal-ai-public-history/graphics/fig-06-modality-fanout.svg"
       alt="Hub diagram with text-image joint space at center and branches for speech, video, music, ImageBind, and vision-language assistants"
       width="960" height="480" loading="lazy" decoding="async"/>
  <figcaption itemprop="caption"><strong>Fig. 6.</strong> After CLIP, public work fanned into speech (Whisper), video, music tokens, broader binding (ImageBind), and assistants that look — still on the public record only.</figcaption>
</figure>
```
