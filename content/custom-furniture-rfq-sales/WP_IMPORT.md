# WordPress import notes — staging only

Do not publish these posts live. Staging or a local import is the ceiling until an editor and counsel sign a piece.

## What you are importing

Markdown drafts with YAML front matter under `articles/`. Forty-four posts plus this folder's ops files. `INDEX.md`, `MANIFEST.md`, `STYLE_GUIDE.md`, `CLAIMS_GUARDRAILS.md`, `BIBLIOGRAPHY.md`, and `PHOTO_NOTES.md` are editorial ops, not posts. Import in waves (see `INDEX.md`); do not dump the folder onto a live sitemap.

## Front matter → WP fields

| YAML | WordPress |
| --- | --- |
| `title` | post title |
| `slug` | post slug (keep; do not let WP "improve" it) |
| `meta_description` | Yoast / Rank Math / core custom field. Do not auto-generate. |
| `dek` | excerpt |
| `tags` | post tags. Create if missing. Do not add "luxury," "investment piece," "shop now." |
| `topic` | one category |
| `series` | tag `custom-furniture-rfq-sales` |
| `era_focus` | custom field `era_focus` |
| `citations` | custom field `citations` (JSON or one URL per line) |
| `status: draft` | **Draft.** Never map to `publish` or `future`. |
| `voice_check: human` | custom field. Internal QA flag, not a displayed byline. |

Suggested post type: `post`. Category: `Custom orders` (create once). Do not file under `Shop` or `Sale`.

## Disclaimer block

Every draft already carries the educational disclaimer. In WP, make it a reusable block (`furniture-rfq-disclaimer`) and insert it after the dek *and* above the footer. Do not restyle it as a tiny gray line.

If a plugin strips blockquotes on import, put the disclaimer in a Custom HTML block.

## Import path (staging)

1. Copy the repo folder onto a machine that can reach staging WP. Do not paste drafts into a live editor over email.
2. Convert MD → Gutenberg with a tool that preserves headings and tables. Test one post (`01`) first.
3. Set author to a holding user (`editorial-drafts`), not a made-up designer.
4. Featured image: follow `PHOTO_NOTES.md`. No stock "happy couple on a white sofa" as if it were our shop.
5. Disable WooCommerce upsells and "related products" on these posts until claims review.
6. `noindex, nofollow` on staging. Confirm robots and site visibility.

## Things that must not auto-run

- SEO plugins rewriting titles or meta.
- "Internal linking" plugins that attach these posts to SKU pages with "buy now."
- Schema `Offer` or `Product` with a price. `Article` is enough. These posts are not offers.
- AI "expand this draft" buttons. The style guide is the opposite of that.
- Chat widgets that open with a discount code.

## Citations on the public page (later)

When a piece is actually cleared, render `citations` as a visible "Sources" list with outbound links. Do not hide CFR or UCC cites. Do not use affiliate wrappers on ftc.gov, ecfr.gov, or law.cornell.edu.

## Rollback

If a draft is imported to production by mistake: unpublish, `noindex`, remove from menus and sitemaps, keep the revision. Do not leave a 301 to a product URL or a "request a quote" landing page that implies the draft was a live offer.
