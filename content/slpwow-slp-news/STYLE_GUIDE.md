# Style guide — SLPWOW SLP News (stage 46)

## Reader

Working SLPs, audiologists in shared settings, school administrators, and informed families reading policy and workforce news — not alarm headlines.

## Voice

- Name the document (Commission PDF, CMS FAQ, ASHA survey), not the outrage.
- Ban SEO slop: *delve, leverage, game-changer, in conclusion, whether you're a…*
- Pack prose already follows `CLAIMS_GUARDRAILS.md`; graphics captions stay equally plain.

## SEO figures

- One primary `<figure>` per article with `itemscope itemtype="https://schema.org/ImageObject"`.
- `alt` describes the schematic for screen readers and image search (facts, not marketing).
- `<figcaption>` uses **Figure 1.**, states schematic intent, and includes the credit span.
- `loading="lazy"` with explicit `width="880"` and `height="420"` (matches SVG viewBox).
- Reusable HTML lives in `embeds/<slug>.md`; articles inline the same block after the first `##` section.

## Graphics

- News cards, timelines, bucket charts, and flow schematics only — **no AI faces, no child likenesses, no patient photos**.
- Palette: `assets/_shared/editorial-palette.md`.
- Every SVG includes accessible `<title>` and `<desc>`.
