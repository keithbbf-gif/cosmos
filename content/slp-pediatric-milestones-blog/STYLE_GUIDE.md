# Style guide — SLPWOW pediatric milestones

Staged copy for **SLPWOW.com**. Parent-facing. This pack does not publish itself.

`voice_check: human` means the draft was written against this file. `voice_check: edited` means an editor pass on top. Neither flag is a byline.

## Who is speaking

A careful writer who has sat with a parent at a well-child visit and with the CDC/ASHA pages on the table. Not a mascot. Not a scare site. Not a university syllabus. Not “a fellow mom who also happens to be…” unless that person is real and named — they are not.

Keith’s wife’s practice is the eventual host. The series should feel like a well-edited magazine section a parent can finish on a phone while the pasta water boils.

## Who it is for

Parents and regular caregivers of children from birth through about five. Grandparents and early educators may overhear. Do not write “whether you’re a parent or a clinician.” Clinicians already have ASHA. These pages are for the people who live with the child.

## Voice

Human. Specific. A little dry warmth is allowed. Cheerleading is not. Panic is not.

Open on a room, a checkup, a sentence a grandparent said, or a number a reader can check. Name the checklist, the paper, the year. If you do not have it, do not fake the furniture.

Prefer:

- “The 2022 CDC lists put ‘about 50 words’ at 30 months, not at 24.”
- “A wave is language. So is handing you the cup.”
- “You can ask for a hearing check without deciding anything else.”

Avoid the house-wide slop list:

- “In today’s rapidly evolving…”
- “It’s important to note”
- “delve” / “landscape” / “robust” / “leverage” / “unlock”
- “cutting-edge” / “game-changer”
- “In conclusion” / “Moreover” / “Furthermore”
- “Whether you’re a … or a …”
- “not just X, but Y” / “both an art and a science”
- “journey,” “tapestry,” “plethora,” “utilize,” “harness,” “empower,” “holistic”
- “red flags you must not ignore” as a headline voice
- throat-clearing first paragraphs

No corporate we. No fake intimacy. No invented dialogue unless you mark it as a typical kitchen sentence, not a quote.

## What an article is

Three kinds:

1. **Age-band** — one stretch of months, what CDC/ASHA actually printed, what it looks like on a Tuesday, what it is *not*.
2. **Domain** — sounds, understanding, gestures, hearing, two languages, play, books.
3. **Parent-guide** — how to read a chart, how to talk to the doctor, what an SLP visit is, wait-and-see, EI, AAC.

Target length: **700–1,400 words**. Age-band and “how to read the chart” pieces toward the long end. Cut the last recap if it only restates H2s. Quality over a word-count floor — a 400-word stub fails; padding to hit a thousand also fails.

## Front matter (required)

```yaml
---
title: Plain-language title, no scare colon stacks
slug: kebab-case-matching-filename
meta_description: One sentence, no diagnosis, no "must," under ~155 characters
series: slp-pediatric-milestones
type: age-band | domain | parent-guide
audience: parents
brand: slpwow
tags: [pediatric-milestones, ...]
age_band: "0-3m" | "4-6m" | ... | "birth-5" | "n/a"
citations:
  - "https://..."
status: draft
stage: draft
voice_check: human
---
```

Keep `status: draft` and `stage: draft`. Never map to WordPress `publish`.

## Claims posture

Follow `CLAIMS_GUARDRAILS.md`. Every draft carries the educational disclaimer. Efficacy of therapy, eligibility for Part C, and “this child needs…” are out of scope.

## Headings

H2s should be specific (“What the 30-month list actually says”) not thematic (“The language journey”).

## Voice check before `voice_check: human`

Read the draft out loud. If a sentence could sit under any parenting-blog brand without changing a noun, rewrite it. If two adjacent paragraphs start with the same syntactic shape, break one. If you cannot point to a source for a number, flag `[VERIFY]` or delete it.
