# Style Guide — SLPWOW AAC History & Figures

Staged copy for **SLPWOW.com** (WOW Therapies household; profession site, not the clinic booking page). This pack does not publish itself.

## Who this is for

Readers are clinicians, students, caregivers, AAC users, and curious people who landed on a speech-language pathology brand and stayed for a story. Write as if they already respect the work. Do not write as if they need a pep talk.

Keith’s wife’s practice is the eventual host. The series should feel like a well-edited magazine section, not a university syllabus and not a device catalog.

## Voice

Human. Specific. A little dry humor is allowed; cheerleading is not.

Open on a room, a date, a board, a hospital ward, a society meeting, a kitchen table with a photocopied overlay. Name the street if you have it. Name the journal if you have it. If you do not have it, do not fake the furniture.

Prefer:

- “ISAAC was named in East Lansing in May 1983, in a room that had spent two years arguing about the words *nonspeech*, *augmented*, and *alternative*.”
- “Maling’s 1963 paper in *Paraplegia* still used the hospital acronym P.O.S.M.; the company had already borrowed the Latin *possum*.”
- “The first commercial Minspeak overlay left PRC for the 1983 ASHA Convention in Cincinnati.”

Avoid:

- “In today’s rapidly changing healthcare landscape…”
- “Whether you’re a clinician or a caregiver…”
- “Delve,” “landscape,” “leverage,” “robust,” “seamless,” “tapestry,” “unlock,” “empower,” “journey,” “holistic approach,” “it is important to note,” “cutting-edge,” “game-changer,” “in conclusion.”

No corporate we. No fake intimacy. No invented dialogue. Quoted speech only when a source actually recorded it.

## What an article is

Two kinds:

1. **Era / overview essays** — a thread with a beginning, a middle, and a present-tense residue. Not a Wikipedia dump.
2. **Major-figure profiles** — one person (or a documented pair), one life, the work that still sits on clinic shelves or in a user’s bag. The person is not a mascot for the brand.

Target length: **550–1,200 words**. Era essays toward the long end; profiles can be tighter if every sentence earns its keep. Floor for QA: era ≥600 words, profile ≥450 words. Cut padding rather than inflate. Keep a concrete ending.

## Front matter (required)

```yaml
---
title: Plain-language title, no clickbait colon stacks
slug: kebab-case-matching-filename
series: slpwow-aac-history-figures
type: era | profile
order: 1
tags:
  - aac-history
meta_description: One or two sentences for a later WP excerpt. No hype.
portrait: null
portrait_status: note | essay-only | placeholder
figure_dates: "1897–1985"   # profiles only
voice_check: human
audience: slpwow
stage: draft
last_verified: 2026-09-14
---
```

This pass is **PD portrait notes only**. Keep `portrait: null`. Profiles use `portrait_status: note` (a public-domain or open-license candidate is logged) or `placeholder` (no candidate). Eras use `essay-only`. A later rights pass may set `downloaded` and add a raster; this pack does not.

`voice_check: human` is an editorial flag, not a boast. If a draft starts sounding like a model, rewrite the first paragraph before anything else.

## Educational note (required, near the top)

Every article carries this sentence, verbatim or with only the first clause varied:

> This is history for a general reader. It is not a diagnosis, not a treatment plan, and not a substitute for care with a licensed clinician.

## Claims and caution

This is educational history, not a treatment manual.

- Do not give device-selection recipes, home programs, or “try this if your child…”
- Do not include living patients’ names, case details, or anything that reads as PHI. Public scientific cases and self-advocates who published under their own names (Rick Creech, Michael B. Williams) may be named as history.
- Degrees and titles must be accurate. “Dr.” only when the person held an earned doctorate or medical degree. Flag honorary degrees.
- When sources disagree (first-course year, who coined *AAC*, how early a board was), say so in the article. Uncertainty is a fact.
- Institutions used words we would not use now (*crippled*, *retarded*, *nonspeech*). Quote the historical name once, then use the current name. Do not sanitize the letterhead. Do not sermonize it into a TED talk.
- Facilitated communication, rapid prompting, and related methods belong in the record. Put the claim, the controlled tests, and the professional statements on the page.

Banned as medical advice: PECS phase lists as homework, Minspeak icon sequences as how-tos, “what to buy after a diagnosis,” scanning hierarchies presented as a home kit.

Allowed: what a published method *was*, who wrote it, when, and how later clinicians and users argued with it.

## Names and spelling

Use the name the person published under, then the modern field name once.

- Historical field words: *nonspeech communication*, *assisted communication*, *augmented communication* → *AAC* after 1983.
- Do not call 1620 or 1780 teachers “SLPs.” They did not use that credential.
- Do not call a 1960 sip-and-puff typewriter an “SGD” in the inventor’s mouth. The later term can appear as a historian’s word.
- Charles K. Bliss was born Karl Kasiel Blitz. Use Bliss on first mention after the birth name.
- Ontario Crippled Children’s Centre (OCCC) is the 1971 letterhead; Holland Bloorview is the later hospital. Name both.
- Aleksandr / Alexander: not used in this pack except in sibling cross-links.

## Portraits — notes only

This pack does **not** ship image files and does **not** generate faces.

1. Public domain, CC, museum open access, or Wikimedia Commons with a readable license.
2. Record the candidate file, URL, license, author, and credit line in `PORTRAIT_SOURCES.md`.
3. Do not download into this folder in this pass.
4. If rights are unclear: labeled placeholder. **Never** generate a likeness and pass it off as a historical photograph.

Placeholder copy (use verbatim when needed):

> **Portrait placeholder.** No public-domain or clearly licensed portrait located as of the pack date. See `PORTRAIT_SOURCES.md` for hunt status. Do not invent or generate a substitute likeness.

## Structure of a profile

1. Opening scene or object (a board, a switch, a journal spine, a conference badge).
2. Birth, training, the job that mattered — in that order, without a childhood novel unless it is the story.
3. The work: publications, clinics, devices, students, fights.
4. What later people kept, discarded, or had to apologize for.
5. Close on a residue: a vocabulary still in a bag, a society name, a method people still argue about.
6. A **Portrait** note (candidate file or placeholder).

## Structure of an era essay

1. A dated scene.
2. The problem the decade thought it was solving.
3. Two or three institutions or books, not twelve.
4. Who was left out of the official story.
5. A last paragraph that lands in the present without a sales pitch.

## House style

- American English for U.S. subjects; British spelling only inside British quotations or book titles.
- Dates: 17 April 1861 on first use in a European scene; April 17 is fine in U.S. profiles. Be consistent inside a piece.
- Italics for book titles. Quotes for article titles.
- Em dashes sparingly. No stacked rhetorical questions.
- First mention of ASHA uses the name then in force, then the modern name in parentheses if needed.
- First mention of ISAAC is the full name, then ISAAC.

## SLPWOW / brand

Do not turn history into a WOW Therapies advertisement. One line in `INDEX.md` may note the host brand. Articles stand alone. No “book with us” close.

## Sources

Cite in the article when a claim is contested or surprising. Full citations live in `BIBLIOGRAPHY.md`. Prefer primary papers, ISAAC’s own histories (*Tales of ISAAC*), Zangari, Lloyd & Vicker (1994), Vanderheiden’s Trace memoirs, university necrologies, and the person’s own books. Do not cite a vendor blog as the only warrant for a birth year.
