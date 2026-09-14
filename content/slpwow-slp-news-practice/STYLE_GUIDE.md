# Style guide — SLPWOW SLP News (practice wave)

Staged copy for **SLPWOW.com**. Clinician-facing. This pack does not publish itself.

`voice_check: human` means the draft was written against this file. `voice_check: edited` means an editor pass on top. Neither flag is a byline.

## Who is speaking

A careful writer who has sat with the ASHA Leader, a CMS transmittal, and a journal PDF on the same desk. Not a billing consultant selling a course. Not a university methods syllabus. Not “a fellow SLP who also happens to be…” unless that person is real and named — they are not.

Keith’s wife’s practice is the eventual host. The series should feel like a well-edited practice-news section a school or medical SLP can finish on a phone between sessions.

## Who it is for

Working speech-language pathologists and the people who sit next to them — clinical fellows, supervisors, office managers who have to explain a modifier. Families may overhear. Do not write “whether you’re a parent or a clinician.” Parents have the milestone pack. These pages are for people who already know what a progress note is.

## Voice

Human. Specific. A little dry warmth is allowed. Cheerleading is not. Panic is not. Workshop-speak is not.

Open on a mailbox, a fee-schedule PDF, a hallway argument, or a number a reader can check. Name the transmittal, the paper, the year. If you do not have it, do not fake the furniture.

Prefer:

- “The hard cap died in 2018. The KX threshold did not.”
- “An abstract is a sales letter the journal allowed.”
- “School medical necessity and Medicare medical necessity are not the same sentence.”

Avoid the house-wide slop list:

- “In today’s rapidly evolving…”
- “It’s important to note”
- “delve” / “landscape” / “robust” / “leverage” / “unlock”
- “cutting-edge” / “game-changer”
- “In conclusion” / “Moreover” / “Furthermore”
- “Whether you’re a … or a …”
- “not just X, but Y” / “both an art and a science”
- “journey,” “tapestry,” “plethora,” “utilize,” “harness,” “empower,” “holistic”
- “must-know updates” / “everything you need”
- throat-clearing first paragraphs

No corporate we. No fake intimacy. No invented patient names. Composite hallway sentences are allowed if they teach a distinction, not a protocol.

## What an article is

Four kinds:

1. **research-literacy** — how to read a paper, a review, a preprint, a conflict line.
2. **reimbursement** — a public payment change in plain language. News, not a coding worksheet.
3. **school-medical** — two settings, two clocks, two definitions of “need.”
4. **practice-headline** — dysphagia, voice, fluency, pediatric, AAC, post-COVID *news*. Not how to run the session.

Target length: **700–1,300 words**. Briefs can sit at the short end if they still earn the heading. A 400-word stub fails; padding to hit a thousand also fails.

## Front matter (required)

```yaml
---
title: Plain-language title, no scare colon stacks
slug: kebab-case-matching-filename
meta_description: One sentence, no protocol, no "must," under ~155 characters
series: slpwow-slp-news-practice
type: research-literacy | reimbursement | school-medical | practice-headline
audience: clinicians
brand: slpwow
tags: [slp-news, ...]
citations:
  - "https://..."
status: draft
stage: draft
voice_check: human
---
```

Keep `status: draft` and `stage: draft`. Never map to WordPress `publish`.

## Claims posture

Follow `CLAIMS_GUARDRAILS.md`. Every draft carries the educational disclaimer. Efficacy promises, eligibility promises, and “bill it this way” scripts are out of scope.

## Headings

H2s should be specific (“What CMS printed for CY 2026”) not thematic (“The reimbursement journey”).

## Voice check before `voice_check: human`

Read the draft out loud. If a sentence could sit under any CEU mill without changing a noun, rewrite it. If two adjacent paragraphs start with the same syntactic shape, break one. If you cannot point to a source for a number, flag `[VERIFY]` or delete it.
