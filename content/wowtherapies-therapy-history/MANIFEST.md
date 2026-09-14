# Manifest — `content/wowtherapies-therapy-history/`

Publishable pack for **staging** review. Count target: **≥30–40**. This pack: **42**.

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

## Required YAML on each article

`title`, `slug`, `meta_description`, `tags`, `type` (`era`|`figure`), `order`, `portrait` (`pd`|`cc`|`confirm`|`none`), `citations`, `status`, `voice_check`, `last_verified`

Required body: educational note (not a diagnosis, not a treatment plan, not a substitute for a licensed clinician).

## Articles (42)

| # | Path | Slug | type | portrait |
| --- | --- | --- | --- | --- |
| 01 | `articles/01-before-the-consulting-room.md` | before-the-consulting-room | era | none |
| 02 | `articles/02-asylum-and-moral-treatment.md` | asylums-moral-treatment | era | none |
| 03 | `articles/03-hypnosis-hysteria-talking-cure.md` | hypnosis-hysteria-talking-cure | era | none |
| 04 | `articles/04-psychoanalytic-century.md` | psychoanalytic-century | era | none |
| 05 | `articles/05-behaviorism-in-the-clinic.md` | behaviorism-in-the-clinic | era | none |
| 06 | `articles/06-humanistic-existential.md` | humanistic-existential-therapies | era | none |
| 07 | `articles/07-systems-and-families.md` | families-systems-therapy | era | none |
| 08 | `articles/08-cognitive-empirical-turn.md` | cognitive-therapy-empirical-turn | era | none |
| 09 | `articles/09-attachment-in-the-room.md` | attachment-therapy-hour | era | none |
| 10 | `articles/10-trauma-lineages.md` | trauma-lineages | era | none |
| 11 | `articles/11-feminist-relational.md` | feminist-relational-therapies | era | none |
| 12 | `articles/12-multicultural-liberation.md` | multicultural-liberation-psychology | era | none |
| 13 | `articles/13-third-wave.md` | third-wave-mindfulness-clinic | era | none |
| 14 | `articles/14-counseling-as-a-profession.md` | counseling-as-a-profession | era | none |
| 15 | `articles/15-philippe-pinel.md` | philippe-pinel | figure | pd |
| 16 | `articles/16-dorothea-dix.md` | dorothea-dix | figure | pd |
| 17 | `articles/17-clifford-beers.md` | clifford-beers | figure | none |
| 18 | `articles/18-sigmund-freud.md` | sigmund-freud | figure | pd |
| 19 | `articles/19-carl-jung.md` | carl-jung | figure | confirm |
| 20 | `articles/20-alfred-adler.md` | alfred-adler | figure | confirm |
| 21 | `articles/21-anna-freud.md` | anna-freud | figure | none |
| 22 | `articles/22-melanie-klein.md` | melanie-klein | figure | none |
| 23 | `articles/23-karen-horney.md` | karen-horney | figure | confirm |
| 24 | `articles/24-donald-winnicott.md` | donald-winnicott | figure | none |
| 25 | `articles/25-carl-rogers.md` | carl-rogers | figure | none |
| 26 | `articles/26-viktor-frankl.md` | viktor-frankl | figure | none |
| 27 | `articles/27-aaron-beck.md` | aaron-beck | figure | none |
| 28 | `articles/28-albert-ellis.md` | albert-ellis | figure | none |
| 29 | `articles/29-marsha-linehan.md` | marsha-linehan | figure | none |
| 30 | `articles/30-john-bowlby.md` | john-bowlby | figure | none |
| 31 | `articles/31-mary-ainsworth.md` | mary-ainsworth | figure | none |
| 32 | `articles/32-virginia-satir.md` | virginia-satir | figure | none |
| 33 | `articles/33-salvador-minuchin.md` | salvador-minuchin | figure | none |
| 34 | `articles/34-irvin-yalom.md` | irvin-yalom | figure | none |
| 35 | `articles/35-frantz-fanon.md` | frantz-fanon | figure | confirm |
| 36 | `articles/36-ignacio-martin-baro.md` | ignacio-martin-baro | figure | none |
| 37 | `articles/37-shoma-morita.md` | shoma-morita | figure | confirm |
| 38 | `articles/38-girindrasekhar-bose.md` | girindrasekhar-bose | figure | confirm |
| 39 | `articles/39-nise-da-silveira.md` | nise-da-silveira | figure | none |
| 40 | `articles/40-mamie-phipps-clark.md` | mamie-phipps-clark | figure | none |
| 41 | `articles/41-judith-herman.md` | judith-herman | figure | none |
| 42 | `articles/42-insoo-kim-berg.md` | insoo-kim-berg | figure | none |

## QA script

`check_pack.py` (this folder) — counts files, required YAML, disclaimer, banned phrases, minimum word counts.
