# WordPress import notes — staging only

Do not publish these posts on the live wowtherapies.com until a human editor and, for any service-adjacent line, counsel have signed the piece.

This is **not** an invitation to edit the production site. Staging, a local Docker WP, or a holding subdirectory is the ceiling.

## What you are importing

Markdown essays with YAML front matter under `articles/`. Forty-five posts. Ops files are **not** posts.

## Front matter → WP

| YAML | WordPress |
| --- | --- |
| `title` | post title |
| `slug` | post slug |
| `meta_description` | Yoast/Rank Math description (do not let the plugin rewrite it) |
| `tags` | post tags |
| `type` | custom field `wow_pack_type` (`era` / `figure` / `institution`) |
| `order` | custom field `wow_pack_order` |
| `portrait` | featured image only if `PORTRAIT_SOURCES.md` has a cleared file; else series template |
| `citations` | custom field (one source per line) plus a visible Sources block |
| `status: staging` | **Draft** on staging. Never map to `publish` on production. |
| `voice_check: human` | custom field. Internal QA flag, not a byline. |

Suggested post type: `post`. Category: `Trauma-Informed Care History` (create once). Optional second category `Figures` / `Eras`. Do not file under `Speech Therapy`, `PTSD Treatment`, or `Book an Evaluation`.

## Disclaimer block

Every essay already carries the educational note. In WP, make it a reusable block (`wow-tic-history-disclaimer`) and insert it after the dek **and** above the footer.

Suggested reusable text (must match the articles):

> **Educational note.** This is history for a general reader. It is not a diagnosis, not a treatment plan, and not a substitute for care with a licensed clinician.

## Import path (staging)

1. Copy this folder onto a machine that can reach **staging** WP. Do not paste essays into the live editor over email.
2. Convert MD → Gutenberg with a tool that preserves headings. Test `articles/01-what-trauma-informed-is-not.md` first.
3. Set author to a holding user (`editorial-history`), not a fabricated psychiatrist.
4. Featured image: `PHOTO_NOTES.md` + `PORTRAIT_SOURCES.md`. Series template when `portrait: none`.
5. `noindex, nofollow` on staging. Confirm robots and site visibility.
6. Disable "related services" / booking widgets on these posts until claims review.

## Things that must not auto-run

- SEO plugins rewriting titles or meta.
- Internal-link plugins that attach these posts to "PTSD treatment" or "anxiety" service pages. WOW Therapies does not have those service pages.
- Schema `MedicalWebPage`, `MedicalTherapy`, or `Drug`. `Article` only. No `treats` / `indication`.
- AI "expand this draft" buttons.
- Auto-featured-image plugins that pull a random stock face.

## Citations on the public page (later)

When a piece is actually cleared, render `citations` as a visible "Sources" list with outbound links. Do not use affiliate wrappers on PubMed, museum, or university URLs.

## Cross-links

Internal links among the forty-five slugs are welcome. One link to the counseling-heritage pack’s trauma-lineages and Herman essays is welcome. Do not auto-link to SLPWOW speech posts. A single series hub page may list the calendar from `INDEX.md`.

## Rollback

If a draft is imported to production by mistake: unpublish, `noindex`, remove from menus and sitemaps, keep the revision. Do not 301 a history URL to a booking form.

## Complementary site

SLPWOW community/history content stays on its own pack and domain lane. Shared house style is fine. Shared articles are not.
