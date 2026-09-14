# WordPress import — Wilmar and the Saline River

Staged Markdown → WP. **Do not publish to bbfur or any live site from this pack.** This file is the handoff for a later human import.

## Folder contract

```
content/wilmar-saline-river-local-history/
  INDEX.md
  STYLE_GUIDE.md
  BIBLIOGRAPHY.md
  IMAGE_SOURCES.md
  PHOTO_NOTES.md
  WP_IMPORT.md          ← this file
  articles/NN-slug.md
  assets/               ← maps, diagrams, notes
```

## Front matter (required)

```yaml
---
title: "A Dollar an Acre"
slug: a-dollar-an-acre
series: Wilmar and the Saline River
series_no: 1
dek: "In 1859 a man paid one dollar an acre for seven hundred acres. The town came later, and took a daughter’s name."
mix: A
mix_secondary: D
region: Wilmar, Drew County
era: 1859–1869
status: staged
voice_check: human
author: BBF Editorial
canonical_site: bbfur
wp_type: post
wp_status: draft
categories:
  - Wilmar and the Saline River
tags:
  - Wilmar
  - Anderson
  - Drew County
featured_image: ../assets/maps/drew-saline-ridge.svg
sources_key:
  - Teske Wilmar EOA
  - DeArmond 1980
---
```

| Field | Rule |
| --- | --- |
| `slug` | Matches filename after the number: `01-a-dollar-an-acre.md` → `a-dollar-an-acre` |
| `series_no` | Integer, unique, matches `INDEX.md` |
| `mix` | `A` town/civic · `B` river/landscape · `C` mills/rail · `D` farm/food/after |
| `status` | `staged` until a human marks `ready` |
| `voice_check` | Must be `human`. Importer should reject the post if missing. |
| `wp_status` | Always `draft` in this pack |
| `canonical_site` | `bbfur` (future furniture/heritage door). Not a live URL. Soft-link only. |

## Markdown → blocks

- H1 in file **is** the post title; WP title field should copy `title:` and the H1 can be stripped on import to avoid doubling.
- `dek` → excerpt / subtitle.
- `##` / `###` → WP headings.
- Figures:

```markdown
<figure>
<img src="…" alt="…">
<figcaption>Caption. Credit: … License: …</figcaption>
</figure>
```

- Pack-relative paths stay as written. On import, upload `assets/` once.
- `photo_slot:` lines are HTML comments. Skip on import until the photo exists.
- “Sources for this piece” → a WP block titled **Sources**.

## Suggested WP taxonomy

**Parent category:** Wilmar and the Saline River

**Tags:** prefer place and institution names (Wilmar, Saline River, Gates, Beauvoir, June Dinner) over mood words.

## Do not

- Auto-publish. Every post stays `draft`.
- Attach a product block, a shop CTA, or an Etsy card.
- Import the lynching or Klan essays without a human editor on the page.
