# Editor report — adaptogens history (claims-guarded)

**Series:** `content/adaptogens-history-claims-guarded/`  
**PR:** #314 (draft; do not merge without human review)  
**Editor pass:** 2026-09-14  
**Frontmatter:** `voice_check: edited` on all 45 drafts  
**Linter:** `python3 content/adaptogens-history-claims-guarded/tools/lint_claims.py` → OK

## Mandate

Quality over speed. Strict claims fence; no disease language used as payoff; grammar and
human-essay voice; mark the series as editor-reviewed without changing the historical
argument or inventing sources.

## Scope

| Item | Count |
|------|------:|
| Draft essays (`stage-*/[0-9][0-9]-*.md`) | 45 |
| Supporting docs (`GUARDRAILS.md`, `CITATIONS.md`, `README.md`) | reviewed, not re-authored |
| Word floor (≥650) | all drafts pass |
| Claims box (≥3 bullets + refuse sentence) | all drafts pass |

## Claims fence audit

**Automated tripwire** (`tools/lint_claims.py`): forbidden cure/treat/prevent patterns,
wellness-bot clusters, missing frontmatter, duplicate slugs/titles/openings, and Claims-box
structure. Re-run after any edit.

**Manual pass (disease language):**

- No draft finishes a sentence that names a modern condition as something a plant
  *treats*, *cures*, or *prevents*. Condition words that appear on the page do so as
  **refusals**, **quoted aisle talk**, **ICD/regulatory contrast**, or **meta-commentary**
  (for example draft 27 quotes a friend's "adaptogen for anxiety" only to refuse it;
  draft 03 names diabetes and tumors as examples of what the Soviet definition did *not*
  say).
- Figurative uses retained where they are not disease claims (`identity anxiety` in draft 15;
  `translation fatigue` in draft 12).
- Endpoint vocabulary (`fatigue-and-attention`, asthenia vs ICD-10) appears only with
  regulatory or historiographic framing, not as product promises.
- No doses, stacks, "what to take," or structure/function completions added in this pass.

**Sly-phrase watch (manual):** scanned for immune-boost, clinically proven, helps with
[condition], beneficial for, and similar aisle leaks. None required rewriting in body copy.

## Voice and grammar

The incoming stack already matched `GUARDRAILS.md` voice: specific objects, dry humor,
visible uncertainty, first-person as reader-not-testimonial.

**Copy edits in this pass:**

| Draft | Change |
|-------|--------|
| 23 `reishi-as-literature` | Article: "a honest" → "an honest" (fungus farm sentence) |

No other mechanical grammar issues surfaced in a full-folder scan (articles, double spaces,
forbidden bot clusters). No draft required a claims-box rewrite.

**Frontmatter:** added `voice_check: edited` immediately after `status: draft` on every
essay. `lint_claims.py` now requires `voice_check: edited` so a future author cannot
accidentally ship without an editor flag.

## Files touched (this editor commit)

- All 45 draft `.md` files — `voice_check: edited`
- `stage-03-east-asian-materia/23-reishi-as-literature.md` — grammar fix
- `tools/lint_claims.py` — enforce `voice_check`
- `MANIFEST.toml` — regenerated (`--write-manifest`)
- `EDITOR_REPORT.md` — this file

## Residual risks (human still required)

The linter cannot catch a sentence that *implies* an indication without forbidden verbs.
Stages 4–5 (South Asian plants, law/aisle language) are the highest-risk zones for a later
writer adding a "helpful" closing line. Re-read any new paragraph with draft 01's test:
if the only defense is "the reader will know what we meant," delete or fence it.

Dating disputes (1947 vs 1958) and secondary headcounts remain explicitly hedged per
`CITATIONS.md`; this pass did not add archival evidence.

## Sign-off

Claims posture unchanged: `educational-ethnobotany`, `status: draft`. Series remains staged
proposal content, not product or clinical guidance.

**Editor:** Cursor cloud agent (grammar/voice/claims fence pass)  
**voice_check:** `edited`
