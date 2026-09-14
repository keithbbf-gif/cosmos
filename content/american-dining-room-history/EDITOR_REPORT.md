# Editor report — American dining room history pack

**Role:** EDITOR (object-first magazine pass)  
**Writer branch:** `cursor/american-dining-room-history-527a` (PR #324)  
**Editor branch:** `cursor/american-dining-room-editor-8415`  
**Scope:** `content/american-dining-room-history/` — 44 drafts + pack QA  
**Staging only:** no live publish  
**Date:** 2026-09-14  

## Stamp

- All **44** articles: `voice_check: edited` (read-aloud pass; grammar; object-first ledes where the writer draft opened on era or process; no sell copy).
- Pack meta (`INDEX.md`, `MANIFEST.md`, `STYLE_GUIDE.md`, `BIBLIOGRAPHY.md`, `PHOTO_CAPTIONS.md`): `voice_check: edited`.
- Full-series scan for STYLE_GUIDE hard bans in body copy: **no violations** (landscape in Baltimore = painted tablet scenery, not metaphorical filler).

## What the editor did

### Voice and sell copy

- Removed **process / pillar** lines (“furniture-history pillar asked…”) from body copy.
- Trimmed **Bradley Brand / BBF** mentions outside the allowed woods slug per `STYLE_GUIDE.md` (one shop sentence remains on `arkansas-southern-hardwood-dining` only).
- Replaced **shopping literacy** and meta **“shop that still cuts”** with teaching language (grain/species reading; vernacular servers → factory pecan and studio slabs).
- Kept deliberate anti-catalog lines (reading-a-table, studio vs epoxy, hunt-board name as dealer romance).

### Object-first ledes (selected)

| Slug | Editor action |
| --- | --- |
| `arkansas-southern-hardwood-dining` | Open on quartersawn white-oak ray fleck; moved brand to closing sentence only |
| `depression-dinette` | Open on enamel top + chromium legs + catalog type |
| `dining-chairs-splat-to-ladder` | Open on pierced Chippendale splat (type), not definition-first |
| `country-early-american-revival` | Open on maple hutch + harvest-gold wall (1974 showroom object) |
| `the-room-is-invented` | “Transformer” → **convertible** gateleg (less pop-culture) |

### Brand scope cleanup

| Slug | Editor action |
| --- | --- |
| `hunt-board-southern-vernacular` | Dropped BBF pillar + shop-knows-drawing lines |
| `butler-pantry-breakfast-room` | Dropped BBF lead; kept MESDA 3163 / island slab close |
| `grand-rapids-factory-dining` | Generic one-off studio contrast; dropped BBF + pillar map |
| `charleston-southern-colonial-dining` | Southern hardwood table without brand name |
| `colonial-revival-dining` | Piedmont server vs Nutting without BBF |
| `shaker-trestle-dining` | Generic square trestle without brand name |

### Structure and repetition

- Intra-article paragraph similarity scan (>0.72): **no duplicate blocks** flagged across the 44 drafts.
- Recap / “key takeaways” closings: **none added**; series cross-links unchanged.

### Copy-editing

- Light grammar and cohesion on merged ledes only.
- `[CITE NEEDED]` pins and museum accession numbers **unchanged** (no invented accessions).

## QA notes (unchanged from writer manifest)

- Accession pins as staged: Brooklyn 1997.150.15a–c; Met 31.44.15, 22.98, 1971.160, 22.28.1; MESDA 3163.
- Hunt board named as twentieth-century dealer term.
- All `primary_keyword` values unique; all slugs unique.
- `status: draft` only; no WordPress publish dates.

## Image + SEO pass (2026-09-14)

- **44/44** drafts: lead `<figure class="adrh-figure">` with museum/Commons hot links, lazy load, `Fig. 1` caption, and `<em>Rights:</em>` line.
- Registry: `assets/figures/REGISTRY.toml` (**28** plates). Assignments: `_editorial/figure_assignments.toml`.
- `RIGHTS.md`, `GRAPHICS_INDEX.md`. Checker: `_editorial/check_figures.py` (44/44, URL spot-check).
- Frontmatter: `figure_id`, `image_rights: documented`, `image_pass: 2026-09-14`. `voice_check: edited` unchanged.
- **Not executed:** BBF shop stills, Brooklyn/MESDA hero replacements listed in `PHOTO_CAPTIONS.md`.

## Handoff

Stack for review: editor **`cursor/american-dining-room-editor-8415`** + graphics **`cursor/american-dining-room-images-seo-f03c`** onto writer branch **PR #324** (`cursor/american-dining-room-history-527a`). Import per staging README when Keith approves. **Do not merge to main without review.**
