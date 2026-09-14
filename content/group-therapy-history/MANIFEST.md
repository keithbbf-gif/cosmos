# Manifest — `content/group-therapy-history/`

Publishable pack for **staging** review. Count target: **≥40**. This pack: **44**.

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
| `README.md` | Door |
| `EDITOR_REPORT.md` | Editor pass sign-off (after `voice_check: edited`) |

## Required YAML on each article

`title`, `slug`, `meta_description`, `tags`, `type` (`era`|`figure`), `order`, `portrait` (`pd`|`cc`|`confirm`|`none`), `citations`, `status`, `voice_check`, `last_verified`

Required body: educational note (not a diagnosis, not a treatment plan, not a substitute for a licensed clinician).

## Articles (44)

| # | Path | Slug | type | portrait |
| --- | --- | --- | --- | --- |
| 01 | `articles/01-before-the-circle.md` | before-the-circle | era | none |
| 02 | `articles/02-pratt-classes-boston.md` | pratt-classes-boston | era | none |
| 03 | `articles/03-interwar-hospital-groups.md` | interwar-hospital-groups | era | none |
| 04 | `articles/04-psychodrama-rooms.md` | psychodrama-rooms | era | none |
| 05 | `articles/05-group-analysis-northfield.md` | group-analysis-northfield | era | none |
| 06 | `articles/06-bion-tavistock.md` | bion-tavistock | era | none |
| 07 | `articles/07-t-groups-ntl.md` | t-groups-ntl | era | none |
| 08 | `articles/08-encounter-boom.md` | encounter-boom | era | none |
| 09 | `articles/09-aa-mutual-aid.md` | aa-mutual-aid | era | none |
| 10 | `articles/10-therapeutic-community-cmhc.md` | therapeutic-community-cmhc | era | none |
| 11 | `articles/11-feminist-consciousness-raising.md` | feminist-consciousness-raising | era | none |
| 12 | `articles/12-child-activity-groups.md` | child-activity-groups | era | none |
| 13 | `articles/13-structured-cbt-groups.md` | structured-cbt-groups | era | none |
| 14 | `articles/14-agpa-profession.md` | agpa-profession | era | none |
| 15 | `articles/15-group-research-factors.md` | group-research-factors | era | none |
| 16 | `articles/16-telehealth-groups-history.md` | telehealth-groups-history | era | none |
| 17 | `articles/17-joseph-hersey-pratt.md` | joseph-hersey-pratt | figure | none |
| 18 | `articles/18-jacob-l-moreno.md` | jacob-l-moreno | figure | confirm |
| 19 | `articles/19-zerka-t-moreno.md` | zerka-t-moreno | figure | none |
| 20 | `articles/20-s-h-foulkes.md` | s-h-foulkes | figure | none |
| 21 | `articles/21-wilfred-bion.md` | wilfred-bion | figure | none |
| 22 | `articles/22-kurt-lewin.md` | kurt-lewin | figure | confirm |
| 23 | `articles/23-samuel-r-slavson.md` | samuel-r-slavson | figure | none |
| 24 | `articles/24-trigant-burrow.md` | trigant-burrow | figure | none |
| 25 | `articles/25-paul-schilder.md` | paul-schilder | figure | confirm |
| 26 | `articles/26-maxwell-jones.md` | maxwell-jones | figure | none |
| 27 | `articles/27-thomas-main.md` | thomas-main | figure | none |
| 28 | `articles/28-michael-balint.md` | michael-balint | figure | none |
| 29 | `articles/29-irvin-yalom-group.md` | irvin-yalom-group | figure | none |
| 30 | `articles/30-morton-a-lieberman.md` | morton-a-lieberman | figure | none |
| 31 | `articles/31-helen-e-durkin.md` | helen-e-durkin | figure | none |
| 32 | `articles/32-alexander-wolf.md` | alexander-wolf | figure | none |
| 33 | `articles/33-yvonne-agazarian.md` | yvonne-agazarian | figure | none |
| 34 | `articles/34-anne-alonso.md` | anne-alonso | figure | none |
| 35 | `articles/35-j-scott-rutan.md` | j-scott-rutan | figure | none |
| 36 | `articles/36-louis-ormont.md` | louis-ormont | figure | none |
| 37 | `articles/37-gisela-konopka.md` | gisela-konopka | figure | none |
| 38 | `articles/38-william-schwartz.md` | william-schwartz | figure | none |
| 39 | `articles/39-enrique-pichon-riviere.md` | enrique-pichon-riviere | figure | none |
| 40 | `articles/40-patrick-de-mare.md` | patrick-de-mare | figure | none |
| 41 | `articles/41-malcolm-pines.md` | malcolm-pines | figure | none |
| 42 | `articles/42-jerome-d-frank.md` | jerome-d-frank | figure | none |
| 43 | `articles/43-jane-addams.md` | jane-addams | figure | pd |
| 44 | `articles/44-dorothy-stock-whitaker.md` | dorothy-stock-whitaker | figure | none |

## QA script

`check_pack.py` (this folder) — counts files, required YAML, disclaimer, banned phrases, minimum word counts.
