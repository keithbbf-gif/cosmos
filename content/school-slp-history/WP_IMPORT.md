# WordPress Import — School SLP History Pack

Staged. First import status is **Draft**. Do not auto-publish.

## Information architecture

Two parent archives:

- **Ages of the school job** — `type: era` (articles 01–22, 28–34, 41–45)
- **People and captions** — `type: profile` (articles 23–27, 35–40)

Slug prefix (avoids colliding with clinic service pages and with the profession-history pack):

`/history/schools/<slug>/`

Examples:

- `/history/schools/november-29-1975/`
- `/history/schools/amy-rowley-1982/`

Do not hang these under `/services/` or `/school-age/speech-homework/`.

## Front-matter → WordPress map

| YAML | WordPress |
|------|-----------|
| `title` | Post title |
| `slug` | Post slug (do not auto-decorate) |
| `type: era` | Category: History — School Ages |
| `type: profile` | Category: History — People & Captions |
| `tags` | Post tags |
| `portrait` | Always null in this pack — no featured image until a later rights-cleared file exists |
| `portrait_status: note` | Keep the Portrait section / placeholder in the body |
| `figure_dates` | Custom field `figure_dates` |
| `voice_check` | Custom field; hide from public |
| `series` | Custom field `series = slpwow-school-slp-history` |
| `stage: draft` | WP status **Draft** on first import |
| `meta_description` | Excerpt / SEO description |
| `audience: slpwow` | unused publicly |

Strip the YAML before the post body. Do not print `voice_check: human` on the site.

## Markdown → blocks

- ATX `##` / `###` → heading blocks.
- Educational note → a muted intro paragraph or a “Note” block, not a popup.
- Portrait placeholder → a captioned empty frame, not an AI fill.

## Cross-links

After the sibling profession pack is imported, link Gifford (charter ASHA) and the 1925 academy both ways. Do not paste those articles into this tree. Do not file Rowley under the fluency pack.
