# WordPress import notes — draft only

Do not publish these posts live. Staging or a local import is the ceiling until a licensed SLP and editor sign a piece.

## What you are importing

Markdown drafts with YAML front matter under `articles/`. Forty-two posts plus this folder’s ops files. `INDEX.md`, `MANIFEST.md`, `STYLE_GUIDE.md`, `CLAIMS_GUARDRAILS.md`, `BIBLIOGRAPHY.md`, and `README.md` are editorial ops, not posts. Import in waves (see `INDEX.md`); do not dump forty-two drafts onto a live sitemap.

## Front matter → WP fields

| YAML | WordPress |
| --- | --- |
| `title` | post title |
| `slug` | post slug (keep; do not let WP “improve” it) |
| `meta_description` | Yoast / Rank Math / core custom field. Do not auto-generate. |
| `tags` | post tags. Create if missing. Do not add “autism,” “apraxia,” “speech delay treatment,” “best SLP.” |
| `series` | custom field `series` = `slp-pediatric-milestones` |
| `type` | custom field (`age-band` / `domain` / `parent-guide`) |
| `age_band` | custom field |
| `citations` | custom field (JSON or one URL per line). Also a visible Sources block when cleared. |
| `status: draft` / `stage: draft` | **Draft.** Never map to `publish` or `future`. |
| `voice_check` | strip on import (internal QA). |
| `audience` / `brand` | strip or store as custom fields; do not print. |

Suggested post type: `post`. Category: `Pediatric milestones` or `For families` (create once). Do not file under `Shop` or a city landing page.

## Disclaimer block

Every draft already carries the educational disclaimer. In WP, make it a reusable block (`slpwow-milestones-disclaimer`) and insert it after the dek *and* above the footer. Do not restyle it as a tiny gray line.

If a plugin strips blockquotes on import, put the disclaimer in a Custom HTML block.

## Import path (staging)

1. Copy the repo folder onto a machine that can reach staging WP.
2. Convert MD → Gutenberg with a tool that preserves headings. Test one post (`01`) first.
3. Set author to a holding user (`editorial-drafts`), not a made-up CCC-SLP who is not on the license wall.
4. Featured image: no stock “sad toddler at a table” as if it were a patient. No clinic photos of real children without a signed release (this pack has none).
5. Disable “related services” / booking widgets on these posts until claims review.
6. `noindex, nofollow` on staging. Confirm robots and site visibility.

## Things that must not auto-run

- SEO plugins rewriting titles or meta into disease keywords.
- Internal-linking plugins that attach these posts to “autism evaluation — book now.”
- Schema `MedicalWebPage`, `MedicalCondition`, `Drug`, or `treats` / `indication`. `Article` is enough.
- AI “expand this draft” buttons.

## Citations on the public page (later)

When a piece is actually cleared, render `citations` as a visible “Sources” list with outbound links. Do not hide CDC or ASHA. Do not use affiliate wrappers on those domains.

## Rollback

If a draft is imported to production by mistake: unpublish, `noindex`, remove from menus and sitemaps, keep the revision. Do not 301 to a booking URL.
