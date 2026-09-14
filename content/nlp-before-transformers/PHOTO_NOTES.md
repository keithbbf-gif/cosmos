# Photo and figure policy — nlp-before-transformers

## Quality over speed

- Timelines must cite **public years** already argued in the essay; run `build_pack_data.py` after
  prose edits so anchors track the text.
- Concept charts are **schematics**, not reproduced paper figures.
- One archival plate per essay from `REGISTRY.toml` — prefer PD diagrams and hardware without
  people in frame.

## SEO embed contract

Each essay carries three `<figure>` blocks immediately after the lead paragraph:

- `alt` — full sentence, unique per figure, includes the essay topic.
- `figcaption` — numbered figure, print-safe credit for archival plates.
- `loading="lazy"` and `decoding="async"` on `<img>`.

Frontmatter additions: `meta_description`, `figure_id`, `figures`, `image_rights`, `image_pass`,
`portrait: null`.

## Forbidden

- AI-generated faces or “researcher portrait” clip art
- Scraped leaderboard tables or benchmark marketing screenshots
- Uncredited paper figure scans
