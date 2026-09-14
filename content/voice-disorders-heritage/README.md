# SLPWOW — Voice Disorders: Clinical Heritage (staged)

Magazine series for a later import to **SLPWOW.com**. This folder is the pack. It is not a live-site edit, not COSMOS core, and not a merge into the sibling speech-pathology history pack.

**Start here:** [`INDEX.md`](INDEX.md) (calendar + roster). Voice: [`STYLE_GUIDE.md`](STYLE_GUIDE.md). Claims: [`CLAIMS_GUARDRAILS.md`](CLAIMS_GUARDRAILS.md). Portraits: [`PORTRAIT_SOURCES.md`](PORTRAIT_SOURCES.md). WordPress: [`WP_IMPORT.md`](WP_IMPORT.md).

Forty-four Markdown articles live in `articles/`. Portrait plates live under `assets/portraits/` only when `PORTRAIT_SOURCES.md` lists them as cleared.

This series is the **voice-disorders** lane of SLPWOW heritage copy: laryngoscopy, phoniatrics, the singing-teacher border, the American voice clinic, stroboscopy, the voice laboratory, professional-voice medicine, and the people who still sit on clinic shelves. The general history of speech-language pathology (Hotel McAlpin, Iowa, ASHA’s name changes) lives next door in `content/slpwow-speech-pathology-history/` (writer PR #254). Gutzmann, Fröschels, and Margaret Greene appear in both packs on purpose — here from the larynx side.

## Layout

| Path | Purpose |
|------|---------|
| `articles/` | 44 era essays and profiles |
| `assets/portraits/` | Licensed portrait files + `*.RIGHTS.md` per plate |
| `embeds/portrait-figure-block.md` | HTML `<figure>` template for SEO captions |
| `verify_portraits.py` | RIGHTS + ledger QA |
| `INDEX.md` | Calendar, roster, publish waves |
| `STYLE_GUIDE.md` | Human voice, bans, structure |
| `CLAIMS_GUARDRAILS.md` | Educational, not a protocol |
| `BIBLIOGRAPHY.md` | Sources used |
| `PHOTO_NOTES.md` | Art direction |
| `PORTRAIT_SOURCES.md` | License ledger and hunt log |
| `WP_IMPORT.md` | Draft-only WordPress map |
| `check_pack.py` | Structural QA |

## Portrait policy

Never generate or embed synthetic historical faces. Use files in `assets/portraits/` only when listed as cleared in `PORTRAIT_SOURCES.md`. Each raster carries a sibling `*.RIGHTS.md`. Until cleared, use the labeled placeholder block in the article.

## What this pack will not do

- No live writes to slpwow.com or the WOW Therapies CMS.
- No home voice-exercise programs, stimulation hierarchies as homework, or “try this if your hoarseness…”.
- No merge into furniture, figroots, COSMOS modules, or the psychotherapy (WOWTherapies) pack.
