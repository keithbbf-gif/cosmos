# WordPress import notes — drafts only

Do **not** deploy. This pack is git-tracked Markdown. A human editor decides the domain later.

## Suggested homes (pick later)

1. A dedicated industry blog on **modelraters.com** (`/blog/` or `/field-notes/`) if that domain is meant for public eval literacy. Waitlist-grade. No rater internals.
2. A **separate publishing domain** if counsel wants a clean wall between product and commentary.
3. Do not put this on a COSMOS, KDash, or live-tree host.

No DNS, no WP install, no plugin work in this PR.

## Front matter → WP fields

| YAML | WordPress |
| --- | --- |
| `title` | Post title |
| `slug` | Post slug (keep; do not auto-pretty) |
| `meta_description` | Yoast / Rank Math excerpt (≤155 chars; some drafts run long — trim at import) |
| `tags` | WP tags; also map `era_start` to a custom field `era_start` |
| `citations` | Footer "Sources" block, or a custom field JSON |
| `status: draft` | WP status **draft**. Never auto-publish. |
| `voice_check: edited` | Internal editorial flag; do not show on the public post |
| `voice_edited` | Internal date stamp; strip on import |
| `figures` | Media library attachments; HTML `<figure class="blog-figure">` blocks are already in the Markdown. Rewrite `../assets/` to the WP uploads path on import. |

Keep YAML in the Markdown for git. Strip it on import or use a front-matter plugin. Do not leave `voice_check` in the rendered HTML.

## Import method

- WP-CLI `wp post create --post_status=draft --post_title=... --post_name=...` from cleaned HTML, **or**
- A one-shot importer that reads `drafts/*.md`, rejects any file whose path is outside this folder, and sets status=draft.
- Manual copy into Gutenberg is fine for the first three posts.

Do not write a COSMOS job, a ledger event, or a fenced worker to publish these.

## Theme / layout

- Serif or a quiet sans. No neon "AI" gradients.
- Sources as a real footnote list, not a "further reading" dump of affiliate links.
- Dates in the body stay ISO-readable (28 May 2020), not "recently".
- Featured images: see `PHOTO_NOTES.md`. No generated fake UIs.

## Legal pass before first public post

- Counsel: brand names, waitlist lines, no novelty.
- Editor: `STYLE_GUIDE.md` bans.
- Fact check: every statute and EO against EUR-Lex / Federal Register, because US orders moved in 2025 and the AI Act timeline picked up Digital Omnibus notes in 2026.

## Suggested first ship (if anyone actually publishes)

01, 05, 09, 11 — API, ChatGPT, evals, law. Those four earn trust. Re-check 14 (Mariner died 4 May 2026; confirm the inheriting Gemini SKU), 38 (Colorado SB26-189), and any OSWorld percentage before a customer-facing post. Do not import all 42 in one week.
