# Style guide — SLPWOW SLP News, wave 2

## Reader

Working clinicians, informed parents, and teachers who hit an SLP headline and need the **document**, not the outrage. Magazine clarity. No alarm.

## Voice

- Short sentences. Name the statute, rule, compact page, or paper.
- Ban SEO slop: *delve, leverage, game-changer, in conclusion, whether you're a…, tapestry, plethora, unlock, empower, cutting-edge, healthcare landscape, holistic approach, in this article we will explore.*
- `voice_check: human` on writer drafts; `voice_check: edited` plus `voice_check_date` after an editor pass.
- No corporate we. No invented quotations. Short quoted phrases only when a title or a statutory term is the point.

## What an article is

A **news brief** about one public artifact (or a tight pair: CMS fact sheet + ASHA analysis). Target **550–900 words**. Open on the document or the date. Close on what the reader should open next. Cut padding.

Wave 1 briefs were graphics-first and short. Wave 2 briefs are text-first. Figures are optional; this pack does not ship SVGs.

## Front matter (required)

```yaml
---
title: Plain-language title
slug: kebab-case-matching-filename
meta_description: One or two sentences. No hype.
series: slpwow-slp-news-wave2
type: news-brief
desk: asha | cms | compact | research | literacy
order: 1
audience: clinicians-and-families
brand: slpwow
tags:
  - slp-news
citations:
  - "https://example.gov/primary"
status: draft
stage: draft
voice_check: human
last_verified: 2026-09-14
---
```

## Educational line

Italic, immediately after the H1:

*Educational news brief for SLPWOW. Not legal advice, not billing advice, and not a substitute for reading the primary source or for evaluation by a licensed clinician.*

## Sources

Cite in a **Sources** section at the end. Prefer CMS, Medicaid.gov, ASHA policy pages, aslpcompact.com, and open-access papers. Paraphrase. Do not paste copyrighted article bodies. A missing primary URL is a fail, not a vibe.

## Claims

See `CLAIMS_GUARDRAILS.md`.
