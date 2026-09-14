---
pack: slpwow-free-resources-curriculum
doc: INDEX
status: curriculum-briefs-wave-1
voice: human
voice_check: edited
lint: check-curriculum
---

# SLPWOW Free Resources — Curriculum Index

**Line:** SLPWOW free therapy materials (clinician-facing PDFs)
**Tree:** `content/slpwow-free-resources-curriculum/` on cosmos
**Status:** curriculum briefs (wave 1). Not yet designed PDFs. Not a live Core change.
**Date:** 2026-09-14
**Rule:** original work only. Do not reproduce copyrighted worksheet text from the web.

This index is the map. `CLAIMS_GUARDRAILS.md` is the law. If a brief and the guardrails disagree, the guardrails win.

## What this pack is

SLPWOW’s free line needs **session-ready paper** that a licensed clinician can print without inheriting another publisher’s page and without telling a family their child “has” a disorder.

This folder specifies:

| Piece | File | Job |
|---|---|---|
| Claims | [`CLAIMS_GUARDRAILS.md`](CLAIMS_GUARDRAILS.md) | No diagnosis. No screen. No outcome guarantee. Original only. |
| Age bands | [`AGE_BANDS.md`](AGE_BANDS.md) | Design feels (`EI`–`AX`, `MX`). Not developmental norms. |
| Formats | [`FORMAT_SCOPE.md`](FORMAT_SCOPE.md) | Worksheets, printouts, word lists, report templates — only these. |
| Style | [`STYLE_CLINICIAN_PDF.md`](STYLE_CLINICIAN_PDF.md) | Quiet, copier-safe, clinician-first PDFs. |
| Gate | [`PREPUBLISH.md`](PREPUBLISH.md) | Ship / refuse checklist. |
| Machine list | [`manifest.toml`](manifest.toml) | Files + first-wave SKUs for checks. |

It does **not** contain designed worksheets, scraped word lists, or sample reports with fake scores.

## Reading order (writers)

1. [`CLAIMS_GUARDRAILS.md`](CLAIMS_GUARDRAILS.md) — entire file.
2. [`AGE_BANDS.md`](AGE_BANDS.md)
3. [`FORMAT_SCOPE.md`](FORMAT_SCOPE.md)
4. The format brief you were assigned.
5. The domain brief you were assigned.
6. [`STYLE_CLINICIAN_PDF.md`](STYLE_CLINICIAN_PDF.md)
7. [`PREPUBLISH.md`](PREPUBLISH.md) on the ticket.

Reviewers start at the guardrails, then `PREPUBLISH.md`, then the PDF.

## Format briefs

| Format | Code | Brief | One-line job |
|---|---|---|---|
| Worksheets | `WS` | [`briefs/worksheets.md`](briefs/worksheets.md) | Trial sheet + tally. Not a test. |
| Printouts | `PO` | [`briefs/printouts.md`](briefs/printouts.md) | Reference / setup / optional home tries. |
| Word lists | `WL` | [`briefs/word-lists.md`](briefs/word-lists.md) | Original clinician lists (12–24 words). |
| Report templates | `RT` | [`briefs/report-templates.md`](briefs/report-templates.md) | Empty shells. No canned diagnosis. |

Out of wave: Boom decks, 30-page seasonal packets, screeners, swallow programs, character IP. See format scope §11.

## Domain briefs

| Domain | Codes | Brief |
|---|---|---|
| Speech-sound and pattern practice | `ART` `PHN` | [`domains/speech-sound.md`](domains/speech-sound.md) |
| Language (words, frames, telling) | `VOC` `SYN` `NAR` | [`domains/language.md`](domains/language.md) |
| Phonological awareness / early print | `PA` | [`domains/phonological-awareness.md`](domains/phonological-awareness.md) |
| Social communication, fluency-friendly, AAC partner | `SOC` `FLU` `AAC` | [`domains/social-fluency.md`](domains/social-fluency.md) |
| Caregiver pages | `CG` | live in [`briefs/printouts.md`](briefs/printouts.md) |
| Documentation shells | `DOC` | live in [`briefs/report-templates.md`](briefs/report-templates.md) |

## Age bands (codes only)

Full table: [`AGE_BANDS.md`](AGE_BANDS.md).

`EI` 18–35 months · `PK` 3;0–5;11 · `EE` 5;0–8;11 · `LE` 8;0–11;11 · `AD` 12;0–17;11 · `AX` 18+ · `MX` mixed / clinician-cut.

Bands are **page feel**. They are not cutoffs and not “mastery ages.”

## First-wave SKU catalog

SKU shape: `SLPWOW-FR-{FORMAT}-{DOMAIN}-{BAND}-{NN}` — [`FORMAT_SCOPE.md`](FORMAT_SCOPE.md) §7.

### Worksheets

| SKU | Job |
|---|---|
| `SLPWOW-FR-WS-ART-EE-01` | Picture words — clinician names the sound |
| `SLPWOW-FR-WS-PHN-PK-01` | Two-pile sort — clinician names the pattern |
| `SLPWOW-FR-WS-VOC-EE-01` | Name / describe / use |
| `SLPWOW-FR-WS-SYN-LE-01` | Finish the frame |
| `SLPWOW-FR-WS-NAR-EE-01` | Three-box original retell |
| `SLPWOW-FR-WS-PA-PK-01` | Same first sound? |
| `SLPWOW-FR-WS-SOC-AD-01` | Optional saying-it-another-way |
| `SLPWOW-FR-WS-FLU-MX-01` | Topic the student picks; no fluency-shame tally |

### Printouts

| SKU | Job |
|---|---|
| `SLPWOW-FR-PO-CG-EI-01` | One-picture optional caregiver try |
| `SLPWOW-FR-PO-CG-PK-01` | Three optional tries |
| `SLPWOW-FR-PO-AAC-MX-01` | Partner board + blanks |
| `SLPWOW-FR-PO-MIX-MX-01` | Session map |
| `SLPWOW-FR-PO-ART-EE-01` | Clinician cue card (wait / model / choice) |
| `SLPWOW-FR-PO-FLU-MX-01` | Partner wait reminder |

### Word lists (original seeds)

| SKU | Grouping |
|---|---|
| `SLPWOW-FR-WL-ART-MX-01` | Picturable words that can show a final consonant |
| `SLPWOW-FR-WL-ART-MX-02` | Everyday words that can show an initial consonant |
| `SLPWOW-FR-WL-VOC-EE-01` | Mime-able verbs |
| `SLPWOW-FR-WL-VOC-AD-01` | Hallway / classroom nouns (teen) |
| `SLPWOW-FR-WL-SYN-LE-01` | Regular-past frames (optional) |
| `SLPWOW-FR-WL-NAR-MX-01` | Neutral story-bone prompts |

Lists: [`briefs/word-lists.md`](briefs/word-lists.md). Do not replace seeds with a web scrape.

### Report templates

| SKU | Job |
|---|---|
| `SLPWOW-FR-RT-DOC-MX-01` | Session snapshot |
| `SLPWOW-FR-RT-DOC-MX-02` | Observation-only progress note |
| `SLPWOW-FR-RT-DOC-MX-03` | Contact log |
| `SLPWOW-FR-RT-DOC-MX-04` | Information I still need |

## Claims in one screen

These materials **do not** diagnose, screen, or determine eligibility. They **do not** replace a licensed SLP. Tallies are session notes, not scores. Age bands are design targets. Home use happens only if the treating clinician sends the page. Fluency pages do not treat stuttering. Report shells are empty on purpose.

Full text: [`CLAIMS_GUARDRAILS.md`](CLAIMS_GUARDRAILS.md). Footer copy lives in §4. Reviewer refuse list lives in §12.

## Originality in one screen

Write the page. Do not recreate a marketplace packet, a Super Duper / Linguisystems / Boom look-alike, or a Facebook-group favorite. Ordinary English is not a publisher’s list; a published sequence with their jokes and art is. If you cannot say who wrote the sentence, delete it.

## What is not in this folder (on purpose)

- Designed PDF art
- Copyrighted worksheet text from the web
- ASHA or test-manual tables
- Live COSMOS Core / ledger / service changes
- A second “parent diagnosis” line

## Checks

From repo root:

```
python3 content/slpwow-free-resources-curriculum/check_curriculum.py
```

The checker proves the files exist, the index links resolve, first-wave SKUs are listed once, and student-facing briefs do not ship banned product-claim phrases outside the guardrails file.

## Ownership

Content lead: this pack. Design does not start until a SKU passes `PREPUBLISH.md`. Keith remains money, credentials, and publish-click. COSMOS Core is unchanged.
