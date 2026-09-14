# WordPress import notes — staging only

Do not publish these posts on the live wowtherapies.com until a human editor and, for any service-adjacent line, counsel have signed the piece.

This is **not** an invitation to edit the production site. Staging, a local Docker WP, or a holding subdirectory is the ceiling.

## What you are importing

Markdown essays with YAML front matter under `drafts/`. Forty-four posts. Ops files are **not** posts:

`INDEX.md`, `MANIFEST.md`, `STYLE_GUIDE.md`, `CLAIMS_GUARDRAILS.md`, `BIBLIOGRAPHY.md`, `PORTRAIT_SOURCES.md`, `PHOTO_NOTES.md`, `WP_IMPORT.md`.

Import in waves (`INDEX.md`). Do not dump forty-four URLs onto a live sitemap in a week.

## Front matter → WP fields

| YAML | WordPress |
| --- | --- |
| `title` | post title |
| `slug` | post slug (keep; do not let WP "improve" it) |
| `meta_description` | Yoast / Rank Math / core custom field. Do not auto-generate. |
| `tags` | post tags. Create if missing. Do not add "CBT treatment," "book now," "best therapist." |
| `type` | custom field `series_type` = `era` or `figure` |
| `order` | custom field `series_order` (integer) |
| `portrait` | custom field; values `pd`, `cc`, `confirm`, `none` |
| `citations` | custom field (one URL or ISBN per line). Also a visible "Sources" block. |
| `status: publishable` | Map to **Draft** or **Pending review** on staging. Never map straight to `publish` on production. |
| `voice_check: human` | custom field. Internal QA flag, not a byline. |

Suggested post type: `post`. Category: `Therapy History` (create once) and a child or second category `CBT History`. Do not file under `Speech Therapy` or `Book an Evaluation`.

## Disclaimer block

Every essay already carries the educational note. In WP, make it a reusable block (`wow-therapy-history-disclaimer`) and insert it after the dek **and** above the footer.

If a plugin strips blockquotes on import, use a Custom HTML block.

Suggested reusable text (must match the articles):

> **Educational note.** This is history for a general reader. It is not a diagnosis, not a treatment plan, and not a substitute for care with a licensed clinician.

## Import path (staging)

1. Copy this folder onto a machine that can reach **staging** WP. Do not paste essays into the live editor over email.
2. Convert MD → Gutenberg with a tool that preserves headings. Test `drafts/01-stoic-sentences-before-the-clinic.md` first.
3. Set author to a holding user (`editorial-history`), not a fabricated psychiatrist.
4. Featured image: `PHOTO_NOTES.md` + `PORTRAIT_SOURCES.md`. Series template when `portrait: none`.
5. `noindex, nofollow` on staging. Confirm robots and site visibility.
6. Disable "related services" / booking widgets on these posts until claims review.

## Things that must not auto-run

- SEO plugins rewriting titles or meta.
- Internal-link plugins that attach these posts to "anxiety treatment" or "depression treatment" service pages.
- Schema `MedicalWebPage`, `MedicalTherapy`, or `Drug`. `Article` only. No `treats` / `indication`.
- AI "expand this draft" buttons.
- Auto-featured-image plugins that pull a random stock face.

## Citations on the public page (later)

When a piece is actually cleared, render `citations` as a visible "Sources" list with outbound links. Do not use affiliate wrappers on PubMed, museum, or university URLs.

## Cross-links

Internal links among the forty-four slugs are welcome (Beck ↔ 1967 book ↔ 1979 manual ↔ Judith Beck). Cross-link the sibling pack slugs `cognitive-therapy-empirical-turn`, `third-wave-mindfulness-clinic`, `aaron-beck`, `albert-ellis` as "wider house" — do not paste those essays into this folder. Do not auto-link to SLPWOW speech posts.

## Rollback

If a draft is imported to production by mistake: unpublish, `noindex`, remove from menus and sitemaps, keep the revision. Do not 301 a history URL to a booking form.

## Complementary site

SLPWOW community/history content stays on its own pack and domain lane. Shared house style is fine. Shared articles are not.
