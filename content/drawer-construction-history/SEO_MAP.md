# SEO map — figures and alt text

Rules for WordPress import (`WP_IMPORT.md`). **Draft posts only.**

## HTML contract

- Use `<figure class="dch-figure">` for pack joinery schematics (Figure 1).
- Use `dch-figure dch-shop-pending` until a `D:\BBF` file replaces the placeholder `<img>` (Photos 2–3).
- Every figure: `loading="lazy"`, `decoding="async"`, explicit `width` / `height`, unique `alt`, numbered `<figcaption>`.
- Keep `figures[].status: needed` in front matter until a real BBF file is attached.

## Alt-text pattern

1. **Schematic (Figure 1):** joint geometry from `graphics[].alt` / `dch_graphics_specs.json` `desc`.
2. **Shop pending (Photos 2–3):** use `figures[].caption`; name the joint, runner, or hardware the essay argues about; include dry-fit or assembled state when the caption does.

Banned alt filler: “woodworking”, “furniture image”, “stock photo”, “AI”, “drawer history”.

## Focus phrases (light touch — no stuffing)

| `topic` | phrase hints for figcaption lead |
| --- | --- |
| `dating-trade` | side-hung groove, London slip, Knapp joint, machine dovetail, cockbead |
| `the-box` | half-blind front, tails on sides, drawer slip, bottom grain, hide glue |
| `case-and-fit` | web frame, kicker, runner, plane to opening, wax on runner |
| `tradition-hardware` | Shaker knob, campaign corner, undermount slide, mortise lock, pull load |

## Per-slug cautions

| slug | SEO / ethics note |
| --- | --- |
| `seasonal-bind-is-a-drawing-error` | Do not retell `the-drawer-that-does-not-bind` from the craft pack; figcaption stays drawing error / clearance. |
| `a-router-bit-named-drawer-lock` | Say kitchen / production; do not imply 18th-century reproduction. |
| `french-dovetail-is-a-kitchen-word` | Kitchen box habit — not a Federal show-face claim. |
| `arts-and-crafts-shows-the-tails` | Through tails as intentional show joinery — not ordinary case work. |
| `plywood-bottoms-are-a-contract` | Honest contract language — not “premium solid” marketing. |

## Featured image

Do not set WordPress featured image to `bbf-shop-pending.svg`. First choice when publishing: shop `fig-01` after BBF pull; until then, schematic SVG is acceptable for staging previews only.
