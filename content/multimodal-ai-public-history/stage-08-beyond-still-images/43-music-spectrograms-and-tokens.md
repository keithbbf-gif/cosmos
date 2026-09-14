---
id: "43"
slug: music-spectrograms-and-tokens
title: Music, spectrograms, and tokens
stage: 08-beyond-still-images
stage_title: Beyond still images
status: draft
voice: human
novelty_safe: true
public_record_only: true
primary_public_sources:
  - "Borsos et al., AudioLM, 2022"
  - "Agostinelli et al., MusicLM, 2023"
  - "Huang et al. / Stability, Stable Audio public model cards (2023–)"
  - "Dhariwal et al., Jukebox, 2020 (OpenAI ancestor)"
does_not_claim:
  - "unpublished commercial music-model recipes"
  - "legal status of any training corpus"
last_reviewed: 2026-09-14
---

# Music, spectrograms, and tokens

Music generation is the rhyme nobody outside a small room wanted to hear as loudly as the pictures. The pictures had Discord. The music had a copyright industry that already knew how to lawyer, and a human ear that is crueler about time than an eye is about fingers.

The public technical rhyme is still our rhyme. **Turn the wave into a vocabulary, then write the vocabulary.** Jukebox (OpenAI, 2020) did a VQ-VAE-ish thing on audio and a transformer on the codes, years before the pretty-picture boom. AudioLM (2022) made a language-model story on semantic and acoustic tokens. MusicLM (2023) put a text condition on a music model and showed a demo that could, in Google’s public telling, follow a caption into a genre. Stable Audio, later, put a file in City B’s hand for some of the job.

Spectrograms sit in the middle like a pun. They are images. You can, and people did, throw a diffusion model at a spectrogram and invert it back to a wave. That path is real and it has a vice: a spectrogram-as-image does not know phase the way a well-designed audio tokenizer does. I will not run that argument to the end. I will say the pun is why audio belongs in a *vision–language* history at all. The field kept using eyes to hear.

Text-to-music is a multimodal joint with a nasty alignment. “A sad cello in a stairwell” is easy to imagine and hard to evaluate. FID does not exist in a form anyone loves. CLAP and other audio–text spaces try to be CLIP for ears. Listening tests are labor. So the public history is thinner: fewer leaderboards, more demo reels, more immediate legal letters. Thin does not mean small. It means I will not fake a 2022-style civilian explosion that did not quite happen.

What did happen: **the token bet stayed stronger here**. Autoregressive audio, hierarchical tokens, a language model that writes sound, survived as a default longer than autoregressive pictures survived as a popular default. Maybe because time is already a sequence. Maybe because the diffusion-on-wave literature took longer to sound good. Maybe fashion. I can live without a single cause.

Whisper and MusicLM are not a pair, but I want them in the same stage. One *listens* to speech and writes words. One *hears a sentence* (or a description) and writes music. Opposite verbs, same decade, same lab neighborhood for some of the papers. The assistant era will want both verbs in one body: talk about a song, make a song, transcribe a meeting, hear a tone. Gemini’s native-audio sentence is that hunger. The 2022–2023 objects are the parts.

A novelty-safe legal hedge, required: I do not know, from here, which public models trained on which catalogs. I know the first thing any serious reader of this draft will think, because it is the first thing the industry thought. This series does not try those cases. It records that **the fight arrived faster for music than for many pictures**, because the existing owners were already organized. That speed is part of the multimodal story. Not every modality has the same politics.

If you take one technical memory: **audio forced the field to remember tokenization**. Pictures could hide in a continuous latent and a UNet. Waves, at any serious length, push you back to a vocabulary or to a very expensive clock. The vocabulary of a song is not the vocabulary of a face. Unification-of-block will keep pretending otherwise. The ear will keep being rude.

Next: a 2023 attempt to put more than two senses in one CLIP-like space — ImageBind — and what a joint space even means after you leave the pair.
