# Editor report — creatine research landscape

**Series:** `content/creatine-research-landscape/`  
**PR:** #498 (draft; do not merge without human review)  
**Editor pass:** 2026-09-14  
**Frontmatter:** `voice_check: edited` on all 52 drafts  
**Linter:** `python3 content/creatine-research-landscape/verify_landscape.py` → PASS

## Mandate

Quality over speed. No disease claims; no personal dosing or “what to take”
speech; keep numbers inside named study methods; human essay voice with the
existing claim fence (CRL-02). Mark the pack editor-reviewed without inventing
sources or turning the landscape into a supplement guide.

## Scope

| Item | Count |
|------|------:|
| Draft essays (`draft-*.md`) | 52 |
| Supporting docs (`README.md`, `MANIFEST.toml`) | reviewed, not re-authored |
| Word floor (≥400 per draft) | all drafts pass |
| Required sections (Learning aims, What this draft does not claim, Sources, See also) | all drafts pass |

## Claims fence audit

**Automated tripwire** (`verify_landscape.py`): draft count, disclaimer needle,
`claims: none`, `kind: educational-landscape`, required headings, word floor,
banned disease/prescription regexes, and condition-name windows. Re-run after any
edit.

**Manual pass (disease language):**

- No draft closes on creatine as treating, curing, preventing, or managing a
  named condition. Stages 6–7 (healthy-volunteer safety marks, brain pool, cognitive
  batteries, occupational map) were read with extra care for back-door indications.
- CRL-45 quotes Rae et al. (2003) title wording (“improves brain performance”)
  only as **authors’ title**, explicitly not this series’ claim.
- CRL-12 names SLC6A6 medical-genetics chapters only to refuse them; no
  condition names appear as indications.
- Dose numbers (e.g. Hultman 1996 schedules, Rae 5 g/day) appear only as
  **reported protocol fields**, with “does not claim” sections refusing personal
  adoption (CRL-19, CRL-20, CRL-52).

**Prescription watch (manual):** scanned for “you should take,” stacking advice,
and structure/function completions. CRL-38 previously used “You should also cite”
in a citation-hygiene sense; rephrased to avoid prescription-shaped “you should”
while keeping the methods point.

## Voice and grammar

The incoming stack already matched CRL-02 voice: dry, specific, methods-first,
visible uncertainty, first-person as reader-not-testimonial.

**Copy edits in this pass:**

| Draft | Change |
|-------|--------|
| `draft-38-caffeine-co-use.md` | “You should also cite the protocol” → “A careful citation also names the protocol” |

No other mechanical grammar issues required rewriting in a full-folder read
(articles, doubled spaces, banned regex trips). No draft needed a disclaimer
rewrite.

**Frontmatter:** added `voice_check: edited` immediately after `claims: none` on
every draft. `verify_landscape.py` now requires `voice_check: edited` so a
future author cannot ship without an editor flag.

## Files touched (this editor commit)

- All 52 `draft-*.md` files — `voice_check: edited`
- `draft-38-caffeine-co-use.md` — prescription-shaped “you should” removed
- `verify_landscape.py` — enforce `voice_check: edited`
- `EDITOR_REPORT.md` — this file

## Residual risks (human still required)

The linter cannot catch a sentence that *implies* an indication without forbidden
verbs. Stage 7 (brain/cognitive/occupational) and CRL-52 (one-page summary) are
the highest-risk zones if a later writer adds a “helpful” closing line. Re-read any
new paragraph with CRL-02’s test: if the only defense is “the reader will know what
we meant,” delete or fence it.

Industry-adjacent funding and position-stand citations remain explicitly hedged;
this pass did not add new primary literature.

## Sign-off

Claims posture unchanged: `educational-landscape`, `claims: none`. Series remains
staged educational content, not product or clinical guidance.

**Editor:** Cursor cloud agent (grammar/voice/claims fence pass)  
**voice_check:** `edited`
