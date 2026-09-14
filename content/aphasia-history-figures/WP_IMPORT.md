# WordPress Import — Aphasia History Pack

Staged. First import status is **Draft**. Do not auto-publish.

## Information architecture

Two parent archives:

- **Ages of aphasia** — `type: era` (articles 01–16)
- **People** — `type: profile` (articles 17–45)

Slug prefix (avoids colliding with clinic service pages and with the profession-history pack):

`/history/aphasia/<slug>/`

Examples:

- `/history/aphasia/the-year-1861/`
- `/history/aphasia/hildred-schuell/`

Do not hang these under `/services/` or `/adults/stroke-homework/`.

## Front-matter → WordPress map

| YAML | WordPress |
|------|-----------|
| `title` | Post title |
| `slug` | Post slug (do not auto-decorate) |
| `type: era` | Category: History — Ages of Aphasia |
| `type: profile` | Category: History — People |
| `tags` | Post tags |
| `portrait` | Always null in this pack — no featured image until a later rights-cleared file exists |
| `portrait_status: note` | Keep the Portrait section / placeholder in the body |
| `figure_dates` | Custom field `figure_dates` |
| `voice_check` | Custom field; hide from public |
| `series` | Custom field `series = slpwow-aphasia-history-figures` |
| `stage: draft` | WP status **Draft** on first import |
| `meta_description` | Excerpt / SEO description |
| `audience: slpwow` | unused publicly |

Strip the YAML before the post body. Do not print `voice_check: human` on the site.

## Markdown → blocks

- ATX `##` / `###` → heading blocks.
- Educational note → a muted intro paragraph or a “Note” block, not a popup.
- Portrait placeholder → a captioned empty frame, not an AI fill.

## Cross-links

After the sibling profession pack is imported, link Broca / Wernicke / Luria / Schuell / Goodglass both ways. Do not paste those articles into this tree.
