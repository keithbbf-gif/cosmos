# Manifest — `content/group-therapy-history/`

Publishable pack for **staging** review. Count target: **≥40**. This pack: **44**.

Do not write to live wowtherapies.com from this folder.

## Ops (not posts)

| File | Purpose |
| --- | --- |
| `INDEX.md` | Calendar, cadence, waves |
| `MANIFEST.md` | This inventory |
| `STYLE_GUIDE.md` | Voice bans + `voice_check: human` / `edited` |
| `EDITOR_REPORT.md` | Editor pass log (stacked on writer PR) |
| `CLAIMS_GUARDRAILS.md` | On-site never-say list |
| `BIBLIOGRAPHY.md` | Consolidated citations |
| `PORTRAIT_SOURCES.md` | PD/CC or honest blank |
| `PHOTO_NOTES.md` | Image rules; no fake faces |
| `WP_IMPORT.md` | Staging import only |

## Required YAML on each draft

`title`, `slug`, `meta_description`, `tags`, `type` (`era`|`figure`), `order`, `portrait`, `citations`, `status`, `voice_check`, `last_verified`

Required body: educational note (not a diagnosis, not a treatment plan, not a substitute for a licensed clinician).

## Drafts (44)

| # | Path | Slug | type | portrait |
| --- | --- | --- | --- | --- |
| 01 | `drafts/01-circles-before-the-clinic.md` | circles-before-the-clinic | era | none |
| 02 | `drafts/02-pratt-class-method.md` | pratt-class-method | era | none |
| 03 | `drafts/03-emmanuel-church-basement.md` | emmanuel-church-basement | era | none |
| 04 | `drafts/04-interwar-hospital-groups.md` | interwar-hospital-groups | era | none |
| 05 | `drafts/05-northfield-experiments.md` | northfield-experiments | era | none |
| 06 | `drafts/06-tavistock-group-relations.md` | tavistock-group-relations | era | none |
| 07 | `drafts/07-aa-meeting-not-clinic.md` | aa-meeting-not-clinic | era | none |
| 08 | `drafts/08-psychodrama-stage.md` | psychodrama-stage | era | none |
| 09 | `drafts/09-childrens-activity-groups.md` | childrens-activity-groups | era | none |
| 10 | `drafts/10-bethel-t-group.md` | bethel-t-group | era | none |
| 11 | `drafts/11-encounter-culture.md` | encounter-culture | era | none |
| 12 | `drafts/12-after-encounter-harm.md` | after-encounter-harm | era | none |
| 13 | `drafts/13-cmhc-ward-group.md` | cmhc-ward-group | era | none |
| 14 | `drafts/14-yalom-1970-textbook-era.md` | yalom-1970-textbook-era | era | none |
| 15 | `drafts/15-psychoeducation-skills-multifamily.md` | psychoeducation-skills-multifamily | era | none |
| 16 | `drafts/16-agpa-research-managed-care.md` | agpa-research-managed-care | era | none |
| 17 | `drafts/17-joseph-pratt.md` | joseph-pratt | figure | confirm |
| 18 | `drafts/18-trigant-burrow.md` | trigant-burrow | figure | none |
| 19 | `drafts/19-jacob-moreno.md` | jacob-moreno | figure | confirm |
| 20 | `drafts/20-zerka-moreno.md` | zerka-moreno | figure | none |
| 21 | `drafts/21-s-h-foulkes.md` | s-h-foulkes | figure | none |
| 22 | `drafts/22-wilfred-bion.md` | wilfred-bion | figure | none |
| 23 | `drafts/23-tom-main.md` | tom-main | figure | none |
| 24 | `drafts/24-maxwell-jones.md` | maxwell-jones | figure | none |
| 25 | `drafts/25-samuel-slavson.md` | samuel-slavson | figure | none |
| 26 | `drafts/26-kurt-lewin.md` | kurt-lewin | figure | confirm |
| 27 | `drafts/27-l-cody-marsh.md` | l-cody-marsh | figure | none |
| 28 | `drafts/28-louis-wender.md` | louis-wender | figure | none |
| 29 | `drafts/29-grace-coyle.md` | grace-coyle | figure | none |
| 30 | `drafts/30-gisela-konopka.md` | gisela-konopka | figure | none |
| 31 | `drafts/31-alexander-wolf.md` | alexander-wolf | figure | none |
| 32 | `drafts/32-helen-durkin.md` | helen-durkin | figure | none |
| 33 | `drafts/33-a-k-rice.md` | a-k-rice | figure | none |
| 34 | `drafts/34-carl-rogers-encounter.md` | carl-rogers-encounter | figure | none |
| 35 | `drafts/35-irvin-yalom-group.md` | irvin-yalom-group | figure | none |
| 36 | `drafts/36-morton-lieberman.md` | morton-lieberman | figure | none |
| 37 | `drafts/37-eric-berne.md` | eric-berne | figure | none |
| 38 | `drafts/38-marsha-linehan-skills-group.md` | marsha-linehan-skills-group | figure | none |
| 39 | `drafts/39-william-mcfarlane.md` | william-mcfarlane | figure | none |
| 40 | `drafts/40-anne-alonso.md` | anne-alonso | figure | none |
| 41 | `drafts/41-louis-ormont.md` | louis-ormont | figure | none |
| 42 | `drafts/42-j-scott-rutan.md` | j-scott-rutan | figure | none |
| 43 | `drafts/43-saul-scheidlinger.md` | saul-scheidlinger | figure | none |
| 44 | `drafts/44-gary-burlingame.md` | gary-burlingame | figure | none |

## QA script

`check_pack.py` (this folder) — counts files, required YAML, disclaimer, banned phrases, minimum word counts.
