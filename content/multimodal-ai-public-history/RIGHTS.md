# Rights — multimodal-ai-public-history graphics

## Scope

This file covers **original vector figures** under `graphics/` and the HTML `<figure>` embeds documented in `EMBEDS.md`. It does **not** change the copyright status of cited papers, model weights, or third-party screenshots (this pack does not ship those).

## Authorship and license

| Asset | Author | License |
| --- | --- | --- |
| `graphics/fig-*.svg` | COSMOS content draft (original diagrams) | **CC0 1.0** ([Creative Commons Zero](https://creativecommons.org/publicdomain/zero/1.0/)) |
| `EMBEDS.md` figure HTML snippets | Same | **CC0 1.0** |
| Essay prose in `stage-*/*.md` | Draft series authors | Not published; see series `README.md` |

You may copy, modify, and redistribute the SVGs without attribution, though attribution is appreciated: *Public multimodal AI history — COSMOS draft series*.

## What we deliberately did not include

- **No AI-generated faces or photorealistic people.** Diagrams use typography, geometry, and abstract tokens only.
- **No embedded raster photographs** of researchers, celebrities, or dataset samples.
- **No logos or trademarks** copied from vendors (OpenAI, Google, Stability, etc.). Names appear as plain text labels where needed for history, not as official marks.
- **No model outputs** passed off as illustrations. These figures are editorial schematics, not samples from DALL·E, Midjourney, or Stable Diffusion.

## Third-party content in essays

Markdown drafts may **name** public papers, blog posts, and products. That is citation, not reproduction. Do not paste copyrighted paper text or scrape images from papers into this tree without a separate rights review.

## Publish gate

Before flipping any essay from `status: draft` to a published URL:

1. Re-read this file and `GRAPHICS_INDEX.md`.
2. Run `python3 check_graphics.py` (must print `PASS`).
3. Confirm no new SVG introduces `<image href="...">` raster embeds without an explicit row in `GRAPHICS_INDEX.md` and an updated credit block here.
