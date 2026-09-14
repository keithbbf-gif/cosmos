# WordPress Import — AAC History Pack

Staged. First import status is **Draft**. Do not auto-publish.

## Information architecture

Two parent archives:

- **Ages of AAC** — `type: era` (articles 01–16)
- **People** — `type: profile` (articles 17–45)

Slug prefix (avoids colliding with clinic service pages and with sibling history packs):

`/history/aac/<slug>/`

Examples:

- `/history/aac/a-field-names-itself/`
- `/history/aac/david-r-beukelman/`

Do not hang these under `/services/` or `/aac-devices-for-sale/`.

## Front-matter → WordPress map

| YAML | WordPress |
|------|-----------|
| `title` | Post title |
| `slug` | Post slug (do not auto-decorate) |
| `type: era` | Category: History — Ages of AAC |
| `type: profile` | Category: History — People |
| `tags` | Post tags |
| `portrait` | Always null in this pack — no featured image until a later rights-cleared file exists |
| `portrait_status: note` or `placeholder` | Keep the Portrait section / placeholder in the body |
| `figure_dates` | Custom field `figure_dates` |
| `voice_check` | Custom field; hide from public |
| `series` | Custom field `series = slpwow-aac-history-figures` |
| `stage: draft` | WP status **Draft** on first import |
| `meta_description` | Excerpt / SEO description |
| `audience: slpwow` | unused publicly |

Strip the YAML before the post body. Do not print `voice_check: human` on the site.

## Markdown → blocks

- ATX `##` / `###` → heading blocks.
- Educational note → a muted intro paragraph or a “Note” block, not a popup.
- Portrait placeholder → a captioned empty frame, not an AI fill.

## Cross-links

After sibling packs are imported, link de l’Épée / Eugene T. McDonald to the profession series, and leave Broca / Wernicke in the aphasia series. Do not paste those articles into this tree.
