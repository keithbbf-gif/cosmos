# Protein powder label literacy

**Status:** staged drafts, not published labeling, not a COSMOS Core change.  
**Pack path:** `content/protein-supplements-label-literacy/`  
**Count:** 48 numbered lessons (`PSL-01` … `PSL-48`) across eight stages.  
**Law frame:** United States — Federal Food, Drug, and Cosmetic Act as amended by the Dietary Supplement Health and Education Act of 1994 (DSHEA).  
**Hard lock:** no disease claims. This pack does not claim that any protein powder diagnoses, treats, cures, or prevents any disease.

## What this pack is

A consumer curriculum for reading a protein-powder tub the way a careful adult should: panel first, marketing last; grams and serving size before stars and seals; statute before slogan.

Each `PSL-*.md` file is a **standalone lesson**. You can open one draft in isolation. The series is still **staged**: later lessons assume earlier ones. Do not shuffle them into a social-feed pile and call that a course.

## What this pack is not

- A product label, Supplement Facts panel, or structure/function claim notification.
- Medical advice, a diet plan, a training plan, or a recommendation to buy or avoid a named commercial brand.
- A claim that protein powder is a drug, a therapy, or a substitute for food or clinical care.
- Permission for a brand, an affiliate, or an agent to paste these sentences onto a tub.

If a sentence here would be illegal or misleading **on a product**, it is written as **teaching about the rule**, not as a claim for a powder.

## Stages

| Stage | Folder | Lessons | Job |
| --- | --- | --- | --- |
| 1 | `stage-01-orientation` | PSL-01–05 | What a label is; how the series is staged; the disease-claim lock; who regulates the tub; food vs supplement vs drug. |
| 2 | `stage-02-dshea-frame` | PSL-06–10 | DSHEA in plain English; what FDA does not pre-approve; new dietary ingredients; 21 CFR 111; why serious-event duties are almost invisible on the panel. |
| 3 | `stage-03-facts-panel` | PSL-11–16 | Supplement Facts vs Nutrition Facts; scoops; protein grams and %DV; macros that are not protein; sugars; incidental nutrients. |
| 4 | `stage-04-protein-identity` | PSL-17–25 | Nitrogen × 6.25; amino lists; completeness; whey, casein, plants, collagen, other animals; free amino acids and spike literacy. |
| 5 | `stage-05-other-ingredients` | PSL-26–30 | Sweeteners, gums, enzymes, allergens, diet-identity marks. |
| 6 | `stage-06-claims` | PSL-31–35 | Structure/function vs disease; the mandatory disclaimer; “clinically studied”; nutrient-content claims; pictures and implied claims. |
| 7 | `stage-07-quality-signals` | PSL-36–40 | Third-party seals; organic / non-GMO / “natural”; metals and Prop 65; lot codes; certificates of analysis. |
| 8 | `stage-08-practice` | PSL-41–48 | Label math, cost per 25 g protein, three fictional worked labels, other-country panels, special populations, red-flag checklist. |

Canon files in `_canon/` are **not** lessons. They are the lock, the source list, and the glossary the lessons point at.

## How to read (one sitting)

1. Read `_canon/CLAIMS_LOCK.md` once.
2. Walk stages 1 → 8 in order.
3. Do the **Label drill** in each lesson. The drill is the point.
4. When a lesson quotes a statute or a CFR, treat the **official text** as authority. This pack is a map, not the Code.

## Front matter contract

Every `PSL-*.md` lesson carries YAML with at least:

- `id`, `slug`, `title`, `pack`, `stage`, `stage_slug`, `status: draft`
- `jurisdiction: US-FDA-DSHEA`
- `disease_claims: forbidden`
- `medical_advice: none`
- `prerequisites`, `next`

A machine gate lives at `tests/test_protein_label_literacy_pack.py`. It counts lessons, requires the lock sentences, and refuses promotional disease-claim phrasing.

## Voice

Plain, adult, specific. No miracle talk. No “as a doctor.” No invented brand prosecutions. Fictional labels in stage 8 are marked **FICTIONAL** and use made-up names.

## COSMOS note

This directory is educational content staged for review. It is not a live-tree runtime object, not a ledger event, and not a KDash panel. Do not wire it into Core because a folder exists.
