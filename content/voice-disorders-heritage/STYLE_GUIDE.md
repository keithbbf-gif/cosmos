# Style Guide — SLPWOW Voice Disorders Heritage Series

Staged copy for **SLPWOW.com** (WOW Therapies). This pack does not publish itself. Nothing here is a live-site edit.

Sibling pack: `content/slpwow-speech-pathology-history/` is the general history of the profession. This pack is the **larynx and the speaking/singing voice** — instruments, clinics, theories, and the people who made “voice disorders” a job.

## Who this is for

Readers are clinicians, students, singers, teachers, caregivers, and curious people who landed on a therapy brand and stayed for a story. Write as if they already respect the work. Do not write as if they need a pep talk.

Keith’s wife’s practice is the eventual host. The series should feel like a well-edited magazine section, not a university syllabus and not a clinic brochure.

## Voice

Human. Specific. A little dry humor is allowed; cheerleading is not.

Open on a room, a date, a book, a mirror, a ward, a symposium hotel. Name the street if you have it. Name the journal if you have it. If you do not have it, do not fake the furniture.

Prefer:

- “On 24 May 1855 the Royal Society heard a singing teacher describe his own glottis.”
- “The 1974 *Folia Phoniatrica* paper is five pages and a diagram.”
- “She put *The Voice and Its Disorders* into British training in 1957, then kept rewriting it.”

Avoid:

- “In today’s rapidly changing healthcare landscape…”
- “Whether you’re a clinician or a singer…”
- “Delve,” “landscape,” “leverage,” “robust,” “seamless,” “tapestry,” “unlock,” “empower,” “journey,” “holistic approach,” “it is important to note,” “cutting-edge,” “game-changer,” “navigate,” “utilize,” “in this article we will explore.”

No corporate we. No fake intimacy. No invented dialogue. Quoted speech only when a source actually recorded it.

## What an article is

Two kinds:

1. **Era / overview essays** — a thread with a beginning, a middle, and a present-tense residue. Not a Wikipedia dump.
2. **Major-figure profiles** — one person, one life, the work that still sits on clinic shelves. The person is not a mascot for the brand.

Target length: **700–1,600 words**. Era essays toward the long end; profiles can be tighter if every sentence earns its keep. Cut padding. Keep a concrete ending.

`check_pack.py` fails an era under 800 words or a profile under 600.

## Front matter (required)

```yaml
---
title: Plain-language title, no clickbait colon stacks
slug: kebab-case-matching-filename
series: slpwow-voice-disorders-heritage
type: era | profile
tags: [voice-disorders-heritage, ...]
portrait: assets/portraits/slug.jpg | null
portrait_status: downloaded | placeholder | essay-only
figure_dates: "1805–1906"   # profiles only; omit if unknown
voice_check: human
audience: slpwow
stage: draft
---
```

`voice_check: human` is an editorial flag, not a boast. If a draft starts sounding like a model, rewrite the first paragraph before anything else.

## Educational line

Every article carries this line, italic, immediately after the H1 (or as the first body sentence after a lead image):

*Educational history for SLPWOW. Not a treatment plan and not a substitute for evaluation by a licensed clinician.*

Do not expand it into a legal essay. Do not turn it into a booking widget.

## Claims and caution

This is educational history, not a treatment manual.

- Do not give DIY protocols, resonant-voice homework, LSVT cue sheets, chewing-method instructions, or “try this if your child is hoarse.”
- Do not include patient names, case details, or anything that reads as PHI. Named historical patients (Frederick III; famous singers in published memoirs) stay in the public record and are treated as such.
- Degrees and titles must be accurate. “Dr.” only when the person held an earned doctorate or medical degree. G. Paul Moore was a Ph.D., not an M.D., even when later video credits slip.
- When sources disagree (death day, who saw the glottis first, who trained Brodnitz), say so in the article. Uncertainty is a fact.
- Oralism, eugenics, wartime experiments, Nazi-era clinics, and celebrity-medicine scandals belong in the record. Do not sanitize. Do not sermonize. Put the primary act on the page, then the later judgment.

Banned as medical advice: voice-hygiene checklists presented as homework, reflux diets as treatment, botulinum dosing, thyroplasty decision trees, gender-affirming voice protocols.

Allowed: what a published method *was*, who wrote it, when, and how later clinicians argued with it.

## Names and spelling

Use the name the person published under, then the modern field name once.

- Historical medical specialty: *laryngology*; German/French *Phoniatrie* / *phoniatrie*; therapy side *Logopädie* / logopedics / speech therapy / speech-language pathology.
- Vocal folds, not “vocal cords,” except inside a quotation or a historical title (*vocal cord* was the ordinary English of the nineteenth and mid-twentieth centuries; say so when you quote).
- Emil Fröschels also appears as Froeschels in American print; use Fröschels on first mention, Froeschels in U.S. citations.
- Gottfried Eduard Arnold published in the United States as Godfrey E. Arnold. First mention carries both.
- Do not call 1855 singing teachers “SLPs.” They did not use that credential.

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

1. Opening scene or object (a mirror, a book spine, a symposium badge, a film canister).
2. Birth, training, the job that mattered — in that order, without a childhood novel unless it *is* the story.
3. The work: publications, clinics, students, fights.
4. What later people kept, discarded, or had to apologize for.
5. Close on a residue: a scale still on a rating form, a meeting that still happens, a method people still argue about.

## Structure of an era essay

1. A dated scene.
2. The problem the decade thought it was solving.
3. Two or three institutions or books, not twelve.
4. Who was left out of the official story.
5. A last paragraph that lands in the present without a sales pitch.

## House style

- American English for U.S. subjects; British spelling only inside British quotations or book titles.
- Dates: 24 May 1855 on first use in a European or founding scene; May 24, 1855 is fine in U.S. profiles. Be consistent inside a piece.
- Italics for book titles. Quotes for article titles.
- Em dashes sparingly. No stacked rhetorical questions.
- First mention of ASHA uses the name then in force, then the modern name in parentheses if needed.

## SLPWOW / brand

Do not turn history into a WOW Therapies advertisement. One line in `INDEX.md` may note the host brand. Articles stand alone. No “book with us” close.

## Sources

Cite in the article when a claim is contested or surprising. Full citations live in `BIBLIOGRAPHY.md`. Prefer primary papers, *Journal of Voice* memorials, UEP curricula vitae, Judy Duchan’s documented history pages, Voice Foundation institutional history, and the person’s own books. Do not cite a blog as the only warrant for a birth year.
