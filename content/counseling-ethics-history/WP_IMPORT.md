# WordPress import notes — staging only

Do not publish these posts on the live wowtherapies.com until a human editor
and, for any service-adjacent or legal-adjacent line, counsel have signed
the piece.

This is **not** an invitation to edit the production site. Staging, a local
Docker WP, or a holding subdirectory is the ceiling.

## What you are importing

Markdown essays with YAML front matter under `stage-*/`. Forty-eight posts.
Ops files are **not** posts:

`README.md`, `STYLE_GUIDE.md`, `GUARDRAILS.md`, `CITATIONS.md`,
`PORTRAIT_SOURCES.md`, `PHOTO_NOTES.md`, `WP_IMPORT.md`, `MANIFEST.toml`,
`tools/`.

Import in waves (`README.md` stage tables). Do not dump forty-eight URLs
onto a live sitemap in a week.

## Front matter → WP fields

| YAML | WordPress |
| --- | --- |
| `title` | post title |
| `slug` | post slug (keep; do not let WP "improve" it) |
| `meta_description` | Yoast / Rank Math / core custom field. Do not auto-generate. |
| `tags` | post tags. Create if missing. Do not add "book now," "best therapist," "file a complaint." |
| `type` | custom field `series_type` |
| `order` | custom field `series_order` (integer) |
| `stage` | custom field `series_stage` |
| `portrait` | custom field; this pack is almost all `none` |
| `citations` | custom field. Also a visible "Sources" block. |
| `status: draft` | Map to **Draft** or **Pending review** on staging. Never map straight to `publish` on production. |
| `voice` / `voice_check` | custom fields. Internal QA flags, not bylines. |

Suggested post type: `post`. Category: `Counseling Ethics History` (create
once). Do not file under `Speech Therapy` or `Book an Evaluation`.

## Disclaimer block

Every essay already carries the educational note and a Claims box. In WP,
make the educational note a reusable block (`wow-ethics-history-disclaimer`)
and insert it after the dek **and** keep the Claims box before Sources.

Suggested reusable text (must match the articles):

> **Educational note.** This is history for a general reader. It is not a diagnosis, not a treatment plan, and not a substitute for care with a licensed clinician.

## Import path (staging)

1. Copy this folder onto a machine that can reach **staging** WP. Do not
   paste essays into the live editor over email.
2. Convert MD → Gutenberg with a tool that preserves headings. Test
   `stage-01-how-to-read/01-what-this-folder-refuses.md` first.
3. Set author to a holding user (`editorial-history`), not a fabricated
   ethicist or psychiatrist.
4. Featured image: `PHOTO_NOTES.md` + `PORTRAIT_SOURCES.md`. Series
   template when `portrait: none`.
5. `noindex, nofollow` on staging. Confirm robots and site visibility.
6. Disable "related services" / booking widgets on these posts until
   claims review.
7. Do not auto-insert the current APA, ACA, or NASW code as a PDF.

## Things that must not auto-run

- SEO plugins rewriting titles or meta.
- Internal-link plugins that attach these posts to speech, OT, PT, or
  "anxiety treatment" service pages.
- Schema `MedicalWebPage`, `MedicalTherapy`, or `Drug`. `Article` only.
  No `treats` / `indication`.
- Schema that implies legal services.
- AI "expand this draft" buttons.
- Auto-featured-image plugins that pull a random stock face or a gavel.

## Citations on the public page (later)

When a piece is actually cleared, render `citations` as a visible "Sources"
list with outbound links to the **association's own page** for the living
code. Do not host the code. Do not use affiliate wrappers on PubMed,
court, or university URLs.

## Cross-links

Internal links among the forty-eight slugs are welcome (1953 Hobbs ↔ 2002
Fisher ↔ Hoffman). Do not auto-link to SLPWOW speech posts. A single
series hub page may list the stages from `README.md`.

## Rollback

If a draft is imported to production by mistake: unpublish, `noindex`,
remove from menus and sitemaps, keep the revision. Do not 301 a history
URL to a booking form.

## Complementary site

SLPWOW community/history content stays on its own pack and domain lane.
The counseling-heritage pack stays on its calendar. Shared house style is
fine. Shared articles are not.
