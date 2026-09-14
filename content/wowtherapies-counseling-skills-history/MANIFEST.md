# Manifest — `content/wowtherapies-counseling-skills-history/`

**Staged** pack for review. Count target: **≥40**. This pack: **44**.

Do not write to live wowtherapies.com from this folder.

## Ops (not posts)

| File | Purpose |
| --- | --- |
| `INDEX.md` | Calendar, cadence, waves |
| `MANIFEST.md` | This inventory |
| `STYLE_GUIDE.md` | Voice bans + `voice_check: human` |
| `CLAIMS_GUARDRAILS.md` | On-site never-say list |
| `BIBLIOGRAPHY.md` | Consolidated citations |
| `PORTRAIT_SOURCES.md` | PD/CC or honest blank |
| `PHOTO_NOTES.md` | Image rules; no fake faces |
| `WP_IMPORT.md` | Staging import only |
| `STAGE.md` | Draft-status contract |
| `README.md` | Door |

## Required YAML on each article

`title`, `slug`, `meta_description`, `tags`, `type` (`skill`|`modality`|`figure`), `order`, `portrait` (`pd`|`cc`|`confirm`|`none`), `citations`, `status`, `voice_check`, `last_verified`

Required body: educational note (not a diagnosis, not a treatment plan, not a substitute for a licensed clinician).

`status` on this pass: **`draft`**.

## Articles (44)

| # | Path | Slug | type | portrait |
| --- | --- | --- | --- | --- |
| 01 | `articles/01-listening-became-a-technique.md` | listening-became-a-technique | skill | none |
| 02 | `articles/02-empathy-from-einfuhlung-to-scales.md` | empathy-from-einfuhlung-to-scales | skill | confirm |
| 03 | `articles/03-reflection-and-the-restatement-problem.md` | reflection-and-the-restatement-problem | skill | none |
| 04 | `articles/04-questions-socratic-circular-miracle.md` | questions-socratic-circular-miracle | skill | none |
| 05 | `articles/05-silence-pacing-unfilled-second.md` | silence-pacing-unfilled-second | skill | none |
| 06 | `articles/06-congruence-as-a-technical-claim.md` | congruence-as-a-technical-claim | skill | none |
| 07 | `articles/07-unconditional-positive-regard.md` | unconditional-positive-regard | skill | none |
| 08 | `articles/08-confrontation-immediacy-disclosure.md` | confrontation-immediacy-disclosure | skill | none |
| 09 | `articles/09-working-alliance-bordin.md` | working-alliance-bordin | skill | none |
| 10 | `articles/10-microskills-ivey.md` | microskills-ivey | skill | none |
| 11 | `articles/11-accurate-empathy-scales.md` | accurate-empathy-scales | skill | none |
| 12 | `articles/12-oars-mi-skill-grammar.md` | oars-mi-skill-grammar | skill | none |
| 13 | `articles/13-counseling-in-speech-language-pathology.md` | counseling-in-speech-language-pathology | skill | none |
| 14 | `articles/14-counseling-families-communication-difference.md` | counseling-families-communication-difference | skill | none |
| 15 | `articles/15-grief-adjustment-communication-change.md` | grief-adjustment-communication-change | skill | none |
| 16 | `articles/16-cultural-humility-as-a-skill.md` | cultural-humility-as-a-skill | skill | none |
| 17 | `articles/17-counseling-skills-outside-the-license.md` | counseling-skills-outside-the-license | skill | none |
| 18 | `articles/18-common-factors-dodo-bird.md` | common-factors-dodo-bird | skill | confirm |
| 19 | `articles/19-person-centered-as-skill-package.md` | person-centered-as-skill-package | modality | none |
| 20 | `articles/20-psychodynamic-listening-modality.md` | psychodynamic-listening-modality | modality | none |
| 21 | `articles/21-behavioral-counseling-skills.md` | behavioral-counseling-skills | modality | none |
| 22 | `articles/22-cognitive-counseling-skill-set.md` | cognitive-counseling-skill-set | modality | none |
| 23 | `articles/23-reality-therapy-glasser.md` | reality-therapy-glasser | modality | none |
| 24 | `articles/24-gestalt-contact-skills.md` | gestalt-contact-skills | modality | none |
| 25 | `articles/25-transactional-analysis-skill-language.md` | transactional-analysis-skill-language | modality | confirm |
| 26 | `articles/26-solution-focused-questioning.md` | solution-focused-questioning | modality | none |
| 27 | `articles/27-narrative-reauthoring.md` | narrative-reauthoring | modality | none |
| 28 | `articles/28-feminist-counseling-skills.md` | feminist-counseling-skills | modality | none |
| 29 | `articles/29-multicultural-counseling-competencies.md` | multicultural-counseling-competencies | modality | none |
| 30 | `articles/30-motivational-interviewing-modality.md` | motivational-interviewing-modality | modality | none |
| 31 | `articles/31-crisis-counseling-history.md` | crisis-counseling-history | modality | none |
| 32 | `articles/32-vocational-career-counseling-skills.md` | vocational-career-counseling-skills | modality | confirm |
| 33 | `articles/33-school-counseling-skill-lineage.md` | school-counseling-skill-lineage | modality | none |
| 34 | `articles/34-rehabilitation-counseling.md` | rehabilitation-counseling | modality | none |
| 35 | `articles/35-integrative-counseling-eclecticism.md` | integrative-counseling-eclecticism | modality | none |
| 36 | `articles/36-david-luterman.md` | david-luterman | figure | none |
| 37 | `articles/37-audrey-holland.md` | audrey-holland | figure | none |
| 38 | `articles/38-allen-e-ivey.md` | allen-e-ivey | figure | none |
| 39 | `articles/39-william-r-miller.md` | william-r-miller | figure | none |
| 40 | `articles/40-clara-e-hill.md` | clara-e-hill | figure | none |
| 41 | `articles/41-gerard-egan.md` | gerard-egan | figure | none |
| 42 | `articles/42-robert-carkhuff.md` | robert-carkhuff | figure | none |
| 43 | `articles/43-derald-wing-sue.md` | derald-wing-sue | figure | none |
| 44 | `articles/44-michael-white.md` | michael-white | figure | none |

## QA script

`check_pack.py` (this folder) — counts files, required YAML, disclaimer, banned phrases, minimum word counts.
