# WordPress import notes (staging only)

Staged Markdown + relative SVG. Not a live publish checklist.

## What to import

- One post per file in `articles/`.
- Title and slug from YAML. Keep `status: draft` until Keith clears.
- Body starts after the second `---` fence. Keep the disclaimer paragraph.
- Two figures per post: Markdown images point at `../assets/<slug>/*.svg`. On import, either
  - upload the 80 SVGs and rewrite URLs to the media library, or
  - serve `assets/` beside the posts so relative paths still resolve.

## What not to do

- Do not strip `<!-- graphics-pack:v1 -->` until a designer replaces the figures on purpose.
- Do not promote a WHO monograph, Ph. Eur. page, or DSHEA label into a disease claim in the excerpt.
- Do not auto-generate “key takeaways” or dose boxes. This pack has neither.
- Do not run `scripts/bootstrap_articles.py` against the filled tree.

## Excerpt / SEO

`meta_description` is the intended excerpt. Tags in YAML are editorial, not a WP taxonomy promise.

## Legal

See `CLAIMS_GUARDRAILS.md`. Historical use is not a modern indication. U.S. modern-aisle sentences should keep the DSHEA dull line.
