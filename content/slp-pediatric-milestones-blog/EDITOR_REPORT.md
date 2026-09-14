# Editor report — SLPWOW pediatric milestones

**Pass date:** 2026-09-14  
**Branch:** `cursor/slp-pediatric-milestones-editor-3a4c` (stacked on `cursor/slp-pediatric-milestones-blog-00eb`, writer PR #317)  
**Editor:** Cloud agent (EDITOR role)

## Verdict: proceed (not a stub pack)

| Check | Result |
|-------|--------|
| Articles in `articles/` | 42 |
| Stub / placeholder bodies | **0** |
| `check_pack.py` (word floor, disclaimer, banned diagnosis lines, slop scan) | **OK** |
| Hard-ban regex hits (`your child has…`, `causes autism`, etc.) | **0** |
| Style-guide slop in bodies (`delve`, `leverage`, `whether you're a`, …) | **0** |
| `unlock` in bodies (post-pass) | **0** |

**HOLD not issued.** Full parent-facing longform with disclaimers and sourced milestone language.

## Summary

| Metric | Count |
|--------|------:|
| Drafts reviewed (full read + pack scan) | 42 |
| Drafts updated (`voice_check: edited` + `voice_check_date: 2026-09-14`) | 42 |
| Articles with prose line edits in this pass | 18 |
| Pack metadata files updated | 4 (`INDEX.md`, `MANIFEST.md`, `EDITOR_REPORT.md`, this report) |

## What was fixed

### Front matter

- Replaced `voice_check: human` with `voice_check: edited` and added `voice_check_date: 2026-09-14` on every article.
- Removed duplicate ASHA milestones URL in `articles/20-questions-asking-and-answering.md`.

### Grammar / voice / guardrails (targeted)

| File | Change |
|------|--------|
| `02-birth-to-three-months-first-sounds.md` | Mixed metaphor on hearing → “turns toward you when you speak”; “forehead” typo → “on your phone.” |
| `04-seven-to-nine-months-babble.md` | CDC item quote: “her name” → “their name.” |
| `05-nine-to-twelve-months-pointing-names.md` | Same pronoun consistency on 9-month item. |
| `08-eighteen-to-twenty-four-months-two-words.md` | Editorial “we bother” → “why speech sounds matter.” |
| `12-five-years-narratives-and-rhymes.md` | “her name” → “their name” on cognitive line. |
| `13-speech-sounds-clear-enough.md` | “What we can do” → “This essay can say.” |
| `19-play-is-language-practice.md` | Missing verb on floor-time line; “SLPWOW” → “this series.” |
| `21-little-grammar-ing-plurals-past.md` | “we fill them in” → “listeners fill them in.” |
| `24-late-talking-what-studies-measured.md` | Corporate “we cannot tell” / “we do not stamp” → child- and series-neutral wording. |
| `25-repeating-sounds-ordinary-disfluency.md` | “lists fluency” → “practice includes fluency.” |
| `26-a-hoarse-or-tired-voice.md` | Trimmed duplicate teacher-microphone beat; kept one environmental-kindness thread. |
| `28-books-and-the-talk-around-them.md` | “a ISBN” → “an ISBN”; “clumsy English and a living Spanish” → clearer bilingual sentence. |
| `33-friends-pretend-social-communication.md` | “hides in your leg” → “clings to your leg.” |
| `37-pacifiers-cups-and-mouths.md` | Banned “unlock” → “produce.” |
| `39-when-someone-says-wait-and-see.md` | Agreement fix on late-talking groups; plan template uses parent “I” on receipt lines; plan example without editorial “we.” |
| `41-pictures-signs-and-aac.md` | Myth line “If we give” → “If you give”; AAC “unlocks” → “automatically leads to”; repaired “Who decides” sentence fragment. |

### Preserved

- Intentional editorial *We will not…* refusal blocks (`19`, `24`, `31`, `33`, `40`) where they refuse diagnosis, protocols, or T-shirt labels.
- Disclaimers that mention diagnosis only to negate scope (not to label the reader’s child).
- All citations, slugs, `status: draft`, and educational footers.

## Voice notes (no full rewrite required)

- Openings are scene-, checklist-, or visit-led; scare-site and brochure tone are absent.
- Cross-refs use mixed `essay 01` vs `essay 30` numbering; harmless for parents; normalize in a future ops pass if import tooling needs two digits everywhere.
- `[VERIFY]` markers remain where the writer flagged unsettled URLs or literature (`29`, `31`, `21`) — hold for print, per `INDEX.md`.

## Remaining weak spots (out of editor scope)

| Area | Note |
|------|------|
| Licensed clinical sign-off | Required before live slpwow.com (`WP_IMPORT.md`, `CLAIMS_GUARDRAILS.md`). |
| Essay cross-ref style | Optional two-digit normalization (`essay 09` vs `essay 9`). |
| Word-count floor | `check_pack.py` enforces ≥650 words; shortest pieces are still above floor. |

## Articles flagged for extra care (copy already honest)

| Slug | Note |
|------|------|
| `late-talking-what-studies-measured` | Research description vs parent T-shirt; no label applied to reader’s child. |
| `friends-pretend-social-communication` | Social domain without naming conditions. |
| `what-happens-at-an-slp-visit` | Describes evaluation vs diagnosis in plain language. |
| `parent-observation-list-not-a-test` | Kitchen list explicitly not a screen or score. |

## Not in scope

- No WordPress publish actions.
- No COSMOS core / live tree paths.
- No new clinical claims or milestone numbers.

## Verification commands (reproducible)

```bash
python3 content/slp-pediatric-milestones-blog/check_pack.py
rg -c 'voice_check: edited' content/slp-pediatric-milestones-blog/articles | wc -l   # expect 42
rg -i 'unlock|delve|leverage|whether you.re a' content/slp-pediatric-milestones-blog/articles || true
rg -i 'your child has (a |an )?(speech delay|language disorder|autism)' content/slp-pediatric-milestones-blog/articles || true
```
