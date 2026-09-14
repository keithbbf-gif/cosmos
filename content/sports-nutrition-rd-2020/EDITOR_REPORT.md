# Editor report — sports nutrition / protein R&D (2020–present)

**Series:** `content/sports-nutrition-rd-2020/`  
**PR:** #392 (draft stack; this editor branch — do not merge without credentialed review)  
**Editor pass:** 2026-09-14  
**Frontmatter:** `voice_check: edited` on all 45 drafts  
**Linter:** `python3 content/sports-nutrition-rd-2020/tools/lint_claims.py` → OK

## Mandate

Quality over speed. Keep the **no-disease** fence (`claims: no-disease`); coach / sports-RD voice per `_editorial/VOICE_NOTES.md` and `CLAIMS_POLICY.md`; mark the series editor-reviewed without inventing sources or turning acute tracer papers into hypertrophy promises.

## Scope

| Item | Count |
|------|------:|
| Draft essays (`stage-*/[0-9][0-9]-*.md`) | 45 |
| Editorial pack (`_editorial/*`, `README.md`) | reviewed |
| Word floor (≥400 body words) | all drafts pass |
| `## Sources` with doi: or PMID: | all drafts pass |

## Claims fence audit

**Automated tripwire** (`tools/lint_claims.py`): `voice_check: edited`, `claims: no-disease`, title/H1 match, minimum length, sources block, bot-smell phrases, and forbidden disease-claim patterns (with refusal-context exceptions so “this draft does not treat REDs” does not false-positive).

**Manual pass (disease language):**

- No draft closes by promising that protein (or a source) **treats, cures, prevents, or heals** a disease or clinical condition. Condition words appear as **refusals**, **quoted label/aisle talk**, or **scope limits** (REDs, collagen PINP vs tendon MRI, kidney “safety” in healthy volunteers only).
- High-risk zones (REDs, deficit, disuse/rehab, collagen, soy hormones, high intakes, omega-3, Ramadan/metabolic disease) already carry explicit “I will not write…” or “What this is not” language; one addition in this pass (team match week).
- UEFA “immune function” floor and journal names containing *Cachexia Sarcopenia Muscle* are cited as literature, not sold as outcomes.

**Sly-phrase watch:** scanned for immune-boost, clinically proven (non-quoted), game-changer, biohack, unlock-your-potential, and tendon-healing payoffs. `40-label-literacy-spiking.md` keeps “clinically proven” only as **mock label copy** in quotes.

## Voice and grammar

Incoming copy already matched the brief: kitchen-table coach/RD tone, papers named with what they measured, willingness to say the field does not know.

**Copy edits in this pass:**

| Draft | Change |
|-------|--------|
| `stage-3-populations/21-team-sport-match-week.md` | Added **What this is not** — match-week protein vs illness/injury treatment |
| `stage-6-practice/38-food-first-vs-supplements.md` | Linked batch-tested powder to contamination draft; reinforced food-first as budget not purity test |

No duplicate H1s, no title/frontmatter mismatches, no bot-cluster openings. Grammar scan (articles, double spaces, forbidden marketing clusters) did not surface other mechanical fixes worth a silent rewrite.

**Frontmatter:** added `voice_check: edited` immediately after `status: draft` on every essay. Linter enforces it on future edits.

## Files touched (this editor commit)

- All 45 draft `.md` files — `voice_check: edited`
- `stage-3-populations/21-team-sport-match-week.md` — claims fence section
- `stage-6-practice/38-food-first-vs-supplements.md` — practice cross-link
- `tools/lint_claims.py` — new series tripwire
- `_editorial/MANIFEST.toml` — `voice_check`, `editor_pass`
- `README.md` — editor status and lint command
- `EDITOR_REPORT.md` — this file

## Residual risks (human still required)

The linter cannot catch a sentence that *implies* a medical outcome without forbidden verbs. Stages 5–6 (deficit, REDs, labels, high intakes) and stage 4 (collagen, soy aisle myths) are the highest-risk zones if a later writer adds a “helpful” closing line. Re-read new paragraphs with `01-daily-protein-targets.md` and `CLAIMS_POLICY.md` as the test.

Tracer and acute MPS papers (especially Trommelen 2023) will keep being misread on social media; the series already fences them — a public editor should still watch for headline drift.

Credentialed sports-medicine / RD sign-off is still required before consumer or athlete-facing publication.

## Sign-off

Claims posture unchanged: `claims: no-disease`, `status: draft`. Series remains staged proposal content, not product label or clinical guidance.

**Editor:** Cursor cloud agent (grammar/voice/claims fence pass)  
**voice_check:** `edited`
