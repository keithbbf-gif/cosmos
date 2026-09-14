# WordPress import notes — staging only

Do not publish these posts on the live wowtherapies.com until a human editor
and, for any service-adjacent line, counsel have signed the piece.

This is **not** an invitation to edit the production site. Staging, a local
Docker WP, or a holding subdirectory is the ceiling.

## What you are importing

Markdown essays with YAML front matter under `stage-*/`. Forty-five drafts.
Ops files are **not** posts:

`README.md`, `GUARDRAILS.md`, `STYLE_GUIDE.md`, `CITATIONS.md`,
`PHOTO_NOTES.md`, `PORTRAIT_SOURCES.md`, `WP_IMPORT.md`, `MANIFEST.toml`.

Import in waves (see `README.md` stages). Do not dump forty-five URLs onto a
live sitemap in a week.

## Front matter → WP fields

| YAML | WordPress |
| --- | --- |
| `title` | post title |
| `slug` | post slug (keep) |
| `stage` / `stage_name` | custom fields |
| `status: draft` | **Draft** or **Pending review** on staging. Never `publish` on production. |
| `claims_posture` | custom field. Internal. |

Suggested post type: `post`. Category: `Therapy History` (create once).
Optional child category: `ACT & mindfulness history`. Do not file under
`Book an Evaluation` or `Speech Therapy`.

## Disclaimer

Every essay already carries the educational note and a Claims box. In WP,
make the educational note a reusable block (`wow-act-history-disclaimer`).

> **Educational note.** This is history for a general reader. It is not a
> diagnosis, not a treatment plan, and not a substitute for care with a
> licensed clinician.

## Things that must not auto-run

- SEO plugins rewriting titles or meta.
- Internal-link plugins that attach these posts to "anxiety treatment"
  service pages.
- Schema `MedicalWebPage`, `MedicalTherapy`, or `Drug`. `Article` only.
- AI "expand this draft" buttons.
- Auto-featured-image plugins that pull a stock meditating face.

## Rollback

If a draft is imported to production by mistake: unpublish, `noindex`, remove
from menus and sitemaps, keep the revision. Do not 301 a history URL to a
booking form.
