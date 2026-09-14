# SEO map — figures and alt text

Rules for WordPress import (`WP_IMPORT.md`). **Draft posts only.**

## HTML contract

- Use `<figure class="faj-figure">` for pack schematics.
- Use `faj-figure faj-museum` for Commons/Met rasters.
- Use `faj-figure faj-shop-pending` until a `D:\BBF` file replaces the placeholder `<img>`.
- Every figure: `loading="lazy"`, `decoding="async"`, explicit `width` / `height`, unique `alt`, numbered `<figcaption>`.

## Alt-text pattern

1. **Schematic:** describe the joint geometry (from `graphics[].alt` in front matter).
2. **Museum:** object type + institution + what the essay uses it for (from `assignments` in `museum_sources.yaml`).
3. **Shop pending:** use `figures[].caption`; include joint name and dry-fit/assembled state.

Banned alt filler: “woodworking”, “furniture image”, “stock photo”, “AI”.

## Focus phrases (light touch — no stuffing)

| topic cluster | phrase hints for figcaption lead |
| --- | --- |
| `compound-dovetails` | compound dovetail, secret miter, hopper joint, houndstooth |
| `curved-work` | steam bend, coopered, brick-laid, kerf bend, scribed shoulder |
| `knockdown` | tusk tenon, bed bolt, campaign hardware, 32 mm system, cam lock |
| `hybrid` | brick-laid corner, fox wedge, compound bridle |

## Per-slug cautions

| slug | SEO / ethics note |
| --- | --- |
| `iron-under-a-slab` | No epoxy-river hero imagery; figcaption must stay slab + figure-eight / movement. |
| `brass-on-a-travel-chest` | Museum plate is type context until a rights-cleared campaign chest photo exists. |
| `a-tusk-you-can-pull` | Met trestle ≠ tusk hardware; figcaption already says hardware may differ. |
| `thirty-two-and-the-hole` | Honest system furniture — do not imply hand-cut dovetail craft for Euro holes. |

## Featured image

Do not set WordPress featured image to a placeholder. First choice when publishing: shop `fig-01` after BBF pull; until then, schematic SVG is acceptable for staging previews only.
