# SLPWOW Format Scope — Free Line

**Status:** what we will and will not make in the first free wave.
**Formats in scope:** worksheets · printouts · word lists · report templates.
**Authority:** `CLAIMS_GUARDRAILS.md`. Style: `STYLE_CLINICIAN_PDF.md`.

This file is the product fence. If a request is “make a board game / boom deck / 40-page packet / diagnostic protocol,” it is **out of this wave**. Queue it; do not smuggle it into a worksheet brief.

## 1. The four formats (one job each)

| Code | Format | Job | Typical length | Primary user while the page is open |
|---|---|---|---|---|
| `WS` | Worksheet | The student or client **marks or says** items while the clinician runs a target they already chose. | 1 page (2 if data lives on the back) | Student + clinician |
| `PO` | Printout | A **reference or setup** page: cue cards, partner boards, carryover ideas, room posters, session maps. Little or no “complete these items.” | 1 page | Clinician, partner, or caregiver |
| `WL` | Word list | A **clinician-facing list** of original stimulus words, grouped in a way that is useful in a session. | 1–2 pages | Clinician (student may see a stripped card) |
| `RT` | Report template | A **blank shell** for notes the clinician already has the right to write. | 1–2 pages | Clinician only |

If you cannot name the job in one sentence, you do not have a format yet.

## 2. In wave / later / never (free line)

### In this wave

- One-page `WS` with a data strip
- One-page `PO` caregiver or partner pages
- `WL` lists compiled by SLPWOW (original grouping, ordinary English)
- `RT` session snapshot, contact log, observation-only progress note
- Black-and-white US Letter, with a note that A4 users may scale to fit

### Later (do not pretend we shipped them)

- Color classroom posters as a separate SKU
- Interactive digital forms
- Translated editions (plan the English so it *can* translate; do not machine-translate and ship)
- Adult aphasia / cognitive *practice* frames beyond a single `AX` snapshot
- Video models

### Never on the free line (refuse)

- Standardized tests or look-alike protocols
- Screeners with cut scores
- Eligibility letters
- Swallow / feeding programs
- Oral-motor exercise packets sold as “cures”
- Recreations of another publisher’s page
- Character IP
- CEU courses disguised as a worksheet

## 3. Worksheets (`WS`)

**A worksheet is a trial sheet**, not a lesson plan and not a test.

Must have:

1. Title that names a **practice job** (“final /k/ words — say or mark”) not a disorder.
2. Design band from `AGE_BANDS.md`.
3. 4–12 student items (`PK`/`EE`) or 8–16 (`LE`+), unless `EI` (one item).
4. A data strip that tallies what happened, with no pass/fail product judgment.
5. The canonical footer from `CLAIMS_GUARDRAILS.md` §4.

Must not have:

- “Score: ___ / 10 = delayed”
- hidden answer keys that diagnose
- more than one clinical domain fighting on the same student face (speech *and* a reading test *and* a social rubric)

**Back page (optional):** clinician notes, cue key, “send home? yes/no.” Never a second test.

Full brief: `briefs/worksheets.md`.

## 4. Printouts (`PO`)

**A printout is hung, handed, or stood on the table.** The user is not “finishing items.”

Examples that are in scope:

- How-to-use this word list (clinician)
- Caregiver “three optional tries this week” (no quota)
- Low-tech partner board with blank cells
- Session map: greeting → practice → close
- “Kind voice day” general-education poster (voice hygiene only; see guardrails §8)

Examples that are actually worksheets in costume:

- 20-box homework calendars with daily quotas
- sticker charts for “no stuttering”
- classroom behavior rubrics that score a personality

If the page has a grid the student must complete, it is a `WS`. Recode it.

Full brief: `briefs/printouts.md`.

## 5. Word lists (`WL`)

**A word list is a clinician book page.** It is not a student coloring sheet.

Rules:

- Compile from ordinary English. Group by a linguistic or session-useful cut (syllable shape, position, everyday theme).
- Write the grouping rule at the top in **your own sentences**.
- Do not copy a published “100 words for /r/” list, even if you shuffle it.
- Mark register: child / teen / adult. A teen list that reads like a preschool list is a miss.
- Student-facing cards are a **derived `PO` or `WS`**, not the list itself. Derive; do not dump 80 words on a seven-year-old.

Phonetic notation: use a simple house style (`/s/`, `initial`, `final`). Do not paste a publisher’s phonetic table.

Full brief: `briefs/word-lists.md`.

## 6. Report templates (`RT`)

**A report template is empty on purpose.**

In scope:

- session snapshot (what we tried, what we heard, what we might try next)
- caregiver contact log
- observation-only progress note
- “information I still need” checklist (documents, not diagnoses)

Out of scope:

- canned “results indicate a moderate [disorder]” paragraphs
- score tables for named commercial tests
- eligibility / dismissal determination letters
- medical history forms that invite a downloadable PHI pile without a records system

Full brief: `briefs/report-templates.md`.

## 7. SKU shape

```
SLPWOW-FR-{FORMAT}-{DOMAIN}-{BAND}-{NN}
```

| Piece | Values |
|---|---|
| `FR` | free resource |
| `FORMAT` | `WS` `PO` `WL` `RT` |
| `DOMAIN` | `ART` speech-sound · `PHN` pattern practice · `PA` phonological awareness · `VOC` vocabulary · `SYN` sentences · `NAR` narrative · `SOC` social communication · `FLU` fluency-friendly · `AAC` partner support · `CG` caregiver · `DOC` documentation · `MIX` more than one domain, clinician-cut |
| `BAND` | `EI` `PK` `EE` `LE` `AD` `AX` `MX` |
| `NN` | 01–99 inside that tuple |

Example: `SLPWOW-FR-WS-ART-EE-01` — free worksheet, speech-sound practice, early-elementary feel, first page in that stack.

Filenames in the design folder match the SKU. Markdown briefs may describe many SKUs; they do not wear a SKU in the filename.

## 8. What one download contains

Default free download = **one SKU, one PDF**.

Do not staple a worksheet + a word list + a report into a “mega pack” that hides three footers. If the clinician needs all three, they download three pages. A later “kit” SKU may list the three IDs; it still reprints each footer.

## 9. Shared fields (every format)

Every brief and every PDF names:

| Field | Worksheet | Printout | Word list | Report template |
|---|---|---|---|---|
| Practice job in one line | required | required | required | “shell for notes,” not a student job |
| Design band | required | required | `MX` default | `MX` |
| Footer | required | required | required | required + PHI line |
| Originality sign-off | required | required | required | required |
| Send-home? | clinician checkbox | often yes | no (clinician keeps) | never sent as a “student worksheet” |

## 10. Handoff between formats (do not duplicate work)

A good first-wave cluster for one target looks like this:

1. `WL` — clinician list (source of words)
2. `WS` — 8–10 of those words as student items + data strip
3. `PO` — caregiver optional-try page using **three** of the same words
4. `RT` — session snapshot that has a blank “targets practiced” line (not a pasted diagnosis)

The words travel. The **claims** stay the same. The student never inherits a list title like “disordered /r/ set.”

## 11. Out-of-scope formats (so we stop arguing in review)

| Request | Response |
|---|---|
| Boom cards / interactive PDF quizzes with scores | Out. Paper first. |
| 30-page seasonal packet | Out. One SKU per download. |
| “Just like the [famous] apraxia deck” | Refuse. Original only. |
| Progress-monitoring probe with norms | Refuse. That is an instrument. |
| IEP goal bank with guaranteed legal language | Out. Not legal advice. A blank “goal the team already wrote” field may live on an `RT`. |
| Sticker book | Out. |

## 12. Definition of done for a format brief

A format brief is done when a writer who has **not** sat in the meeting can produce a first PDF without asking:

- who the page is for
- what is forbidden to say
- how many items
- where the footer goes
- whether it is a test (it is not)
