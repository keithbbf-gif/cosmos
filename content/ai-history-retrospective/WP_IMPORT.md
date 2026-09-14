# WordPress import notes

Staged Markdown in this folder is the source. WordPress is a projection.

## Suggested content types

| Folder / file | WP type | Notes |
| --- | --- | --- |
| `essays/*.md` | Post, category `AI History — Eras` | Series order from `INDEX.md` |
| `profiles/*.md` | Post, category `AI History — Figures` | One post per slug |
| `INDEX.md` | Page | Manual HTML or a table block; do not auto-import the whole index as a post |
| `STYLE_GUIDE.md`, `BIBLIOGRAPHY.md`, `PORTRAIT_SOURCES.md`, `PHOTO_NOTES.md`, `NOVELTY_GUARDRAILS.md` | Pages, parent `AI History — Colophon` | Keep out of the public magazine RSS if the site is consumer-facing |

## Front matter → WordPress

| YAML | WP |
| --- | --- |
| `title` | Post title |
| `slug` | Post slug (do not prefix with dates) |
| `tags` | Post tags |
| `kind` | Custom field `kind` (`essay` / `profile`) |
| `era` | Custom field `era` |
| `voice_check` | Custom field; discard from rendered HTML |
| `portrait` | Featured image attachment, path relative to this folder |
| `portrait_status` | Custom field; if `placeholder`, do not set a “photograph” schema type |

Convert the Markdown body with a CommonMark parser. Keep image URLs rooted at `/wp-content/uploads/ai-history-retrospective/` after media import, or leave them as repo-relative and fix with a search-replace.

## Media import

1. Upload everything under `assets/portraits/` except `*.placeholder.svg` as Media Library items **only if** the license row in `PORTRAIT_SOURCES.md` allows redistribution.
2. Paste the credit line from `PORTRAIT_SOURCES.md` into the attachment’s caption and into the `copyright` / `credit` field your theme uses.
3. For CC BY-SA files, the share-alike obligation follows derivative crops and theme filters. Do not run a “style transfer” or face-restore filter.
4. Upload placeholders as ordinary media with alt text: “Labeled placeholder, not a photograph of [Name].”
5. Do not set Open Graph images to placeholders; omit the OG image rather than imply a likeness.

## Block structure

A typical post:

1. Optional kicker: `History of AI — Retrospective`
2. Title from front matter
3. First paragraph (lede) — no featured-image duplicate if the first body figure is the portrait
4. Portrait figure + italic credit
5. Remaining Markdown as heading / paragraph / list blocks
6. Footer: “Further reading” pulled from the article’s last section, plus a link to `BIBLIOGRAPHY.md`

## Internal links

Repo links use relative paths (`../profiles/alan-turing.md`). On import, map `slug` to permalink `/ai-history/<slug>/`.

## What not to import

- This file’s operational checklists, if the public site should stay magazine-clean
- `NOVELTY_GUARDRAILS.md` may stay internal
- Any path outside `content/ai-history-retrospective/`

## Legal footer (suggested)

> Portraits are credited individually. Public-domain and Creative Commons files are used under the terms on their Wikimedia Commons file pages as of staging. Placeholders are not likenesses.

## Staging status

This tree is a **draft**. Do not schedule a production import until a human editor has walked `NOVELTY_GUARDRAILS.md` and spot-checked quotations against the bibliography.
