# WordPress import notes — staging only

Do not publish these posts live. Staging or a local import is the ceiling until science/QA and counsel sign a piece.

## What you are importing

Markdown drafts with YAML front matter under `articles/`. Forty-four posts plus this folder's ops files. `INDEX.md`, `MANIFEST.md`, `STYLE_GUIDE.md`, `CLAIMS_GUARDRAILS.md`, `BIBLIOGRAPHY.md`, and `PHOTO_NOTES.md` are editorial ops, not posts. Import in waves (see `INDEX.md`); do not dump the folder onto a live sitemap.

## Front matter → WP fields

| YAML | WordPress |
| --- | --- |
| `title` | post title |
| `slug` | post slug (keep; do not let WP "improve" it) |
| `meta_description` | Yoast / Rank Math / core custom field. Do not auto-generate. |
| `tags` | post tags. Create if missing. Do not add "wellness," "immune boosting," "anti-aging," "detox." |
| `era_focus` | custom field `era_focus` (string year) |
| `citations` | custom field `citations` (JSON or one URL per line). Also paste into a closed HTML comment or footnote block. |
| `status: draft` | **Draft.** Never map to `publish` or `future`. |
| `voice_check: human` | custom field. Internal QA flag, not a displayed byline. |

Suggested post type: `post`. Category: `Manufacturing literacy` (create once). Do not file under `Shop` or `Science-backed products`.

## Disclaimer block

Every draft already carries the DSHEA disclaimer. In WP, make it a reusable block (`supplements-dshea-disclaimer`) and insert it after the dek *and* above the footer. Do not restyle it as a tiny gray line.

If a plugin strips blockquotes on import, put the disclaimer in a Custom HTML block.

## Import path (staging)

1. Copy the repo folder onto a machine that can reach staging WP. Do not paste drafts into a live editor over email.
2. Convert MD → Gutenberg with a tool that preserves headings and tables. Test one post (`01`) first.
3. Set author to a holding user (`editorial-drafts`), not a made-up PhD.
4. Featured image: follow `PHOTO_NOTES.md`. No stock "scientist holding pipette" as if it were our lab.
5. Disable "related products" / WooCommerce upsells on these posts until claims review.
6. `noindex, nofollow` on staging. Confirm robots and site visibility.

## Things that must not auto-run

- SEO plugins rewriting titles or meta.
- "Internal linking" plugins that attach these posts to SKU pages with disease keywords.
- Schema `MedicalWebPage` or `Drug` markup. `Article` is enough. Do not emit `treats` / `indication` schema.
- AI "expand this draft" buttons. The style guide is the opposite of that.

## Citations on the public page (later)

When a piece is actually cleared, render `citations` as a visible "Sources" list with outbound links. Do not hide CFR cites or warning-letter URLs. Do not use affiliate wrappers on FDA.gov, eCFR, USP.org, or FTC.gov.

## Rollback

If a draft is imported to production by mistake: unpublish, `noindex`, remove from menus and sitemaps, keep the revision. Do not leave a 301 to a product URL.
