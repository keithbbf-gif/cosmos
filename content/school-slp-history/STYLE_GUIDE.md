# Style Guide — SLPWOW School-Based SLP History & Policy

Staged copy for **SLPWOW.com** (WOW Therapies household; profession site, not the clinic booking page). This pack does not publish itself.

## Who this is for

Readers are clinicians, students, caregivers, and curious people who landed on a speech-language pathology brand and stayed for a story. Write as if they already respect the work. Do not write as if they need a pep talk.

Keith’s wife’s practice is the eventual host. The series should feel like a well-edited magazine section, not a university syllabus and not a clinic brochure.

## Voice

Human. Specific. A little dry humor is allowed; cheerleading is not.

Open on a room, a date, a statute number, a hotel corridor, a closet with a folding table, a Supreme Court syllabus. Name the street if you have it. Name the reporter if you have it. If you do not have it, do not fake the furniture.

Prefer:

- “On 29 November 1975, Gerald Ford signed S. 6. There was no ceremony.”
- “Duchan puts Chicago’s first ten speech teachers in 1910, under Ella Flagg Young.”
- “Related services, in the 1975 text, listed speech pathology in parentheses. The parentheses did the century’s work.”

Avoid:

- “In today’s rapidly changing healthcare landscape…”
- “Whether you’re a clinician or a parent…”
- “Delve,” “landscape,” “leverage,” “robust,” “seamless,” “tapestry,” “unlock,” “empower,” “journey,” “holistic approach,” “it is important to note,” “cutting-edge,” “game-changer,” “in conclusion.”

No corporate we. No fake intimacy. No invented dialogue. Quoted speech only when a source actually recorded it.

## What an article is

Two kinds:

1. **Era / policy essays** — a thread with a beginning, a middle, and a present-tense residue. Not a Wikipedia dump.
2. **Profiles** — one person, one case name, or one public figure whose paper still sits in a school file. The person is not a mascot for the brand.

Target length: **550–1,200 words**. Era essays toward the long end; profiles can be tighter if every sentence earns its keep. Floor for QA: era ≥600 words, profile ≥450 words. Cut padding rather than inflate. Keep a concrete ending.

## Front matter (required)

```yaml
---
title: Plain-language title, no clickbait colon stacks
slug: kebab-case-matching-filename
series: slpwow-school-slp-history
type: era | profile
order: 1
tags:
  - school-slp-history
meta_description: One or two sentences for a later WP excerpt. No hype.
portrait: null
portrait_status: note | essay-only
figure_dates: "1880–1962"   # profiles only
voice_check: human
audience: slpwow
stage: draft
last_verified: 2026-09-14
---
```

`voice_check: human` is an editorial flag, not a boast. If a draft starts sounding like a model, rewrite the first paragraph before anything else.

`portrait: null` is mandatory in this pack. Portrait **notes** live in `PORTRAIT_SOURCES.md`.

## Educational note (required, near the top)

Every article carries this sentence, verbatim or with only the first clause varied:

> This is history for a general reader. It is not a diagnosis, not a treatment plan, and not a substitute for care with a licensed clinician.

## Claims and caution

See `CLAIMS_GUARDRAILS.md`. This is educational history and civic policy, not a treatment manual and not legal advice.

- Do not give DIY protocols, home exercise programs, or “try this if your child…”
- Do not tell a parent how to win a due-process hearing.
- Do not include living students’ names except the public case captions already in court reporters (Amy Rowley, Amber Tatro, Garret Frey, Endrew F.). Use the caption the Court used.
- Degrees and titles must be accurate.
- When sources disagree (who hired first, a Public Law typo on a government page), say so in the article. Uncertainty is a fact.

Banned as advice: caseload “caps” presented as homework, eligibility decision trees, IEP goal banks, Medicaid billing how-tos, cue hierarchies.

Allowed: what a statute *said*, who wrote a policy letter, when a city hired its first speech teacher, and how later clinicians argued with the number.

## Names and spelling

- Historical U.S. school job: *speech correction teacher* → *speech clinician* / *speech therapist* → *speech-language pathologist*.
- Do not call 1910 or 1925 school workers “SLPs.” They did not hold that credential.
- Use the statutory language of the year you are in (*handicapped children* in 1975; *children with disabilities* after 1990). Then say, once, that the older noun is the statute’s, not the house’s.
- Rosa’s Law (2010) replaced “mental retardation” in federal law with “intellectual disability.” Historical case names (PARC) keep their caption; the essay explains the word.

## Portraits — notes only

This pack does **not** ship image files and does **not** generate faces.

Placeholder copy (use verbatim when needed):

> **Portrait placeholder.** No public-domain or clearly licensed portrait located as of the pack date. See `PORTRAIT_SOURCES.md` for hunt status. Do not invent or generate a substitute likeness.

## Structure of a profile

1. Opening scene or object (a book spine, a consent decree, a Rockville letterhead).
2. Birth and training when known; if a birth year is not independently confirmed, say so.
3. The work: publications, offices, fights.
4. What later people kept, discarded, or had to apologize for.
5. Close on a residue.
6. A **Portrait** note.

## Structure of an era / policy essay

1. A dated scene.
2. The problem the decade thought it was solving.
3. Two or three institutions, statutes, or books, not twelve.
4. Who was left out of the official story.
5. A last paragraph that lands in the present without a sales pitch.

## House style

- American English.
- Dates: 29 November 1975 on first use for a federal signing; November 29 is fine in a U.S. school-board scene. Be consistent inside a piece.
- Italics for book and case names on first full citation; thereafter short names.
- Em dashes sparingly. No stacked rhetorical questions.

## SLPWOW / brand

Do not turn history into a WOW Therapies advertisement. One line in `INDEX.md` may note the host brand. Articles stand alone. No “book with us” close.

## Sources

Cite in the article when a claim is contested or surprising. Full citations live in `BIBLIOGRAPHY.md`. Prefer statutes on govinfo, U.S. Reports, ED.gov IDEA history, ASHA public policy pages, Judy Duchan’s documented history pages, and contemporaneous *Quarterly Journal of Speech* / *LSHSS* papers. Do not cite a blog as the only warrant for a date.
