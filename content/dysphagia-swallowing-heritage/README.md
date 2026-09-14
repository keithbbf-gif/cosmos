# SLPWOW — Dysphagia & Swallowing: Clinical Heritage (staged)

Magazine series for a later import to **SLPWOW.com**. This folder is the pack. It is not a live-site edit, not COSMOS core, and not a merge into the sibling speech-pathology history pack or the voice-disorders heritage pack.

**Start here:** [`INDEX.md`](INDEX.md) (calendar + roster). Voice: [`STYLE_GUIDE.md`](STYLE_GUIDE.md). Claims: [`CLAIMS_GUARDRAILS.md`](CLAIMS_GUARDRAILS.md). Portraits: [`PORTRAIT_SOURCES.md`](PORTRAIT_SOURCES.md) (notes only). WordPress: [`WP_IMPORT.md`](WP_IMPORT.md).

Forty-four Markdown drafts live in `articles/` (16 era essays, 28 profiles). Cleared **PD/CC portraits** live under `assets/portraits/` with per-file `*.RIGHTS.md` sidecars and pack ledger [`RIGHTS.md`](RIGHTS.md). Lead `<figure class="slpwow-figure">` blocks carry SEO captions; living figures stay placeholder — never AI faces.

This series is the **swallowing / dysphagia** lane of SLPWOW heritage copy: the word before the clinic, experimental physiology, bismuth and barium, the rigid esophagoscope, infant cine at Bethesda, the Hopkins swallowing center, the 1980s SLP turn, FEES, silent aspiration as an argument, texture modification as a century-long habit, and the people whose books and films still sit on clinic shelves. The general history of the profession (Hotel McAlpin, Iowa, ASHA’s name changes) lives next door in `content/slpwow-speech-pathology-history/`. Voice and larynx live in `content/voice-disorders-heritage/`. Chevalier Jackson appears in the voice pack from the knife side; here he is the foreign-body and esophagus man.

## Layout

| Path | Purpose |
|------|---------|
| `articles/` | 16 era essays + 28 profiles |
| `INDEX.md` | Calendar, roster, publish waves |
| `MANIFEST.md` | Pack identity |
| `STYLE_GUIDE.md` | Human voice, bans, structure |
| `CLAIMS_GUARDRAILS.md` | Educational, not a protocol |
| `BIBLIOGRAPHY.md` | Sources used |
| `PHOTO_NOTES.md` | Art direction for figures and captions |
| `PORTRAIT_SOURCES.md` | License ledger and hunt log |
| `RIGHTS.md` | Cleared portrait registry + placeholder policy |
| `assets/portraits/` | Ingested PD/CC JPEGs + `*.RIGHTS.md` |
| `_tools/` | Commons ingest + figure patch helpers |
| `WP_IMPORT.md` | Draft-only WordPress map |
| `check_pack.py` | Structural QA |

## Portrait policy

Never generate or embed synthetic historical faces. Ingest only **public domain, CC, museum open access, or Wikimedia Commons** files with a verified file-page license. Record every binary in `RIGHTS.md` and `assets/portraits/<id>.RIGHTS.md`. Profiles with `portrait_status: downloaded` must carry a lead `<figure class="slpwow-figure slpwow-figure--portrait">` block (`<!-- figure-id: <slug>.lead-portrait -->`). Living or uncleared figures stay `portrait_status: placeholder` with the verbatim placeholder block — no substitute likeness.

## What this pack will not do

- No live writes to slpwow.com or the WOW Therapies CMS.
- No home swallow programs, chin-tuck homework, thickener recipes, or “try this if your parent coughs…”.
- No merge into furniture, figroots, COSMOS modules, the psychotherapy (WOWTherapies) pack, or the voice-disorders tree.
