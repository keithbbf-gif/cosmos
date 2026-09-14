# Public multimodal AI history — draft series

Staged drafts about **public** multimodal AI: CLIP and the contrastive vision–language line, diffusion and the 2022 text-to-image event, and the vision–language assistants that followed.

This folder is historiography, not a lab notebook. It retells what papers, model cards, blog posts, licenses, and widely reported product launches already put on the record. It does not invent methods, claim priority, or describe any private system.

## How to read

Start at `stage-00-how-to-read/00-how-to-read-this-series.md`. Then walk the stages in order, or jump by the map below. Every file is a **draft**. Dates and numbers are taken from public artifacts and hedged when the public record is thin.

## Novelty-safe rules (non-negotiable)

- Public record only: papers, official blogs, model cards, licenses, court-visible or press-visible events.
- No unpublished architectures, no “we found,” no insider training recipes.
- No private product, no internal stack, no house names.
- When a lab did not publish weights, say so. When a number is a vendor claim, mark it as a claim.
- Do not paste copyrighted paper text. Cite, then speak in a human voice.
- Opinion is allowed when it is labeled as reading, not as evidence.

## Stage map

| Stage | Folder | What it is for |
| --- | --- | --- |
| 00 | `stage-00-how-to-read/` | How to read, what “public” means, what a draft refuses |
| 01 | `stage-01-precursors/` | Captions, VQA, embeddings, attention — before the 2021 hinge |
| 02 | `stage-02-contrastive-vl/` | CLIP, ALIGN, OpenCLIP, retrieval-as-supervision |
| 03 | `stage-03-discrete-generation/` | DALL·E 1, VQ-VAE / VQGAN, image tokens |
| 04 | `stage-04-diffusion-mechanics/` | DDPM, ADM, classifier-free guidance, latents, GLIDE |
| 05 | `stage-05-public-t2i/` | DALL·E 2, Imagen, Stable Diffusion, Midjourney, two publics |
| 06 | `stage-06-control-and-personalization/` | DreamBooth, LoRA, ControlNet, folk promptcraft |
| 07 | `stage-07-vision-language-assistants/` | Flamingo, BLIP, LLaVA, GPT-4V, Gemini |
| 08 | `stage-08-beyond-still-images/` | Whisper, video, music, ImageBind |
| 09 | `stage-09-aftermath/` | Metrics that lie, unified-model aesthetics, writing too early |

## Draft index

| # | File | Stage | One-line |
| --- | --- | --- | --- |
| 00 | `stage-00-how-to-read/00-how-to-read-this-series.md` | 00 | How these drafts are allowed to speak |
| 01 | `stage-01-precursors/01-what-multimodal-meant.md` | 01 | The word before it was a product category |
| 02 | `stage-01-precursors/02-imagenet-as-unimodal-peak.md` | 01 | Labels so good they hid their poverty |
| 03 | `stage-01-precursors/03-vectors-of-meaning.md` | 01 | Meaning as a direction, pictures invited in |
| 04 | `stage-01-precursors/04-show-and-tell-and-the-caption.md` | 01 | 2015 captions looked finished. They were not. |
| 05 | `stage-01-precursors/05-vqa-as-a-research-sport.md` | 01 | Leaderboards, banana-yellow priors, useful scars |
| 06 | `stage-01-precursors/06-devise-and-early-embeddings.md` | 01 | The unglamorous ancestor of joint space |
| 07 | `stage-01-precursors/07-attention-as-the-joint.md` | 01 | Two sequences talking |
| 08 | `stage-01-precursors/08-transformers-eat-both-modalities.md` | 01 | BERT, then ViT: same block, different tokens |
| 09 | `stage-02-contrastive-vl/09-contrastive-learning-before-clip.md` | 02 | Two views of one image, then a sentence as the second view |
| 10 | `stage-02-contrastive-vl/10-clip-the-public-paper.md` | 02 | What the CLIP paper actually claims |
| 11 | `stage-02-contrastive-vl/11-four-hundred-million-pairs.md` | 02 | A headline number and a public silence |
| 12 | `stage-02-contrastive-vl/12-zero-shot-as-a-phase-change.md` | 02 | ImageNet without ImageNet labels |
| 13 | `stage-02-contrastive-vl/13-align-florence-and-industrial-twins.md` | 02 | Other labs, same rhyme, private scrapes |
| 14 | `stage-02-contrastive-vl/14-openclip-and-the-commons.md` | 02 | Rebuilding a joint space in public |
| 15 | `stage-02-contrastive-vl/15-retrieval-not-captioning.md` | 02 | CLIP as retriever, then as critic |
| 16 | `stage-03-discrete-generation/16-dalle-1-was-not-diffusion.md` | 03 | Discrete VAE plus a transformer, same week as CLIP |
| 17 | `stage-03-discrete-generation/17-vqvae-vqgan-image-as-vocabulary.md` | 03 | Pictures turned into a codebook |
| 18 | `stage-03-discrete-generation/18-autoregressive-pictures.md` | 03 | Next-token prediction aimed at pixels |
| 19 | `stage-04-diffusion-mechanics/19-ddpm-the-slow-idea.md` | 04 | Add noise until nothing; walk back |
| 20 | `stage-04-diffusion-mechanics/20-when-diffusion-beat-gans.md` | 04 | ADM and the end of a monopoly |
| 21 | `stage-04-diffusion-mechanics/21-classifier-free-guidance.md` | 04 | The knob that made pictures pop |
| 22 | `stage-04-diffusion-mechanics/22-noise-schedules-nobody-wanted.md` | 04 | The unglamorous hinge inside the sampler |
| 23 | `stage-04-diffusion-mechanics/23-glide-and-language-on-noise.md` | 04 | OpenAI’s first serious diffusion-plus-text paper |
| 24 | `stage-04-diffusion-mechanics/24-latent-diffusion.md` | 04 | Denoise in a smaller room |
| 25 | `stage-05-public-t2i/25-dalle-2-and-unclip.md` | 05 | CLIP space as a steering wheel |
| 26 | `stage-05-public-t2i/26-imagen-and-the-language-encoder-bet.md` | 05 | A frozen LLM as the text tower |
| 27 | `stage-05-public-t2i/27-the-stable-diffusion-weights-drop.md` | 05 | 10 August and 22 August 2022 |
| 28 | `stage-05-public-t2i/28-midjourney-and-the-productization-of-taste.md` | 05 | Discord as the IDE; no paper, a look |
| 29 | `stage-05-public-t2i/29-promptcraft-as-folk-practice.md` | 05 | A craft that grew up in public, not in a lab |
| 30 | `stage-05-public-t2i/30-two-publics-api-and-weights.md` | 05 | Waitlists and wget, same year |
| 31 | `stage-05-public-t2i/31-laion-safety-and-the-dataset-fights.md` | 05 | A commons, a filter, a fight |
| 32 | `stage-06-control-and-personalization/32-dreambooth-and-textual-inversion.md` | 06 | A few photos become a word |
| 33 | `stage-06-control-and-personalization/33-lora-as-a-community-object.md` | 06 | A rank, a file, a fork |
| 34 | `stage-06-control-and-personalization/34-controlnet-and-the-return-of-the-condition.md` | 06 | Edges, pose, depth — the picture as a verb |
| 35 | `stage-07-vision-language-assistants/35-flamingo-few-shot-not-chat.md` | 07 | A frozen pair and a trained bridge |
| 36 | `stage-07-vision-language-assistants/36-blip-and-the-q-former.md` | 07 | Cheap adapters, bootstrapped captions |
| 37 | `stage-07-vision-language-assistants/37-pali-and-palm-e.md` | 07 | Scale the encoder; then put pixels in a robot paper |
| 38 | `stage-07-vision-language-assistants/38-llava-and-visual-instruction.md` | 07 | GPT-4 as a data engine; a linear map |
| 39 | `stage-07-vision-language-assistants/39-gpt-4v-as-a-public-proof.md` | 07 | September 2023: the assistant looks |
| 40 | `stage-07-vision-language-assistants/40-gemini-and-natively-multimodal.md` | 07 | A claim, a report, what we can say |
| 41 | `stage-08-beyond-still-images/41-whisper-audio-as-a-first-class-public.md` | 08 | Spectrograms, 680k hours, weights on the table |
| 42 | `stage-08-beyond-still-images/42-video-from-papers-to-sora.md` | 08 | 2022 papers, 2024 as a public event |
| 43 | `stage-08-beyond-still-images/43-music-spectrograms-and-tokens.md` | 08 | AudioLM, MusicLM, the quieter rhyme |
| 44 | `stage-08-beyond-still-images/44-imagebind-and-joint-spaces-after-clip.md` | 08 | More than two modalities in one space |
| 45 | `stage-09-aftermath/45-fid-clipscore-and-metrics-that-lie.md` | 09 | The scores that licensed a boom |
| 46 | `stage-09-aftermath/46-gato-and-the-everything-is-tokens-aesthetic.md` | 09 | A research mood that did not become the product path |
| 47 | `stage-09-aftermath/47-writing-this-history-too-early.md` | 09 | What a 2026 draft still cannot know |

Forty-nine markdown files live in this folder tree: this README plus numbered drafts **00–47** (forty-eight drafts). All numbered files are staged for review, not published as finished essays.

## Voice

Write like a person who watched the decade and kept the receipts. Short memory, concrete nouns, dates when the public record has them. No landscape-of-AI throat-clearing. If a feeling is in the draft — the waitlist, the weights drop, the Discord look — it is a public feeling, not a private memoir of a lab.

## Status

`status: draft` on every file. Stage means **editorial stage**, not a claim that the history is complete.
