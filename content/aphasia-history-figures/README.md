# SLPWOW — Aphasia History & Major Figures (staged)

Magazine series for a later import to **SLPWOW.com**. This folder is the pack. It is not a live-site edit, not COSMOS core, and not a merge with the general speech-pathology history pack.

**Start here:** [`INDEX.md`](INDEX.md) (calendar + roster). Voice: [`STYLE_GUIDE.md`](STYLE_GUIDE.md). Claims: [`CLAIMS_GUARDRAILS.md`](CLAIMS_GUARDRAILS.md). Portraits: [`PORTRAIT_SOURCES.md`](PORTRAIT_SOURCES.md). WordPress: [`WP_IMPORT.md`](WP_IMPORT.md).

Forty-five Markdown drafts live in `articles/` (16 era essays, 29 profiles). Cleared lead portraits live under `assets/portraits/` with a sibling `*.RIGHTS.md` per plate.

## Layout

| Path | Purpose |
|------|---------|
| `articles/` | 16 era essays + 29 profiles |
| `assets/portraits/` | Cleared portrait rasters + `*.RIGHTS.md` |
| `embeds/portrait-figure-block.md` | HTML `<figure>` template for SEO captions |
| `INDEX.md` | Editorial calendar and figure roster |
| `STYLE_GUIDE.md` | Voice, length, front matter |
| `PORTRAIT_SOURCES.md` | Public-domain hunt log and clearance ledger |
| `verify_portraits.py` | RIGHTS + ledger QA |
| `PHOTO_NOTES.md` | Art direction for a later graphics pass |
| `BIBLIOGRAPHY.md` | Sources used |
| `WP_IMPORT.md` | Draft → WordPress map |
| `check_pack.py` | Structural QA |

## Portrait policy

Never generate or embed synthetic historical faces. Use files in `assets/portraits/` only when listed as cleared in `PORTRAIT_SOURCES.md`. Each raster carries `assets/portraits/<id>.RIGHTS.md`. Until cleared, profiles use the placeholder block in `STYLE_GUIDE.md`.

## Sibling pack

A separate staged series, `content/slpwow-speech-pathology-history/`, covers the profession (ASHA, Iowa, Wisconsin, stuttering textbooks). This pack is the **aphasia** deep series: lesions, wards, tests, and the people who sat with the living. Do not merge the two trees. Cross-link after both are imported.
