# Style Guide — SLPWOW Dysphagia & Swallowing Heritage Series

Staged copy for **SLPWOW.com** (WOW Therapies household; profession site, not the clinic booking page). This pack does not publish itself.

Sibling packs: `content/slpwow-speech-pathology-history/` is the general history of the profession. `content/voice-disorders-heritage/` is the larynx and the speaking/singing voice. This pack is the **swallow** — physiology, radiology, endoscopy, infant feeding as science, the SLP turn of the 1970s–80s, and the people who made “dysphagia” a job rather than a dictionary word.

## Who this is for

Readers are clinicians, students, caregivers, and curious people who landed on a speech-language pathology brand and stayed for a story. Write as if they already respect the work. Do not write as if they need a pep talk.

Keith’s wife’s practice is the eventual host. The series should feel like a well-edited magazine section, not a university syllabus and not a clinic brochure.

## Voice

Human. Specific. A little dry humor is allowed; cheerleading is not.

Open on a room, a date, a book, a fluoroscopy suite, a foreign-body card, a society meeting. Name the street if you have it. Name the journal if you have it. If you do not have it, do not fake the furniture.

Prefer:

- “On 13 April 1992 Johns Hopkins lost the radiologist who had opened a swallowing center nine years earlier.”
- “The 1988 *Dysphagia* paper is four pages and a new acronym.”
- “She put *Evaluation and Treatment of Swallowing Disorders* into American training in 1983, then kept rewriting the physiology.”

Avoid:

- “In today’s rapidly changing healthcare landscape…”
- “Whether you’re a clinician or a caregiver…”
- “Delve,” “landscape,” “leverage,” “robust,” “seamless,” “tapestry,” “unlock,” “empower,” “journey,” “holistic approach,” “it is important to note,” “cutting-edge,” “game-changer,” “navigate,” “utilize,” “in this article we will explore.”

No corporate we. No fake intimacy. No invented dialogue. Quoted speech only when a source actually recorded it.

## What an article is

Two kinds:

1. **Era / overview essays** — a thread with a beginning, a middle, and a present-tense residue. Not a Wikipedia dump.
2. **Major-figure profiles** — one person, one life, the work that still sits on clinic shelves. The person is not a mascot for the brand.

Target length: **700–1,600 words**. Era essays toward the long end; profiles can be tighter if every sentence earns its keep. Cut padding. Keep a concrete ending.

`check_pack.py` fails an era under 650 words or a profile under 450.

## Front matter (required)

```yaml
---
title: Plain-language title, no clickbait colon stacks
slug: kebab-case-matching-filename
series: slpwow-dysphagia-swallowing-heritage
type: era | profile
order: 1
tags:
  - dysphagia-heritage
meta_description: One or two sentences for a later WP excerpt. No hype. No how-to.
portrait: null
portrait_status: note | essay-only
figure_dates: "1783–1855"   # profiles only
voice_check: human
audience: slpwow
stage: draft
last_verified: 2026-09-14
---
```

`voice_check: human` is an editorial flag, not a boast. If a draft starts sounding like a model, rewrite the first paragraph before anything else.

`portrait: null` is mandatory in this pack. Portrait **notes** live in `PORTRAIT_SOURCES.md` and in a short “Portrait” section at the end of each profile.

## Educational line

Every article carries this line, italic, immediately after the H1 (or as the first body sentence after a lead image):

*Educational history for SLPWOW. Not a treatment plan and not a substitute for evaluation by a licensed clinician.*

Do not expand it into a legal essay. Do not turn it into a booking widget.

## Claims and caution

This is educational history, not a treatment manual.

- Do not give DIY protocols, chin-tuck homework, Mendelsohn or effortful-swallow steps, Shaker-exercise counts, thickener recipes, or “try this after a stroke.”
- Do not include living patients’ names, case details, or anything that reads as PHI. Historical patients already in the public scientific record (Jackson’s published foreign-body cases; named public figures in published memoirs) may be named as history.
- Degrees and titles must be accurate. “Dr.” only when the person held an earned doctorate or medical degree. Logemann was a Ph.D., not an M.D.
- When sources disagree (birth year, who “founded” FEES, whether 1981 was the first swallowing center on earth), say so in the article. Uncertainty is a fact.
- NPO-as-punishment, nursing-home starvation scandals, eugenic feeding decisions, and wartime experiments belong in the record. Do not sanitize. Do not sermonize. Put the primary act on the page, then the later judgment.

Banned as medical advice: swallow-maneuver cue sheets, IDDSI level charts presented as a household diet, water-protocol how-tos, tracheostomy-valve decision trees, infant pacing recipes.

Allowed: what a published method *was*, who wrote it, when, and how later clinicians argued with it.

## Names and spelling

Use the name the person published under, then the modern field name once.

- Historical medical word: *dysphagia* (difficulty swallowing) is older than the clinic. Do not pretend SLPs coined it.
- Vocal folds, not “vocal cords,” except inside a quotation or a historical title.
- *Oesophagus* inside British titles and Hurst; *esophagus* in American copy.
- Jerilyn Ann Logemann published as Jeri A. Logemann. First mention may carry Jerilyn; after that, Logemann or Jeri as the sources do.
- Wylie J. Dodds was Jerry in the Milwaukee hallway. First mention carries both.
- Do not call 1898 radiologists or 1920s endoscopists “SLPs.” They did not use that credential.
- FEES began in print as FEESS (fiberoptic endoscopic examination of swallowing safety). Say so once.

## Portraits — notes only

This pack does **not** ship image files and does **not** generate faces.

1. Public domain, CC, museum open access, or Wikimedia Commons with a readable license.
2. Record the candidate file, URL, license, author, and credit line in `PORTRAIT_SOURCES.md`.
3. Do not download into this folder in this pass.
4. If rights are unclear: labeled placeholder. **Never** generate a likeness and pass it off as a historical photograph.

Placeholder copy (use verbatim when needed):

> **Portrait placeholder.** No public-domain or clearly licensed portrait located as of the pack date. See `PORTRAIT_SOURCES.md` for hunt status. Do not invent or generate a substitute likeness.

## Structure of a profile

1. Opening scene or object (a book spine, a fluoroscopy tower, a safety-pin card, a society badge).
2. Birth, training, the job that mattered — in that order, without a childhood novel unless it is the story.
3. The work: publications, clinics, students, fights.
4. What later people kept, discarded, or had to apologize for.
5. Close on a residue: a test still in the cabinet, a journal that still arrives, a method people still argue about.
6. A **Portrait** note (candidate file or placeholder).

## Structure of an era essay

1. A dated scene.
2. The problem the decade thought it was solving.
3. Two or three institutions or books, not twelve.
4. Who was left out of the official story.
5. A last paragraph that lands in the present without a sales pitch.

## House style

- American English for U.S. subjects; British spelling only inside British quotations or book titles.
- Dates: 19 June 2014 on first use in a European or founding scene; June 19, 2014 is fine in U.S. profiles. Be consistent inside a piece.
- Italics for book titles. Quotes for article titles.
- Em dashes sparingly. No stacked rhetorical questions.
- First mention of ASHA uses the name then in force, then the modern name in parentheses if needed.

## SLPWOW / brand

Do not turn history into a WOW Therapies advertisement. One line in `INDEX.md` may note the host brand. Articles stand alone. No “book with us” close.

## Sources

Cite in the article when a claim is contested or surprising. Full citations live in `BIBLIOGRAPHY.md`. Prefer primary papers, *Dysphagia* memorials, Northwestern and Hopkins necrologies, ASHA Archives, Judy Duchan’s documented history pages, and the person’s own books. Do not cite a blog as the only warrant for a birth year.
