# WordPress import — History of the Fig

Staged Markdown → WP. **Do not publish to figroots.com from this pack.** This file is the handoff for a later human import.

## Folder contract

```
content/fig-history-ancient-to-today/
  ARTICLE_INDEX.md      ← canon slug list
  INDEX.md              ← reading order + mix codes
  WRITER_STYLE_GUIDE.md
  STYLE_GUIDE.md        ← visual system
  BIBLIOGRAPHY.md
  IMAGE_SOURCES.md
  PHOTO_NOTES.md
  WP_IMPORT.md          ← this file
  GRAPHICS_*.md
  articles/_staging/<slug>/index.md
  assets/shared/svg/
  assets/images/<slug>/
```

## Front matter (required)

```yaml
---
title: "Pliny’s Twenty-Nine Names"
slug: pliny-and-the-roman-fig-catalog
series: History of the Fig
series_no: 11
dek: "One chapter of the Natural History is a customs ledger of Italian appetite."
mix: A
mix_secondary: B
region: Italy
era: 1st century CE
status: staging
voice_check: human
author: FigRoots Editorial
canonical_site: figroots.com
wp_type: post
wp_status: draft
figures:
  - shared.timeline-master
  - shared.chart-variety-regions
categories:
  - History of the Fig
tags:
  - Rome
  - Pliny
  - varieties
sources_key:
  - Pliny NH 15.19
  - Condit 1955
---
```

| Field | Rule |
| --- | --- |
| `slug` | Matches folder name under `articles/_staging/` |
| `series_no` | Integer, unique, matches `INDEX.md` |
| `mix` | `A` regional · `B` botanical/cultural · `C` trade/era · `D` modern commercial/garden |
| `status` | `staging` until a human marks `ready` |
| `voice_check` | Must be `human`. Importer should reject the post if missing. |
| `wp_status` | Always `draft` in this pack |
| `figures` | IDs that exist in `GRAPHICS_INDEX.md` |

## Markdown → blocks

- H1 in file **is** the post title; WP title field should copy `title:` and the H1 can be stripped on import to avoid doubling.
- `dek` → excerpt / subtitle.
- Figure blocks keep the HTML `figure-id` comment for pack validation. On import, convert the `![alt](path)` + italic caption into a WP figure + figcaption. Rewrite `../../../assets/…` to media-library URLs after one upload of `assets/`.
- Prefer download + local media so the live site does not depend on Wikimedia.
- `orchard_slot:` HTML comments: skip until the photo exists.
- “Sources for this piece” → a WP block titled **Sources**.

## Suggested WP taxonomy

**Parent category:** History of the Fig

**Child categories (map from `mix`):**

- Civilizations & Regions (`A`)
- Tree & Culture (`B`)
- Trade & Work (`C`)
- Modern Orchard & Market (`D`)

**Series plugin / tag:** `series:history-of-the-fig` + `series_no` as menu order.

## Import order

1. Create the four child categories and the parent.
2. Upload `assets/` (keep directory names).
3. Import posts in `series_no` order.
4. Leave all posts **Draft**.
5. Human pass: voice, image licenses, dek length, internal links.
6. Only then schedule. This pack does not contain a schedule.

## Internal links

Articles may point to other slugs as `[text](/fig-history/SLUG/)`. That path is a **proposal**. Change the prefix to whatever the live IA uses. Do not point at `figroots.com` URLs that do not exist yet.

## What not to import

- Index and guide Markdown as posts.
- This file.
- Any live-tree note. This directory is the entire payload.

## Quality gate before a post leaves `staging`

- [ ] `voice_check: human` and a human actually read it
- [ ] Every named ancient text exists in `BIBLIOGRAPHY.md`
- [ ] Every external raster is in `IMAGE_SOURCES.md`
- [ ] Figure mix passes the balance test in `PHOTO_NOTES.md`
- [ ] `python3 tools/fig_graphics_validate.py content/fig-history-ancient-to-today` exits 0
- [ ] No medical claims beyond the cited author
- [ ] No “first in the world” sentence that Kislev’s critics would laugh at
