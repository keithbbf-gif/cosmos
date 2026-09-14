---
id: "31"
slug: laion-safety-and-the-dataset-fights
title: LAION, safety, and the dataset fights
stage: 05-public-t2i
stage_title: Public text-to-image
status: draft
voice: human
novelty_safe: true
public_record_only: true
primary_public_sources:
  - "Schuhmann et al., LAION-5B, NeurIPS Datasets and Benchmarks 2022"
  - "LAION-400M public notes (2021)"
  - "Public statements around later LAION dataset withdrawals / safety reviews (press + official posts; treat as events, not verdicts)"
does_not_claim:
  - "legal outcomes"
  - "a complete inventory of harmful content"
  - "that CLIP-filtering is morally sufficient"
last_reviewed: 2026-09-14
---

# LAION, safety, and the dataset fights

LAION-5B’s paper is, on its face, a civic offer. CLIP and DALL·E showed what billions of pairs might do. Those billions were not available. So here is a URL list: 5.85 billion CLIP-filtered image–text pairs, English and not, with extra scores for watermark, NSFW, and a neighborhood index so you can poke the thing. NeurIPS Datasets and Benchmarks, 2022. The tone is democratize. The method is a loop.

The loop is the history.

To decide whether a web pair is “good enough” to keep, they use CLIP. CLIP, whose own pairs you cannot see, becomes the gate of the pairs you can. A closed taste becomes an open commons. I said this in draft 14 as a knot. I am saying it again as a **safety and politics** knot. If CLIP under-represents a language, a body type, a kind of amateur photograph, the commons inherits the hole. If CLIP is good at matching English marketing syntax, the commons inherits the ad. Filtering is not neutral. It is a second model.

The paper is not naïve about harmful content. It describes classifiers (including CLIP-based ones) for pornographic and otherwise “inappropriate” material, and it treats the scores as something you can use to *subset*, not as a guarantee. That distinction — **score as a tool, not as a purification** — is the adult sentence. A lot of later conversation lost the distinction. People said “LAION is unsafe” as if a URL list were a single moral object. People said “it’s just links” as if a link were not an invitation.

Then the public events arrived, as they had to. Researchers and journalists found illegal sexual imagery of children in web-scale collections, including in the LAION universe, because the web has it and a scraper will meet it. LAION, in public, took down and reviewed. I will not play investigator. I will write the historical shape: **once you publish a commons of the web, you inherit the web’s worst category errors, and “we filtered with CLIP” is not a legal or moral finish line.** City B’s existence depends on someone having published something like this. City B’s shame does too.

There are other fights in the same pile, and I will keep them separate so they do not become a sludge:

- **Consent and copyright.** A URL list of pictures people took for a different purpose. Lawsuits and takedowns belong to courts and to later years; this draft only records that the fight is downstream of the offer.
- **Labor.** Annotators and raters and the invisible writers of alt-text. The commons is not unpaid in the sense of “no human was involved.” It is unpaid in the sense of “the humans were not paid *for this*.”
- **The aesthetic subset.** Later training runs (including ones associated with Stable Diffusion versions) used “aesthetics” scores. Pretty as a filter is a cultural policy. It will show up in whose faces look like default.

I refuse two sermons.

Sermon one: scale is innocent because it is average. It is not. Averages hide the tail, and the tail is where the harm lives.

Sermon two: the only ethical move was never to build the commons. Maybe. Also maybe not: the closed WIT-style corpora did not disappear because LAION was criticized. They stayed closed. A world with only City A still has the pairs. It just does not let you see the index. Visibility is not virtue, but invisibility is not virtue either.

What I want a reader to carry into stage 06: when people start fine-tuning on ten photos of their face, they are standing on this pile. When ControlNet trains on edges derived from web pictures, this pile. When a safety paper says “we removed NSFW,” ask *which classifier*, *trained on what*, *with whose false negatives*. The dataset fights are not a detour from multimodal history. They are the supervision.

Stage 05 ends here on purpose, on a sour note. The pretty year was a data year. The next stage is what City B did with the file once they had it: they taught it new nouns, new ranks, new verbs. Personalization, LoRA, ControlNet. The joint learns to take orders from something other than a sentence.
