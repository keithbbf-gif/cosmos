# Style Guide — SLPWOW Aphasia History & Figures

Staged copy for **SLPWOW.com** (WOW Therapies household; profession site, not the clinic booking page). This pack does not publish itself.

## Who this is for

Readers are clinicians, students, caregivers, and curious people who landed on a speech-language pathology brand and stayed for a story. Write as if they already respect the work. Do not write as if they need a pep talk.

Keith’s wife’s practice is the eventual host. The series should feel like a well-edited magazine section, not a university syllabus and not a clinic brochure.

## Voice

Human. Specific. A little dry humor is allowed; cheerleading is not.

Open on a room, a date, a book, a hospital ward, a society meeting. Name the street if you have it. Name the journal if you have it. If you do not have it, do not fake the furniture.

Prefer:

- “Leborgne died at Bicêtre on 17 April 1861, at eleven in the morning.”
- “The 1906 offprint ran thirty-eight pages and a title that picked a fight.”
- “McBride’s 1932 dissertation used the first forty cases; the 1935 book used 234.”

Avoid:

- “In today’s rapidly changing healthcare landscape…”
- “Whether you’re a clinician or a caregiver…”
- “Delve,” “landscape,” “leverage,” “robust,” “seamless,” “tapestry,” “unlock,” “empower,” “journey,” “holistic approach,” “it is important to note,” “cutting-edge,” “game-changer,” “in conclusion.”

No corporate we. No fake intimacy. No invented dialogue. Quoted speech only when a source actually recorded it.

## What an article is

Two kinds:

1. **Era / overview essays** — a thread with a beginning, a middle, and a present-tense residue. Not a Wikipedia dump.
2. **Major-figure profiles** — one person (or a documented pair), one life, the work that still sits on clinic shelves. The person is not a mascot for the brand.

Target length: **550–1,200 words**. Era essays toward the long end; profiles can be tighter if every sentence earns its keep. Floor for QA: era ≥600 words, profile ≥450 words. Cut padding rather than inflate. Keep a concrete ending.

## Front matter (required)

```yaml
---
title: Plain-language title, no clickbait colon stacks
slug: kebab-case-matching-filename
series: slpwow-aphasia-history-figures
type: era | profile
order: 1
tags:
  - aphasia-history
meta_description: One or two sentences for a later WP excerpt. No hype.
portrait: null
portrait_status: note | essay-only
figure_dates: "1824–1880"   # profiles only
voice_check: human
audience: slpwow
stage: draft
last_verified: 2026-09-14
---
```

`voice_check: human` is the writer flag; after editor pass, set `voice_check: edited`. Neither is a boast. If a draft starts sounding like a model, rewrite the first paragraph before anything else.

`portrait: null` is mandatory in this pack. Portrait **notes** live in `PORTRAIT_SOURCES.md` and in a short “Portrait” section at the end of each profile.

## Educational note (required, near the top)

Every article carries this sentence, verbatim or with only the first clause varied:

> This is history for a general reader. It is not a diagnosis, not a treatment plan, and not a substitute for care with a licensed clinician.

## Claims and caution

This is educational history, not a treatment manual.

- Do not give DIY protocols, home exercise programs, or “try this after a stroke…”
- Do not include living patients’ names, case details, or anything that reads as PHI. Historical patients already in the public scientific record (Leborgne, Lelong, Lordat’s self-report) may be named as history.
- Degrees and titles must be accurate. “Dr.” only when the person held an earned doctorate or medical degree. Flag honorary degrees.
- When sources disagree (death year, who coined a term, how large a lesion was), say so in the article. Uncertainty is a fact.
- Craniometry, racial ranking, eugenics, orphanage research, and wartime experiments belong in the record. Do not sanitize. Do not sermonize. Put the primary act on the page, then the later judgment.

Banned as medical advice: stimulation hierarchies presented as homework, MIT or constraint protocols as how-tos, naming drills, “what to do if your parent…”

Allowed: what a published method *was*, who wrote it, when, and how later clinicians argued with it.

## Names and spelling

Use the name the person published under, then the modern field name once.

- Historical medical word: *aphemia* (Broca) → *aphasia* (Trousseau and later usage).
- Do not call 1861 clinicians “SLPs.” They did not use that credential.
- Jules Déjerine / Augusta Déjerine-Klumpke: keep the accent on first mention.
- Aleksandr R. Luria also appears as Alexander; use Aleksandr on first mention, Luria after.
- Trousseau’s popularization of *aphasie* (1864) is a naming fact, not a discovery claim.

## Portraits — notes only

This pack does **not** ship image files and does **not** generate faces.

1. Public domain, CC, museum open access, or Wikimedia Commons with a readable license.
2. Record the candidate file, URL, license, author, and credit line in `PORTRAIT_SOURCES.md`.
3. Do not download into this folder in this pass.
4. If rights are unclear: labeled placeholder. **Never** generate a likeness and pass it off as a historical photograph.

Placeholder copy (use verbatim when needed):

> **Portrait placeholder.** No public-domain or clearly licensed portrait located as of the pack date. See `PORTRAIT_SOURCES.md` for hunt status. Do not invent or generate a substitute likeness.

## Structure of a profile

1. Opening scene or object (a book spine, a clinic door, a ward, a society meeting).
2. Birth, training, the job that mattered — in that order, without a childhood novel unless it is the story.
3. The work: publications, clinics, students, fights.
4. What later people kept, discarded, or had to apologize for.
5. Close on a residue: a test still in the cabinet, a building name, a method people still argue about.
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

## SLPWOW / brand

Do not turn history into a WOW Therapies advertisement. One line in `INDEX.md` may note the host brand. Articles stand alone. No “book with us” close.

## Sources

Cite in the article when a claim is contested or surprising. Full citations live in `BIBLIOGRAPHY.md`. Prefer primary papers, ASHA Archives, university necrologies, Judy Duchan’s documented history pages, Eling & Whitaker, Benton, and the person’s own books. Do not cite a blog as the only warrant for a birth year.
