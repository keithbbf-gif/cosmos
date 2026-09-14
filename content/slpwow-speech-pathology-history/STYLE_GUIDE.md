# Style Guide — SLPWOW Speech Pathology History Series

Staged copy for **SLPWOW.com** (WOW Therapies). This pack does not publish itself. Nothing here is a live-site edit.

## Who this is for

Readers are clinicians, students, caregivers, and curious people who landed on a therapy brand and stayed for a story. Write as if they already respect the work. Do not write as if they need a pep talk.

Keith’s wife’s practice is the eventual host. The series should feel like a well-edited magazine section, not a university syllabus and not a clinic brochure.

## Voice

Human. Specific. A little dry humor is allowed; cheerleading is not.

Open on a room, a date, a book, a hospital ward, a hotel corridor. Name the street if you have it. Name the journal if you have it. If you do not have it, do not fake the furniture.

Prefer:

- “On 29 December 1925, thirteen people sat down in the Hotel McAlpin…”
- “The 1969 paper ran thirty-eight scales and seven neurologic groups.”
- “She earned the first American doctorate in the field in 1922, at Wisconsin, under Smiley Blanton.”

Avoid:

- “In today’s rapidly changing healthcare landscape…”
- “Whether you’re a clinician or a parent…”
- “Delve,” “landscape,” “leverage,” “robust,” “seamless,” “tapestry,” “unlock,” “empower,” “journey,” “holistic approach,” “it is important to note.”

No corporate we. No fake intimacy. No invented dialogue. Quoted speech only when a source actually recorded it.

## What an article is

Two kinds:

1. **Era / overview essays** — a thread with a beginning, a middle, and a present-tense residue. Not a Wikipedia dump.
2. **Major-figure profiles** — one person, one life, the work that still sits on clinic shelves. The person is not a mascot for the brand.

Target length: **900–1,400 words**. Cut padding. Keep a concrete ending.

## Front matter (required)

```yaml
---
title: Plain-language title, no clickbait colon stacks
slug: kebab-case-matching-filename
series: slpwow-speech-pathology-history
type: era | profile
tags: [speech-pathology-history, ...]
portrait: assets/portraits/slug.jpg | null
portrait_status: downloaded | placeholder | essay-only
figure_dates: "1885–1977"   # profiles only; omit if unknown
voice_check: human
audience: slpwow
stage: draft
---
```

`voice_check: human` is an editorial flag, not a boast. If a draft starts sounding like a model, rewrite the first paragraph before anything else.

## Claims and caution

This is educational history, not a treatment manual.

- Do not give DIY protocols, home exercise programs, or “try this if your child…”
- Do not include patient names, case details, or anything that reads as PHI.
- Degrees and titles must be accurate. “Dr.” only when the person held an earned doctorate or medical degree. Flag honorary degrees.
- When sources disagree (death year, wartime service, who coined a term), say so in the article. Uncertainty is a fact.
- Oralism, eugenics, orphanage research, and wartime experiments belong in the record. Do not sanitize. Do not sermonize. Put the primary act on the page, then the later judgment.

Banned as medical advice: stimulation hierarchies presented as homework, stuttering “cures,” aphasia drills, cleft-palate home programs.

Allowed: what a published method *was*, who wrote it, when, and how later clinicians argued with it.

## Names and spelling

Use the name the person published under, then the modern field name once.

- Historical U.S. field: *speech correction* → *speech pathology* → *speech-language pathology* / *communication sciences and disorders*.
- Britain: *speech therapy* → *speech and language therapy* (RCSLT).
- German-speaking Europe: *Phoniatrie* (medical) and *Logopädie* (therapy).
- Emil Fröschels also appears as Froeschels in American print; use Fröschels on first mention, Froeschels in U.S. citations.

Do not call 1925 clinicians “SLPs.” They did not use that credential.

## Portraits

Every profile tries for a real, rights-clear portrait.

1. Public domain, CC, museum open access, or Wikimedia Commons with a readable license.
2. Record the file, URL, license, author, and credit line in `PORTRAIT_SOURCES.md`.
3. Download only when redistribution in this repo is clearly allowed.
4. Embed with a caption **and** a credit under the image.
5. If rights are unclear: labeled placeholder. **Never** generate a likeness and pass it off as a historical photograph.

Placeholder copy (use verbatim when needed):

> **Portrait placeholder.** No public-domain or clearly licensed portrait located as of the pack date. See `PORTRAIT_SOURCES.md` for hunt status. Do not invent or generate a substitute likeness.

## Structure of a profile

1. Opening scene or object (a book spine, a clinic door, a ward).
2. Birth, training, the job that mattered — in that order, without a childhood novel unless it is the story (Van Riper’s stutter; Johnson’s).
3. The work: publications, clinics, students, fights.
4. What later people kept, discarded, or had to apologize for.
5. Close on a residue: a test still in the cabinet, a building name, a method people still argue about.

## Structure of an era essay

1. A dated scene.
2. The problem the decade thought it was solving.
3. Two or three institutions or books, not twelve.
4. Who was left out of the official story.
5. A last paragraph that lands in the present without a sales pitch.

## House style

- American English for U.S. subjects; British spelling only inside British quotations or book titles.
- Dates: 29 December 1925 on first use in a European or founding scene; December 29, 1925 is fine in U.S. profiles. Be consistent inside a piece.
- Italics for book titles. Quotes for article titles.
- Em dashes sparingly. No stacked rhetorical questions.
- First mention of ASHA uses the name then in force, then the modern name in parentheses if needed.

## SLPWOW / brand

Do not turn history into a WOW Therapies advertisement. One line in `INDEX.md` may note the host brand. Articles stand alone. No “book with us” close.

## Sources

Cite in the article when a claim is contested or surprising. Full citations live in `BIBLIOGRAPHY.md`. Prefer ASHA Archives, university necrologies, Dictionary of National Biography, Judy Duchan’s documented history pages, and the person’s own books. Do not cite a blog as the only warrant for a birth year.
