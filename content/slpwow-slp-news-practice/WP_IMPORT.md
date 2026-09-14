# WordPress import notes — draft only

Do not publish these posts live. Staging or a local import is the ceiling until a licensed SLP and editor sign a piece. Dollar figures need a second look against the live CMS page.

## What you are importing

Markdown drafts with YAML front matter under `articles/`. Forty-six posts plus this folder’s ops files. `INDEX.md`, `MANIFEST.md`, `STYLE_GUIDE.md`, `CLAIMS_GUARDRAILS.md`, `BIBLIOGRAPHY.md`, and `README.md` are editorial ops, not posts. Import in waves (see `INDEX.md`); do not dump forty-six drafts onto a live sitemap.

## Front matter → WP fields

| YAML | WordPress |
| --- | --- |
| `title` | post title |
| `slug` | post slug (keep; do not let WP “improve” it) |
| `meta_description` | Yoast / Rank Math / core custom field. Do not auto-generate. |
| `tags` | post tags. Create if missing. Do not add “speech therapy near me,” “best SLP,” disease+book-now. |
| `series` | custom field `series` = `slpwow-slp-news-practice` |
| `type` | custom field (`research-literacy` / `reimbursement` / `school-medical` / `practice-headline`) |
| `citations` | custom field (JSON or one URL per line). Also a visible Sources block when cleared. |
| `status: draft` / `stage: draft` | **Draft.** Never map to `publish` or `future`. |
| `voice_check` | strip on import (internal QA). |
| `audience` / `brand` | strip or store as custom fields; do not print. |

Suggested post type: `post`. Category: `SLP News` or `Practice news` (create once). Do not file under `Shop` or a city landing page. Do not merge with the pediatric-milestones or history calendars.

## Disclaimer block

Every draft already carries the educational disclaimer. In WP, make it a reusable block (`slpwow-slp-news-disclaimer`) and insert it after the dek *and* above the footer. Do not restyle it as a tiny gray line.

If a plugin strips blockquotes on import, put the disclaimer in a Custom HTML block.

## Import path (staging)

1. Copy the repo folder onto a machine that can reach staging WP.
2. Convert MD → Gutenberg with a tool that preserves headings. Test one post (`01`) first.
3. Set author to a holding user (`editorial-drafts`), not a made-up CCC-SLP who is not on the license wall.
4. Featured image: use the pack SVG for that slug (`featured_image` in front matter → upload SVG or exported PNG). No stock “sad elder with a sippy cup” as if it were a patient. No clinic photos of real patients without a signed release (this pack has none). Rights: `RIGHTS.md`.
5. Preserve `<figure>` / `<figcaption>` and `ImageObject` microdata from the markdown embeds (`embeds/<slug>.md`).
6. Disable “related services” / booking widgets on these posts until claims review.
7. `noindex, nofollow` on staging. Confirm robots and site visibility.
8. Keep `status=draft`. If the importer offers “publish,” decline.

## Things that must not auto-run

- SEO plugins rewriting titles or meta into disease keywords or “Medicare billing tips.”
- Internal-linking plugins that attach these posts to “book a swallow eval.”
- Schema `MedicalWebPage`, `MedicalCondition`, `Drug`, or `treats` / `indication`. `Article` or `NewsArticle` is enough.
- AI “expand this draft” buttons.
- Auto-updating dollar widgets that scrape a blog instead of CMS.

## Citations on the public page (later)

When a piece is actually cleared, render `citations` as a visible “Sources” list with outbound links. Do not hide CMS or ASHA. Do not use affiliate wrappers on those domains.

## Rollback

If a draft is imported to production by mistake: unpublish, `noindex`, remove from menus and sitemaps, keep the revision. Do not 301 to a booking URL.
