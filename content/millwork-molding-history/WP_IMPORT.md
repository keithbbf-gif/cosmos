# WordPress import notes (staging only)

Staged Markdown + relative SVG. Not a live publish checklist.

## What to import

- One post per file in `articles/`.
- Title and slug from YAML. Keep `status: draft` until Keith clears.
- Body starts after the second `---` fence. Keep the disclaimer paragraph.
- Two figures per post: Markdown images point at `../assets/<slug>/*.svg`. On import, either
  - upload the 88 SVGs and rewrite URLs to the media library, or
  - serve `assets/` beside the posts so relative paths still resolve.

## What not to do

- Do not strip `<!-- graphics-pack:v1 -->` until a designer replaces the figures on purpose.
- Do not promote a shop essay into a bid, an ADA review, or a grind template.
- Do not auto-generate “key takeaways” or SKU boxes. This pack has neither.
- Do not invent client names from the BBF healthcare list.

## Excerpt / SEO

`meta_description` is the intended excerpt. Tags in YAML are editorial, not a WP taxonomy promise. `lane: bbf-millwork` stays in front matter for Website-GC routing.
