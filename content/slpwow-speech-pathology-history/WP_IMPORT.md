# WordPress Import — SLPWOW Speech Pathology History

Staged pack only. Do **not** push these files to live slpwow.com or the WOW Therapies host from this repository. A human editor imports when the brand is ready.

## Pack layout

```
content/slpwow-speech-pathology-history/
  INDEX.md                 editorial calendar + roster
  STYLE_GUIDE.md
  BIBLIOGRAPHY.md
  PHOTO_NOTES.md
  PORTRAIT_SOURCES.md
  WP_IMPORT.md             this file
  assets/
    visible-speech-english-chart.png
    portraits/*.jpg|png
  articles/01-…40-….md
```

## Recommended WP information architecture

Create two parent pages or two category archives:

- **Ages of the work** — `type: era` (articles 01–16)
- **People** — `type: profile` (articles 17–40)

Slug prefix suggestion (avoids colliding with clinic service pages):

`/history/speech-pathology/<slug>/`

Examples:

- `/history/speech-pathology/hotel-mcalpin-1925/`
- `/history/speech-pathology/sara-stinchfield-hawk/`

Do not hang these under `/services/` or `/blog/coupons/`.

## Front-matter → WordPress map

| YAML | WordPress |
|------|-----------|
| `title` | Post title |
| `slug` | Post slug (do not auto-decorate) |
| `type: era` | Category: History — Ages |
| `type: profile` | Category: History — People |
| `tags` | Post tags |
| `portrait` | Featured image if path is not `null` |
| `portrait_status: placeholder` | No featured image; keep the placeholder block in the body |
| `figure_dates` | Optional subtitle or a custom field `figure_dates` |
| `voice_check` | Custom field; hide from public |
| `series` | Custom field `series = slpwow-speech-pathology-history` |
| `stage: draft` | WP status **Draft** on first import |
| `audience: slpwow` | unused publicly |

Strip the YAML before the post body. Do not print `voice_check` or `voice_check_date` on the site.

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

Upload only files listed as **Downloaded** in `PORTRAIT_SOURCES.md`.

Media Library title = person’s name. Alt text = name + role + date (see `PHOTO_NOTES.md`). Caption = recommended credit line from `PORTRAIT_SOURCES.md`.

Do **not** upload:

- `johann-conrad-amman.jpg` as a featured image (too small).
- `samuel-heinicke.jpg` as a featured image (too small). Fine as an inline figure in essay 01 if needed.
- Any ASHA omeka scrape.

Luria: upload only if the editor accepts the Commons-stated PD caution.

## SEO / social (keep dull on purpose)

Title examples that match the pack voice:

- “Sara Stinchfield Hawk and the First American Doctorate in Speech”
- “Thirteen People in the Hotel McAlpin”

Avoid:

- “The Amazing Woman Who Invented Speech Therapy!”
- “10 Speech Pathologists Who Changed the World”

Excerpt: first 1–2 concrete sentences of the article, not a keyword list.

No medical schema (`MedicalWebPage`, `howTo`) on these posts. They are historical essays.

## Medical-legal

Add a sitewide footer on the History section, once:

> These essays are historical and educational. They are not treatment advice and they are not a substitute for evaluation by a licensed clinician.

Do not append a clinic booking widget to the 1939 Monster Study piece.

## Import tools

Reasonable paths:

1. Manual: copy body into Gutenberg, set categories, upload one image. Forty drafts is a weekend.
2. WP All Import / CSV: one row per article — `title, slug, content_html, category, tags, featured_image, custom_figure_dates`.
3. Static Markdown plugins exist; they fight with this theme later. Prefer HTML in WP.

If converting with Pandoc:

```bash
pandoc articles/26-sara-stinchfield-hawk.md -f markdown -t html -o /tmp/26.html
```

Then paste. Strip the YAML first.

## Publish waves

See `INDEX.md` (“Suggested publish waves”). Wave A is safe to put live first: origins, no open ethics crisis in the lead slot. Johnson / Monster Study (article 29) should not be the first public post.

## What not to merge

- Not into COSMOS docs, KDash, or `live/`.
- Not into figroots or furniture content packs.
- Not into the clinic’s service-page templates.

## After import (editor checklist)

- [ ] All 40 posts exist as **Draft**
- [ ] Featured images only where `portrait_status: downloaded`
- [ ] Placeholder block still visible on hunt profiles
- [ ] Internal links among the 40 rewritten from `.md` filenames to permalinks
- [ ] Bibliography page is a draft, not a public dump of URLs, unless the editor wants a “Further reading” page
- [ ] Live slpwow.com still untouched until a human hits Publish
