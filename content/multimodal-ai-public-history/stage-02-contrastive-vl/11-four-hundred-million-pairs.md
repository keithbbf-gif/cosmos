---
id: "11"
slug: four-hundred-million-pairs
title: Four hundred million pairs, and the public silence
stage: 02-contrastive-vl
stage_title: Contrastive vision–language
status: draft
voice: human
novelty_safe: true
public_record_only: true
primary_public_sources:
  - "Radford et al., CLIP paper (WIT / 400 million pair description)"
  - "OpenAI CLIP model card (limitations, use)"
  - "Schuhmann et al., LAION-400M / LAION-5B public dataset papers (the open attempt to rhyme)"
does_not_claim:
  - "contents of the unreleased WIT scrape"
  - "legal conclusions"
  - "that LAION equals WIT"
last_reviewed: 2026-09-14
---

# Four hundred million pairs, and the public silence

CLIP’s dataset is famous and not public. That sentence is the draft.

The paper says they collected 400 million (image, text) pairs from the internet. The number is round on purpose; you can feel it. It is large enough to make ImageNet look like a pamphlet and small enough, later, to look modest next to LAION-5B’s billions. It became a chant. People said “400 million” the way they used to say “1.28 million.” A chant is not a corpus.

I will not describe the scrape. I do not have it. Neither do you. Secondary writeups that pretend to know which sites were in WIT are, unless they cite a primary, fan fiction. The primary says: web, pairs, 400 million, constructed to be a noisier and broader cousin of the academic caption sets. Then it moves on to experiments. The moving on is a silence. The silence is part of the public record.

Why does the silence matter if the weights are out?

Because **behavior is not provenance**. We can measure that CLIP is strong on certain classifications and weak on others. We can measure that it has cultural skews, that it can be prompted into ugly stereotypes, that it is better at some geographies and objects than others. The model card admits a list of these. What we cannot do is point at the training pair that taught a particular association. ImageNet let you do a version of that: the synset, the URL list, the contest rules. WIT does not. So a whole style of dataset accountability — “show me the label” — broke, in public, the same month the tool shipped.

The open-data response was not long in coming. LAION-400M and then LAION-5B tried to rebuild a web-scale pair set that a person could actually download as URLs and metadata. They filtered with CLIP itself, which is a historical knot I will untie in draft 31: the open commons is partly *defined* by the closed model’s taste. That does not make LAION a copy of WIT. It makes LAION a public rhyme with a circularity at the center.

A human thing I want to keep: those 400 million texts were written by people who did not think they were training a model. They were writing alt-text for a screen reader, or a filename, or a product title, or a joke, or spam. “Natural language supervision” is a gentle phrase for an involuntary authorship. The later legal and ethical fights around training data — which I will only touch as public events, not as a brief — start here, in the gap between a number and a consent.

There is a technical silence too. Cleaning. Deduplication. How they handled languages. How they handled pornographic content, medical content, faces. The paper and card give some notes and not a recipe. I will not invent one. I will say that every later open attempt had to make those choices in daylight, and the daylight was brutal, and that brutality is one reason some labs still prefer the silence.

Compare three public objects:

| Object | What you can hold | What you cannot |
| --- | --- | --- |
| ImageNet ILSVRC | Images, synsets, a contest protocol | The full original web, some taken-down URLs |
| CLIP WIT | A number, a prose description, a trained weight | The pairs |
| LAION-5B | URLs, text, CLIP similarity, later safety scores | Stable files (links rot); uncontested consent |

A history that only praises “scale” will treat these as the same story with different file sizes. They are not. They are different contracts with the reader.

I do not conclude, from the silence, that the work should not have been published. I conclude that **the publication was partial**, and that later “foundation model” papers inherited the partial as a norm. When Gemini or GPT-4V describes data at the level of category and not corpus, they are speaking CLIP’s dialect. The dialect started as a practical choice. It became a genre.

If you are tempted, in a later draft of your own, to write “CLIP was trained on the internet” and stop, do not. Write: trained on an unreleased collection of 400 million web pairs, as stated; weights released; pairs not. That extra clause is the whole ethics of this paragraph. It is also, more selfishly, the only way a later researcher can know what they do not know.
