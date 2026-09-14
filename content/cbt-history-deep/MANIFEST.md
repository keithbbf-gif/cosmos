# Manifest — `content/cbt-history-deep/`

Publishable pack for **staging** review. Count target: **≥40**. This pack: **44**.

Do not write to live wowtherapies.com from this folder.

Deepens `content/wowtherapies-therapy-history/` (cognitive turn, third wave, Beck, Ellis). Does not replace it.

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
| `RIGHTS.md` | Rights manifest for rasters and CC0 editorial SVG |
| `GRAPHICS_INDEX.md` | Lead graphics register |
| `embeds/` | HTML `<figure>` templates for SEO |
| `WP_IMPORT.md` | Staging import only |

## Required YAML on each draft

`title`, `slug`, `meta_description`, `tags`, `type` (`era`|`figure`), `order`, `portrait` (`pd`|`cc`|`confirm`|`none`), `citations`, `status`, `voice_check`, `last_verified`

Required body: educational note (not a diagnosis, not a treatment plan, not a substitute for a licensed clinician).

## Drafts (44)

| # | Path | Slug | type | portrait |
| --- | --- | --- | --- | --- |
| 01 | `drafts/01-stoic-sentences-before-the-clinic.md` | stoic-sentences-before-the-clinic | era | none |
| 02 | `drafts/02-adler-cognitive-timber.md` | adler-cognitive-timber | era | none |
| 03 | `drafts/03-kelly-personal-constructs-1955.md` | kelly-personal-constructs-1955 | era | none |
| 04 | `drafts/04-eysenck-1952-gauntlet.md` | eysenck-1952-gauntlet | era | none |
| 05 | `drafts/05-first-wave-behavior-clinic.md` | first-wave-behavior-clinic | era | none |
| 06 | `drafts/06-ellis-names-rebt-1955.md` | ellis-names-rebt-1955 | era | none |
| 07 | `drafts/07-beck-leaves-the-couch.md` | beck-leaves-the-couch | era | none |
| 08 | `drafts/08-depression-book-1967.md` | depression-book-1967 | era | none |
| 09 | `drafts/09-depression-manual-1979.md` | depression-manual-1979 | era | none |
| 10 | `drafts/10-dsm-iii-countable-object.md` | dsm-iii-countable-object | era | none |
| 11 | `drafts/11-nimh-tdcrp-graph.md` | nimh-tdcrp-graph | era | none |
| 12 | `drafts/12-chambless-est-lists.md` | chambless-est-lists | era | none |
| 13 | `drafts/13-managed-care-six-sessions.md` | managed-care-six-sessions | era | none |
| 14 | `drafts/14-third-wave-nickname-2004.md` | third-wave-nickname-2004 | era | none |
| 15 | `drafts/15-behavioral-activation-return.md` | behavioral-activation-return | era | none |
| 16 | `drafts/16-iapt-political-object.md` | iapt-political-object | era | none |
| 17 | `drafts/17-computerized-cbt-and-apps.md` | computerized-cbt-and-apps | era | none |
| 18 | `drafts/18-critiques-worksheet-could-not-hear.md` | critiques-worksheet-could-not-hear | era | none |
| 19 | `drafts/19-process-based-cbt-family-fight.md` | process-based-cbt-family-fight | era | none |
| 20 | `drafts/20-after-beck-2021.md` | after-beck-2021 | era | none |
| 21 | `drafts/21-aaron-temkin-beck.md` | aaron-temkin-beck | figure | none |
| 22 | `drafts/22-albert-ellis-east-65th.md` | albert-ellis-east-65th | figure | none |
| 23 | `drafts/23-judith-s-beck.md` | judith-s-beck | figure | none |
| 24 | `drafts/24-george-a-kelly.md` | george-a-kelly | figure | none |
| 25 | `drafts/25-joseph-wolpe.md` | joseph-wolpe | figure | none |
| 26 | `drafts/26-donald-meichenbaum.md` | donald-meichenbaum | figure | none |
| 27 | `drafts/27-arnold-a-lazarus.md` | arnold-a-lazarus | figure | none |
| 28 | `drafts/28-a-john-rush.md` | a-john-rush | figure | none |
| 29 | `drafts/29-david-m-clark.md` | david-m-clark | figure | none |
| 30 | `drafts/30-david-h-barlow.md` | david-h-barlow | figure | none |
| 31 | `drafts/31-marsha-linehan-cbt-dialectic.md` | marsha-linehan-cbt-dialectic | figure | none |
| 32 | `drafts/32-steven-c-hayes.md` | steven-c-hayes | figure | none |
| 33 | `drafts/33-zindel-segal-mbct.md` | zindel-segal-mbct | figure | none |
| 34 | `drafts/34-jon-kabat-zinn.md` | jon-kabat-zinn | figure | none |
| 35 | `drafts/35-jeffrey-e-young.md` | jeffrey-e-young | figure | none |
| 36 | `drafts/36-neil-s-jacobson.md` | neil-s-jacobson | figure | none |
| 37 | `drafts/37-christine-a-padesky.md` | christine-a-padesky | figure | none |
| 38 | `drafts/38-david-d-burns-feeling-good.md` | david-d-burns-feeling-good | figure | none |
| 39 | `drafts/39-dianne-l-chambless.md` | dianne-l-chambless | figure | none |
| 40 | `drafts/40-philip-c-kendall.md` | philip-c-kendall | figure | none |
| 41 | `drafts/41-edna-b-foa.md` | edna-b-foa | figure | none |
| 42 | `drafts/42-patricia-a-resick.md` | patricia-a-resick | figure | none |
| 43 | `drafts/43-stefan-g-hofmann.md` | stefan-g-hofmann | figure | none |
| 44 | `drafts/44-adrian-wells.md` | adrian-wells | figure | none |

## QA script

`check_pack.py` (this folder) — counts files, required YAML, disclaimer, banned phrases, DIY leaks, minimum word counts.
