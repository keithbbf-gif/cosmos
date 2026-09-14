# WordPress import notes — draft only

Do not publish these posts live. Staging or a local import is the ceiling until science/QA and counsel sign a piece.

## What you are importing

Markdown drafts with YAML front matter under `drafts/`. Forty-four posts plus this folder's ops files. `INDEX.md`, `MANIFEST.md`, `STYLE_GUIDE.md`, `CLAIMS_GUARDRAILS.md`, `BIBLIOGRAPHY.md`, `README.md`, and `PHOTO_NOTES.md` are editorial ops, not posts.

**Import in waves** (see `INDEX.md`). Do not dump forty-four drafts onto a live sitemap. Wave 1 first. If the staging site can only hold six, hold 01, 08, 10, 37, 38, 44.

## Front matter → WP fields

| YAML | WordPress |
| --- | --- |
| `title` | post title |
| `slug` | post slug (keep; do not let WP "improve" it) |
| `meta_description` | Yoast / Rank Math / core custom field. Do not auto-generate. |
| `summary` | excerpt. Do not let an SEO plugin rewrite it into "boost your gut." |
| `tags` | post tags. Create if missing. Do not add "wellness," "immune boosting," "leaky gut," "psychobiotic cure." |
| `era_focus` | custom field `era_focus` (string year) |
| `wave` | custom field `wave` (integer 1–6). Use for menus, not for "part 1 of a protocol." |
| `featured_image` | optional. Repo-relative SVG path for wired drafts (`IMAGE_SEO.md`). |
| `figure_alt` | optional. Matches `<img alt>` for importers. |
| `citations` | custom field `citations`. Also paste into a closed HTML comment or footnote block. |
| `status: draft` | **Draft.** Never map to `publish` or `future`. |
| `voice_check: human` | custom field. Internal QA flag. Not a displayed byline. |
| `legal_frame: educational-research` | custom field. If a plugin wants `MedicalWebPage`, refuse. |

Suggested post type: `post`. Category: `Microbiome research literacy` (create once). Do not file under `Shop`, `Gut health`, or `Science-backed products`.

## Disclaimer block

Every draft already carries the DSHEA disclaimer. In WP, make it a reusable block (`microbiome-dshea-disclaimer`) and insert it after the dek *and* above the footer. Do not restyle it as a tiny gray line.

Hospital/drug pieces (10, 36, 37, 38) need a second line in that block: this essay describes research and regulation; it is not an indication for a dietary supplement.

## Import path (staging)

1. Copy the repo folder onto a machine that can reach staging WP. Do not paste drafts into a live editor over email.
2. Convert MD → Gutenberg with a tool that preserves headings and tables. Test one post (`01`) first.
3. Set author to a holding user (`editorial-drafts`), not a made-up PhD or "our microbiome team."
4. Featured image: use `featured_image` YAML when present; else follow `PHOTO_NOTES.md`. No stock "scientist holding a glowing gut." No AI faces.
5. Disable "related products" / WooCommerce upsells on these posts until claims review.
6. `noindex, nofollow` on staging. Confirm robots and site visibility.

## Things that must not auto-run

- SEO plugins rewriting titles or meta into disease keywords.
- Internal-linking plugins that attach these posts to SKU pages with *C. diff*, IBS, weight, or mood keywords.
- Schema `MedicalWebPage`, `Drug`, or `treats` / `indication`. `Article` is enough.
- AI "expand this draft" buttons. The style guide is the opposite of that.

## Citations on the public page (later)

When a piece is actually cleared, render `citations` as a visible "Sources" list with outbound links. Do not hide PMIDs. Do not use affiliate wrappers on FDA.gov, PubMed, FTC.gov, or ISAPP.

## Rollback

If a draft is imported to production by mistake: unpublish, `noindex`, remove from menus and sitemaps, keep the revision. Do not leave a 301 to a product URL.
