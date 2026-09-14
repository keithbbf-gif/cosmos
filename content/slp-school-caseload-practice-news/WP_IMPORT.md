# WordPress import notes — draft only

Do not publish these posts live. Staging or a local import is the ceiling until a licensed SLP and editor sign a piece.

## What you are importing

Markdown drafts with YAML front matter under `articles/`. Forty-four posts plus this folder’s ops files. `INDEX.md`, `MANIFEST.md`, `STYLE_GUIDE.md`, `CLAIMS_GUARDRAILS.md`, `BIBLIOGRAPHY.md`, and `README.md` are editorial ops, not posts. Import in waves (see `INDEX.md`); do not dump forty-four drafts onto a live sitemap.

## Front matter → WP fields

| YAML | WordPress |
| --- | --- |
| `title` | post title |
| `slug` | post slug (keep; do not let WP “improve” it) |
| `meta_description` | Yoast / Rank Math / core custom field. Do not auto-generate. |
| `tags` | post tags. Create if missing. Do not add “autism treatment,” “best school SLP,” “caseload lawsuit.” |
| `series` | custom field `series` = `slp-school-caseload-practice-news` |
| `type` | custom field (`news-explainer` / `practice-explainer` / `caseload-explainer` / `series-map`) |
| `citations` | custom field (JSON or one URL per line). Also a visible Sources block when cleared. |
| `status: draft` / `stage: draft` | **Draft.** Never map to `publish` or `future`. |
| `voice_check` / `voice_check_date` | strip on import (internal QA). |
| `audience` / `brand` | strip or store as custom fields; do not print. |

Suggested post type: `post`. Category: `School practice` or `SLP News` (create once). Do not file under `Shop` or a city landing page.

## Disclaimer block

Every draft already carries the educational / no-PHI disclaimer. In WP, make it a reusable block (`slpwow-school-caseload-disclaimer`) and insert it after the dek *and* above the footer. Do not restyle it as a tiny gray line.

If a plugin strips blockquotes on import, put the disclaimer in a Custom HTML block.

## Import path (staging)

1. Copy the repo folder onto a machine that can reach staging WP.
2. Convert MD → Gutenberg with a tool that preserves headings. Test one post (`01`) first.
3. Set author to a holding user (`editorial-drafts`), not a made-up CCC-SLP who is not on the license wall.
4. Featured image: no stock “sad child in speech therapy” as if it were a student. No classroom photos of real children. This pack has no patient images.
5. Disable booking widgets and “related services” on these posts until claims review.
6. `noindex, nofollow` on staging. Confirm robots and site visibility.

## Things that must not auto-run

- SEO plugins rewriting titles or meta into disease or lawsuit keywords.
- Internal-linking plugins that attach these posts to “autism evaluation — book now.”
- Schema `MedicalWebPage`, `MedicalCondition`, `Drug`, or `treats` / `indication`. `Article` is enough.
- AI “expand this draft” buttons.
- Auto-insert of student-looking stock photos.

## Citations on the public page (later)

When a piece is actually cleared, render `citations` as a visible “Sources” list with outbound links. Do not hide ASHA, IDEA.ed.gov, or CMS. Do not use affiliate wrappers on those domains.

## Rollback

If a draft is imported to production by mistake: unpublish, `noindex`, remove from menus and sitemaps, keep the revision. Do not 301 to a booking URL.
