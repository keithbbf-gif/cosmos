# WordPress Import — SLPWOW Dysphagia & Swallowing Heritage

Staged pack only. Do **not** push these files to live slpwow.com or the WOW Therapies host from this repository. A human editor imports when the brand is ready.

## Pack layout

```
content/dysphagia-swallowing-heritage/
  INDEX.md                 editorial calendar + roster
  MANIFEST.md
  STYLE_GUIDE.md
  CLAIMS_GUARDRAILS.md
  BIBLIOGRAPHY.md
  PHOTO_NOTES.md
  PORTRAIT_SOURCES.md
  WP_IMPORT.md             this file
  check_pack.py
  articles/01-…44-….md
```

## Recommended WP information architecture

Create two parent pages or two category archives under the History section, beside the speech-pathology history series and the voice-disorders series:

- **Swallow — Ages** — `type: era` (articles 01–16)
- **Swallow — People** — `type: profile` (articles 17–44)

Slug prefix suggestion (avoids colliding with clinic service pages and with sibling history packs):

`/history/swallow/<slug>/`

Examples:

- `/history/swallow/cannons-bismuth/`
- `/history/swallow/jeri-a-logemann/`

Do not hang these under `/services/` or `/dysphagia/` or `/swallowing-therapy/exercises/`.

## Front-matter → WordPress map

| YAML | WordPress |
|------|-----------|
| `title` | Post title |
| `slug` | Post slug (do not auto-decorate) |
| `type: era` | Category: History — Swallow Ages |
| `type: profile` | Category: History — Swallow People |
| `tags` | Post tags |
| `portrait` | Featured image only if a later pass adds a cleared file; this pack ships `null` |
| `portrait_status: note` | No featured image; keep the placeholder block in the body |
| `figure_dates` | Optional subtitle or a custom field `figure_dates` |
| `voice_check` | Custom field; hide from public |
| `series` | Custom field `series = slpwow-dysphagia-swallowing-heritage` |
| `stage: draft` | WP status **Draft** on first import |
| `audience: slpwow` | unused publicly |
| `meta_description` | Excerpt |

Strip the YAML before the post body. Do not print `voice_check` (writer `human` or editor `edited`) on the site.

Keep the italic educational line under the title. It is not optional.

## Markdown → blocks

- ATX `##` / `###` → heading blocks.
- Blockquotes that start with `**Portrait placeholder.**` → a muted “callout” or “notice” block. Do not style them as testimonials.
- Italic book titles stay italic.
- Do not auto-link every proper name to Wikipedia.

## Featured images

This pack ships **no** image binaries. Upload later only files listed as **cleared** in `PORTRAIT_SOURCES.md`.

Do **not** upload generated likenesses, ASHA omeka scrapes, or university-page snapshots without a redistribution grant. Do **not** upload a frame from a clinical swallow study.

## SEO / social (keep dull on purpose)

Title examples that match the pack voice:

- “Cannon’s Bismuth: The Afternoon a Swallow Became a Picture”
- “The 1983 Book That Put Swallowing on an SLP Shelf”

Avoid:

- “The Amazing Doctor Who Invented Swallow Therapy!”
- “10 Swallowing Tests That Could Save Your Life”

Excerpt: first 1–2 concrete sentences of the article, not a keyword list.

No medical schema (`MedicalWebPage`, `howTo`) on these posts. They are historical essays. A how-to schema on the IDDSI essay or the silent-aspiration essay would be a clinical incident.

## Medical-legal

Add a sitewide footer on the History section, once (same sentence as the sibling packs):

> These essays are historical and educational. They are not treatment advice and they are not a substitute for evaluation by a licensed clinician.

Do not append a clinic booking widget to the nursing-home essay or the infant-feeding essay.

## Import tools

Reasonable paths:

1. Manual: copy body into Gutenberg, set categories. Forty-four drafts is a long weekend.
2. WP All Import / CSV: one row per article — `title, slug, content_html, category, tags, custom_figure_dates`.
3. Static Markdown plugins exist; they fight with this theme later. Prefer HTML in WP.

If converting with Pandoc:

```bash
pandoc articles/27-jeri-a-logemann.md -f markdown -t html -o /tmp/27.html
```

Then paste. Strip the YAML first.

## Publish waves

See `INDEX.md` (“Suggested publish waves”). Wave A is safe to put live first: the word, Magendie, Cannon — no open protocol in the lead slot. Essays 11 (silent aspiration), 12 (texture), and 15 (nursing home) should not be the first public posts — they are the ones readers will try to treat as manuals.

## What not to merge

- Not into COSMOS docs, KDash, or `live/`.
- Not into figroots or furniture content packs.
- Not into the WOWTherapies psychotherapy pack.
- Not into the voice-disorders heritage tree (cross-link after both are imported).
- Not into the clinic’s service-page templates.

## After import (editor checklist)

- [ ] All 44 posts exist as **Draft**
- [ ] No featured images until a cleared file exists
- [ ] Placeholder block still visible on hunt profiles
- [ ] Internal links among the 44 rewritten from `.md` filenames to permalinks
- [ ] Cross-links to sibling history series rewritten to those permalinks once those packs are imported
- [ ] Bibliography page is a draft, not a public dump of URLs, unless the editor wants a “Further reading” page
- [ ] Live slpwow.com still untouched until a human hits Publish
