# WordPress import notes — staging only

Do not publish these posts on the live wowtherapies.com until a human editor and, for any service-adjacent line, counsel have signed the piece.

This is **not** an invitation to edit the production site. Staging, a local Docker WP, or a holding subdirectory is the ceiling.

## What you are importing

Markdown essays with YAML front matter under `articles/`. Forty-four posts. Ops files are **not** posts:

`INDEX.md`, `MANIFEST.md`, `STYLE_GUIDE.md`, `CLAIMS_GUARDRAILS.md`, `BIBLIOGRAPHY.md`, `PORTRAIT_SOURCES.md`, `PHOTO_NOTES.md`, `WP_IMPORT.md`, `README.md`.

Import in waves (`INDEX.md`). Do not dump forty-four URLs onto a live sitemap in a week.

## Front matter → WP fields

| YAML | WordPress |
| --- | --- |
| `title` | post title |
| `slug` | post slug (keep; do not let WP "improve" it) |
| `meta_description` | Yoast / Rank Math / core custom field. Do not auto-generate. |
| `tags` | post tags. Create if missing. Do not add "PTSD group," "book now," "best therapist." |
| `type` | custom field `series_type` = `era` or `figure` |
| `order` | custom field `series_order` (integer) |
| `portrait` | custom field; values `pd`, `cc`, `confirm`, `none` |
| `citations` | custom field (one URL or ISBN per line). Also a visible "Sources" block. |
| `status: publishable` | Map to **Draft** or **Pending review** on staging. Never map straight to `publish` on production. |
| `voice_check: human` | custom field. Internal QA flag, not a byline. |

Suggested post type: `post`. Category: `Group Therapy History` (create once). A second category `Figures` / `Eras` is optional. Do not file under `Speech Therapy`, `Book an Evaluation`, or the individual `Therapy History` category without a hub note.

## Disclaimer block

Every essay already carries the educational note. In WP, make it a reusable block (`wow-group-therapy-history-disclaimer`) and insert it after the dek **and** above the footer.

If a plugin strips blockquotes on import, use a Custom HTML block.

Suggested reusable text (must match the articles):

> **Educational note.** This is history for a general reader. It is not a diagnosis, not a treatment plan, and not a substitute for care with a licensed clinician.

## Import path (staging)

1. Copy this folder onto a machine that can reach **staging** WP. Do not paste essays into the live editor over email.
2. Convert MD → Gutenberg with a tool that preserves headings. Test `articles/01-before-the-circle.md` first.
3. Set author to a holding user (`editorial-history`), not a fabricated group analyst.
4. Featured image: `PHOTO_NOTES.md` + `PORTRAIT_SOURCES.md`. Series template when `portrait: none`.
5. `noindex, nofollow` on staging. Confirm robots and site visibility.
6. Disable "related services" / booking widgets on these posts until claims review.

## Things that must not auto-run

- SEO plugins rewriting titles or meta.
- Internal-link plugins that attach these posts to "anxiety treatment" or "join our group" service pages.
- Schema `MedicalWebPage`, `MedicalTherapy`, or `Drug`. `Article` only. No `treats` / `indication`.
- AI "expand this draft" buttons.
- Auto-featured-image plugins that pull a random stock circle of smiling strangers.

## Citations on the public page (later)

When a piece is actually cleared, render `citations` as a visible "Sources" list with outbound links. Do not use affiliate wrappers on PubMed, museum, or university URLs.

## Cross-links

Internal links among the forty-four slugs are welcome (Pratt ↔ Boston classes ↔ Slavson). Cross-link *once* to the individual therapy-history hub if that pack is imported. Do not auto-link to SLPWOW speech posts. A single series hub page may list the calendar from `INDEX.md`.

## Rollback

If a draft is imported to production by mistake: unpublish, `noindex`, remove from menus and sitemaps, keep the revision. Do not 301 a history URL to a booking form.

## Complementary site lanes

Individual psychotherapy history and SLPWOW community/history content stay on their own packs. Shared house style is fine. Shared articles are not.
