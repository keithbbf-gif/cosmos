# Manifest — `content/family-systems-therapy-history/`

Staged pack for **staging** review. Count target: **≥40**. This pack: **44**.

Do not write to live wowtherapies.com from this folder.

## Ops (not posts)

| File | Purpose |
| --- | --- |
| `INDEX.md` | Calendar, cadence, waves |
| `MANIFEST.md` | This inventory |
| `STYLE_GUIDE.md` | Voice bans + `voice_check: human` / `edited` |
| `CLAIMS_GUARDRAILS.md` | On-site never-say list |
| `BIBLIOGRAPHY.md` | Consolidated citations |
| `PORTRAIT_SOURCES.md` | PD/CC or honest blank |
| `PHOTO_NOTES.md` | Image rules; no fake faces |
| `WP_IMPORT.md` | Staging import only |

## Required YAML on each article

`title`, `slug`, `meta_description`, `tags`, `type` (`era`|`figure`), `order`, `portrait` (`pd`|`cc`|`confirm`|`none`), `citations`, `status`, `voice_check`, `last_verified`

Required body: educational note (not a diagnosis, not a treatment plan, not a substitute for a licensed clinician).

## Articles (44)

| # | Path | Slug | type | portrait |
| --- | --- | --- | --- | --- |
| 01 | `articles/01-before-the-family-was-a-patient.md` | before-the-family-was-a-patient | era | none |
| 02 | `articles/02-child-guidance-invites-the-parents.md` | child-guidance-invites-the-parents | era | none |
| 03 | `articles/03-schizophrenogenic-theories.md` | schizophrenogenic-theories | era | none |
| 04 | `articles/04-palo-alto-double-bind.md` | palo-alto-double-bind | era | none |
| 05 | `articles/05-mri-brief-interactional.md` | mri-brief-interactional | era | none |
| 06 | `articles/06-bowen-georgetown-diagram.md` | bowen-georgetown-diagram | era | none |
| 07 | `articles/07-satir-experiential-growth.md` | satir-experiential-growth | era | none |
| 08 | `articles/08-wiltwyck-philadelphia-structure.md` | wiltwyck-philadelphia-structure | era | none |
| 09 | `articles/09-strategic-haley-madanes.md` | strategic-haley-madanes | era | none |
| 10 | `articles/10-milan-systemic.md` | milan-systemic | era | none |
| 11 | `articles/11-contextual-nagy-loyalty.md` | contextual-nagy-loyalty | era | none |
| 12 | `articles/12-feminist-revolt-family-therapy.md` | feminist-revolt-family-therapy | era | none |
| 13 | `articles/13-milwaukee-solution-focused.md` | milwaukee-solution-focused | era | none |
| 14 | `articles/14-narrative-white-epston.md` | narrative-white-epston | era | none |
| 15 | `articles/15-after-the-mirror-race-class-consent.md` | after-the-mirror-race-class-consent | era | none |
| 16 | `articles/16-manuals-evidence-profession.md` | manuals-evidence-profession | era | none |
| 17 | `articles/17-nathan-ackerman.md` | nathan-ackerman | figure | none |
| 18 | `articles/18-gregory-bateson.md` | gregory-bateson | figure | none |
| 19 | `articles/19-don-jackson.md` | don-jackson | figure | none |
| 20 | `articles/20-jay-haley.md` | jay-haley | figure | none |
| 21 | `articles/21-virginia-satir.md` | virginia-satir | figure | none |
| 22 | `articles/22-murray-bowen.md` | murray-bowen | figure | none |
| 23 | `articles/23-salvador-minuchin.md` | salvador-minuchin | figure | none |
| 24 | `articles/24-carl-whitaker.md` | carl-whitaker | figure | none |
| 25 | `articles/25-ivan-boszormenyi-nagy.md` | ivan-boszormenyi-nagy | figure | none |
| 26 | `articles/26-mara-selvini-palazzoli.md` | mara-selvini-palazzoli | figure | none |
| 27 | `articles/27-cloe-madanes.md` | cloe-madanes | figure | none |
| 28 | `articles/28-john-weakland.md` | john-weakland | figure | none |
| 29 | `articles/29-paul-watzlawick.md` | paul-watzlawick | figure | none |
| 30 | `articles/30-steve-de-shazer.md` | steve-de-shazer | figure | none |
| 31 | `articles/31-insoo-kim-berg.md` | insoo-kim-berg | figure | none |
| 32 | `articles/32-michael-white.md` | michael-white | figure | none |
| 33 | `articles/33-david-epston.md` | david-epston | figure | none |
| 34 | `articles/34-monica-mcgoldrick.md` | monica-mcgoldrick | figure | none |
| 35 | `articles/35-betty-carter.md` | betty-carter | figure | none |
| 36 | `articles/36-lynn-hoffman.md` | lynn-hoffman | figure | none |
| 37 | `articles/37-sue-johnson.md` | sue-johnson | figure | none |
| 38 | `articles/38-nancy-boyd-franklin.md` | nancy-boyd-franklin | figure | none |
| 39 | `articles/39-celia-jaes-falicov.md` | celia-jaes-falicov | figure | none |
| 40 | `articles/40-pauline-boss.md` | pauline-boss | figure | none |
| 41 | `articles/41-harry-aponte.md` | harry-aponte | figure | none |
| 42 | `articles/42-lyman-wynne.md` | lyman-wynne | figure | none |
| 43 | `articles/43-froma-walsh.md` | froma-walsh | figure | none |
| 44 | `articles/44-kenneth-hardy.md` | kenneth-hardy | figure | none |

## QA script

`check_pack.py` (this folder) — counts files, required YAML, disclaimer, banned phrases, minimum word counts.
