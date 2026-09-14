# WordPress Import

Staged Markdown in this pack is the editorial master. WordPress is a projection. Do not edit "live" in the CMS until a copy has been forked, or you will fork the voice.

## Recommended path

1. Copy `content/herbal-medicine-history-blog/` out of this repo onto the editorial machine. The COSMOS tree is not a CMS root.
2. Fact-check each draft against `BIBLIOGRAPHY.md`. Resolve `[soft:]` flags or keep them as in-text caution — do not delete caution to look finished.
3. Convert Markdown → Gutenberg or Classic.

### Option A — WP-CLI + a Markdown importer

If the site already uses a Markdown plugin (Jetpack Markdown, WP GitHuber MD, or a static-to-WP pipeline):

```bash
# example only — paths are the editor's
wp post create --post_type=post --post_status=draft \
  --post_title="The Ice Man's Two Mushrooms" \
  --post_excerpt="In 1991 a thaw on the Tisenjoch gave back a man who had packed fungus on a thong." \
  drafts/01-otzi-birch-polypore.md
```

Front matter is not native WP. Strip the YAML or map it:

| YAML | WordPress |
| --- | --- |
| `title` | post title |
| `slug` | post_name |
| `summary` | excerpt |
| `tags` | post_tag (create if missing) |
| `era`, `region` | custom taxonomies `era`, `region` — or a pair of custom fields |
| `sources_notes` | custom field `sources_notes` (not shown on the public template unless you want a sourced footer) |
| `photo` | featured-image alt + caption; the block in the body stays until a file is chosen |
| `legal_frame` | custom field; lock the public template to append an educational disclaimer if counsel wants one |
| `voice_check` | editorial only; do not print |

### Option B — Manual paste (safer for voice)

Open the draft, paste into a Gutenberg "Custom HTML" or a Markdown block, then:

- Convert H1 to the post title (do not leave a duplicate H1 in the body).
- Turn the photo slot into an image block + caption + credit.
- Add the educational footer (below) once per post, not once per paragraph.

### Option C — Static site first

Hugo / Eleventy can read the YAML as-is. Use that for a private preview. Export to WP later with a WXR file if the magazine's stack requires WP.

## Post settings

- **Status:** draft, then legal/medical read, then schedule.
- **Category suggestion:** `History` (parent), children `Pharmacopeias`, `Isolates`, `Regulation`, `Supplements as a category`.
- **Tags:** take from front matter; do not add `wellness`, `natural cure`, `detox`.
- **Author:** a named editor, not "Admin."
- **Discussion:** off until the magazine wants comments; this subject attracts cure spam.

## Excerpt rules

The `summary` field is written to be an excerpt. Do not let Yoast or an AI plugin rewrite it into "Discover the secrets of ancient healing." If an SEO plugin flags "low emotion," ignore it.

## Disclaimer block (optional, counsel-driven)

If the magazine's lawyer wants a sitewide note, use one short, dull paragraph — not a second essay:

> These articles are historical and educational. They are not medical advice, a diagnosis, or a product claim. Plant names and old indications are not instructions. Dietary supplements in the United States are regulated under the Dietary Supplement Health and Education Act of 1994 and related FDA rules; they are not approved as drugs to treat disease.

Do not pair that paragraph with a "shop the story" module.

## Images

Upload from rights-cleared files only (`PHOTO_NOTES.md`). Featured image: historical plate or document crop, 3:2 or 16:9, no fake lab. Filename: `herbal-hist-01-otzi-map.jpg` — not `stock-herb-123.jpg`.

Alt text: from the draft's photo caption, tightened.

## Internal links

Wave A essays may link forward to Dioscorides and the *Canon*; isolate essays may link back to the plant's older essay. Maximum three internal links per piece or the CMS will look like a web. Do not auto-link every binomial.

## What not to install

- Affiliate modules
- "Related products" from a supplement vendor
- Chat widgets that answer medical questions
- AI rewrite buttons on these posts

## Rollback

Keep the Markdown in git. If a WP editor "improves" a sentence into banned voice, revert from the file, not from memory.
