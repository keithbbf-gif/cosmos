# WordPress import — History of the Fig

Staged Markdown → WP. **Do not publish to figroots.com from this pack.** This file is the handoff for a later human import.

## Folder contract

```
content/fig-history-ancient-to-today/
  INDEX.md
  STYLE_GUIDE.md
  BIBLIOGRAPHY.md
  IMAGE_SOURCES.md
  PHOTO_NOTES.md
  WP_IMPORT.md          ← this file
  articles/NN-slug.md
  assets/               ← maps, diagrams, timelines, plate notes
```

## Front matter (required)

```yaml
---
title: "Pliny’s Twenty-Nine Names"
slug: pliny-twenty-nine-names
series: History of the Fig
series_no: 10
dek: "One chapter of the Natural History is a customs ledger of Italian appetite."
mix: A
mix_secondary: B
region: Italy
era: 1st century CE
status: staged
voice_check: human
author: FigRoots Editorial
canonical_site: figroots.com   # future; not live
wp_type: post
wp_status: draft
categories:
  - History of the Fig
tags:
  - Rome
  - Pliny
  - varieties
featured_image: assets/maps/mediterranean-fig-belt.svg
sources_key:
  - Pliny NH 15.19
  - Condit 1955
---
```

| Field | Rule |
| --- | --- |
| `slug` | Matches filename after the number: `10-pliny-twenty-nine-names.md` → `pliny-twenty-nine-names` |
| `series_no` | Integer, unique, matches `INDEX.md` |
| `mix` | `A` regional · `B` botanical/cultural · `C` trade/era · `D` modern commercial/garden |
| `status` | `staged` until a human marks `ready` |
| `voice_check` | Must be `human`. Importer should reject the post if missing. |
| `wp_status` | Always `draft` in this pack |

## Markdown → blocks

- H1 in file **is** the post title; WP title field should copy `title:` and the H1 can be stripped on import to avoid doubling.
- `dek` → excerpt / subtitle. FigRoots theme: dek under the headline, not inside the first paragraph.
- `##` / `###` → WP headings.
- Figures:

```markdown
<figure>
<img src="…" alt="…">
<figcaption>Caption. Credit: … License: …</figcaption>
</figure>
```

- Pack-relative paths (`assets/…`, Wikimedia URLs) stay as written. On import, upload `assets/` to the media library **once**, then rewrite URLs. Do not re-upload Commons files if the license allows hotlink-or-download; prefer download + local media so the live site does not depend on Wikimedia.
- `orchard_slot:` lines are HTML comments in the article (`<!-- orchard_slot: ORCH-01 -->`). Skip on import until the photo exists.
- “Sources for this piece” → a WP block titled **Sources**, not a footnote plugin unless the site already has one.

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
3. Import posts in `series_no` order so “Next in the series” can be wired.
4. Leave all posts **Draft**.
5. Human pass: voice, image licenses, dek length, internal links.
6. Only then schedule. This pack does not contain a schedule.

## Internal links

Articles may point to other slugs as `[text](/fig-history/SLUG/)`. That path is a **proposal**. Change the prefix to whatever the live IA uses. Do not point at `figroots.com` URLs that do not exist yet.

## What not to import

- `INDEX.md`, the four guides, and `assets/*.svg` as posts.
- This file.
- Any COSMOS path, work order, or live-tree note. This directory is the entire payload.

## Quality gate before a post leaves `staged`

- [ ] `voice_check: human` and a human actually read it
- [ ] Every named ancient text exists in `BIBLIOGRAPHY.md`
- [ ] Every external image is in `IMAGE_SOURCES.md`
- [ ] Figure mix passes the balance test in `PHOTO_NOTES.md`
- [ ] No medical claims beyond the cited author
- [ ] No “first in the world” sentence that Kislev’s critics would laugh at
