# WordPress Import — SLPWOW Voice Disorders Heritage

Staged pack only. Do **not** push these files to live slpwow.com or the WOW Therapies host from this repository. A human editor imports when the brand is ready.

## Pack layout

```
content/voice-disorders-heritage/
  INDEX.md                 editorial calendar + roster
  STYLE_GUIDE.md
  CLAIMS_GUARDRAILS.md
  BIBLIOGRAPHY.md
  PHOTO_NOTES.md
  PORTRAIT_SOURCES.md
  WP_IMPORT.md             this file
  check_pack.py
  assets/portraits/
  articles/01-…44-….md
```

## Recommended WP information architecture

Create two parent pages or two category archives under the History section, beside the speech-pathology history series:

- **Voice — Ages** — `type: era` (articles 01–16)
- **Voice — People** — `type: profile` (articles 17–44)

Slug prefix suggestion (avoids colliding with clinic service pages and with the sibling history pack):

`/history/voice/<slug>/`

Examples:

- `/history/voice/a-dental-mirror-in-paris/`
- `/history/voice/minoru-hirano/`

Do not hang these under `/services/` or `/voice-therapy/exercises/`.

## Front-matter → WordPress map

| YAML | WordPress |
|------|-----------|
| `title` | Post title |
| `slug` | Post slug (do not auto-decorate) |
| `type: era` | Category: History — Voice Ages |
| `type: profile` | Category: History — Voice People |
| `tags` | Post tags |
| `portrait` | Featured image if path is not `null` |
| `portrait_status: placeholder` | No featured image; keep the placeholder block in the body |
| `figure_dates` | Optional subtitle or a custom field `figure_dates` |
| `voice_check` | Custom field; hide from public |
| `series` | Custom field `series = slpwow-voice-disorders-heritage` |
| `stage: draft` | WP status **Draft** on first import |
| `audience: slpwow` | unused publicly |

Strip the YAML before the post body. Do not print `voice_check` (or other editorial flags) on the site.

Keep the italic educational line under the title. It is not optional.

## Markdown → blocks

- ATX `##` / `###` → heading blocks.
- Images:

```markdown
![alt](../assets/portraits/name.jpg)

*Caption. Credit line.*
```

On import, rewrite the relative path to the Media Library URL. Keep caption + credit as a caption block, not in the alt text.

- Blockquotes that start with `**Portrait placeholder.**` → a muted “callout” or “notice” block. Do not style them as testimonials.
- Italic book titles stay italic.
- Do not auto-link every proper name to Wikipedia.

## Featured images

Upload only files listed as **cleared** in `PORTRAIT_SOURCES.md`.

Media Library title = person’s name. Alt text = name + role + date (see `PHOTO_NOTES.md`). Caption = recommended credit line from `PORTRAIT_SOURCES.md`.

Do **not** upload generated likenesses, ASHA omeka scrapes, or university-page snapshots without a redistribution grant.

## SEO / social (keep dull on purpose)

Title examples that match the pack voice:

- “Manuel García and the Afternoon He Saw His Own Glottis”
- “Cover and Body: A Five-Page Paper from Kurume”

Avoid:

- “The Amazing Singing Teacher Who Invented Voice Therapy!”
- “10 Voice Doctors Who Changed the World”

Excerpt: first 1–2 concrete sentences of the article, not a keyword list.

No medical schema (`MedicalWebPage`, `howTo`) on these posts. They are historical essays. A how-to schema on the chewing-method essay would be a clinical incident.

## Medical-legal

Add a sitewide footer on the History section, once (same sentence as the sibling pack):

> These essays are historical and educational. They are not treatment advice and they are not a substitute for evaluation by a licensed clinician.

Do not append a clinic booking widget to the Frederick III essay or the spasmodic-dysphonia toxin essay.

## Import tools

Reasonable paths:

1. Manual: copy body into Gutenberg, set categories, upload one image. Forty-four drafts is a long weekend.
2. WP All Import / CSV: one row per article — `title, slug, content_html, category, tags, featured_image, custom_figure_dates`.
3. Static Markdown plugins exist; they fight with this theme later. Prefer HTML in WP.

If converting with Pandoc:

```bash
pandoc articles/19-manuel-garcia-jr.md -f markdown -t html -o /tmp/19.html
```

Then paste. Strip the YAML first.

## Publish waves

See `INDEX.md` (“Suggested publish waves”). Wave A is safe to put live first: the mirror, no open ethics crisis in the lead slot. Essay 12 (toxin) and essay 14 (Parkinson intensity) should not be the first public posts — they are the ones readers will try to treat as manuals.

## What not to merge

- Not into COSMOS docs, KDash, or `live/`.
- Not into figroots or furniture content packs.
- Not into the WOWTherapies psychotherapy pack.
- Not into the clinic’s service-page templates.

## After import (editor checklist)

- [ ] All 44 posts exist as **Draft**
- [ ] Featured images only where `portrait_status: downloaded`
- [ ] Placeholder block still visible on hunt profiles
- [ ] Internal links among the 44 rewritten from `.md` filenames to permalinks
- [ ] Cross-links to the sibling speech-pathology history series rewritten to those permalinks once that pack is imported
- [ ] Bibliography page is a draft, not a public dump of URLs, unless the editor wants a “Further reading” page
- [ ] Live slpwow.com still untouched until a human hits Publish
