---
title: Style Guide — AI Compute Chip Magazine
status: staged
voice_check: edited
series: ai-compute-chip-magazine
---

# Style Guide

This issue is public GPU, CUDA, and TPU history for readers who have installed a driver, argued about occupancy, or quoted a peak FLOP they did not mean. It is not a press kit, not a white paper, and not a product pitch for any private stack.

## Voice

Write as someone who has shipped a kernel, read a datasheet, and learned that marketing FLOPs and measured FLOPs are different species. Prefer names, dates, architecture codenames, and first-party releases over mood. Short sentences are fine. Long sentences are fine when they carry a fact.

Speak to the reader as a peer. Do not coach. Do not cheerlead. Do not close with a moral or a recap list of “key takeaways.”

First person is allowed for shop observations (“the first time I saw an SXM module”). It is not a diary.

## Banned phrasing

Do not use: delve, landscape (metaphorical), robust, leverage, unlock, cutting-edge, game-changer, “In today’s,” “It’s important to note,” Moreover, “Whether you’re,” “In conclusion,” “At the end of the day,” “rich tapestry,” “journey,” “elevate,” “empower,” “seamless,” “holistic,” “unpack,” “nuanced” as filler, “democratize” as cheer, “revolution,” “Cambrian explosion,” “paradigm shift.”

Quoted press-release titles in `## Sources` may keep vendor words; the narrator’s body should not.

No COSMOS. No mesh memoir. No unpublished mechanisms. No patent or docket language.

## Facts and citations

Public sources only: press releases, papers, conference talks, product records, widely reported news. If a date is thin, say so. Do not invent a private conversation or an internal roadmap.

Vendor superlatives may be quoted and dated; do not repeat them as the narrator’s claim.

## Files

Canonical drafts live as `NN-slug.md` in this folder (45 articles). Slug list: `writer-slugs.json`. Do not fork a second article tree.

## Structure of an article

1. Open on an object or a dated event the reader can verify.
2. Name the people, orgs, and silicon.
3. Say what changed in hardware or software terms.
4. Say what the market or API did with it.
5. Leave one way to read a spec or a box label today.
6. End with `## Sources`, not a sermon.

Target roughly 500–1,200 words of body text. Frontmatter, captions, and source lists do not count.

## Frontmatter (every article)

```yaml
---
title: Plain title
dek: One-line hook
slug: NN-kebab-slug
series: AI Compute Chip Magazine
status: staged
voice_check: edited
kind: standalone-article
scope: public-history
novelty: public-record-only
exclusions: [no-cosmos, no-patents, no-unpublished-claims]
---
```

Writer drafts may start with `voice_check: human`. After a full editor pass, set `voice_check: edited` and record the pass in `EDITOR_REPORT.md`.
