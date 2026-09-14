# Sports nutrition / protein R&D drafts (Jan 2020–present)

Working drafts for a long-form series on **protein in sport**: how much, when, from what, and for whom — written from papers published or still governing practice from January 2020 through September 2026.

These are **not** a product, a meal plan, or medical advice. They are staged copy for editors and reviewers.

## How to read this folder

Start with `_editorial/CLAIMS_POLICY.md`. Then the source pack. Then any draft.

Each draft file has YAML front matter (`status: draft`, `voice_check: edited`, `claims: no-disease`, `stage`, sources). Body copy is meant to sound like a coach or sports RD, not a supplement label.

| Stage | What it is | Count |
| --- | --- | --- |
| 1 Foundations | Daily dose, per-meal dose, distribution, timing, quality scores | 8 |
| 2 Training | Strength, endurance, concurrent, overnight, cold, disuse | 7 |
| 3 Populations | Female athletes, cycle, masters, youth, weight-class, team, aesthetic | 7 |
| 4 Sources | Dairy, plants, soy, mycoprotein, collagen, insect, future proteins | 8 |
| 5 Environments | Deficit, energy availability, travel, heat, altitude, tactical, fasting | 7 |
| 6 Practice | Food-first, labels, contamination, carbs+protein, high intakes, consensus, open questions | 8 |

**45 drafts.** Plus this README and the editorial pack. Nothing here is cleared for a consumer site.

## What changed after 2020 (the short version)

The 2017 ISSN protein stand and the 2018 Morton meta-regression are still the floor most practitioners stand on: roughly **1.4–2.0 g/kg/day** for most exercising people, with the hypertrophy increment from extra protein looking small once you are already eating enough and lifting. What the 2020s added is less a new number than a set of *corrections*:

- A single large protein feeding can keep muscle protein synthesis elevated well past the old 3–4 hour window (Trommelen 2023). That does not crown 100 g as a hypertrophy protocol.
- Plant patterns can support training adaptations when **total protein is matched** and the diet is not accidentally low-leucine (Hevia-Larraín 2021; Pinckaers 2021–2024).
- Energy deficit changes the problem. Whole-body needs rise; a 20 g whey shake that looked tidy in energy balance can be a rounding error in a cut or a field op (Gwin 2020–2024).
- Cold-water immersion after lifting is not free. It can blunt the use of the protein you just ate (Fuchs 2020, 2025).
- Consensus documents got more specific about *who*: UEFA 2021 for football, IOC REDs 2023 for energy availability, ISSN EAA 2023 for free-form amino acids.

## Claims

No disease claims. See `_editorial/CLAIMS_POLICY.md`.

## Status

`draft` — editor pass complete (`voice_check: edited`); credentialed reviewer still required before any public use. Re-run `python3 content/sports-nutrition-rd-2020/tools/lint_claims.py` after edits.
