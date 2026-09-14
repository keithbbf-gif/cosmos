# Figure SEO — label literacy pack

Staging import only. Figures support **Article** discovery and accessibility; they are not product claims.

## Markup contract

Use HTML in Markdown at the first relevant H2 (or immediately after the disclaimer when the figure is the panel walk):

```html
<figure class="blog-figure">
  <img src="../assets/svg/example.svg"
       alt="Describe structure: fictional Supplement Facts panel with (b)(2) above hairline"
       width="900" height="480" loading="lazy" />
  <figcaption><strong>Figure.</strong> One sentence tying the diagram to 21 CFR section. <em>Original typeset diagram; fictional panel — not a real product label.</em></figcaption>
</figure>
```

Rules:

- **`alt`** — structure and regulation reference; no trust or efficacy adjectives (`PHOTO_NOTES.md`).
- **`figcaption`** — starts with **Figure.**; cites CFR or guide section when possible; italic disclaimer line matches `RIGHTS.md`.
- **`loading="lazy"`** — always on in-body figures.
- **`width` / `height`** — match SVG `viewBox` to reduce layout shift.

Do **not** emit `MedicalWebPage`, `Drug`, or `treats` schema. If the CMS adds `ImageObject`, point `contentUrl` at the same SVG path and reuse `figure_alt` as `description`.

## YAML → WordPress / SEO plugins

| YAML | Use |
| --- | --- |
| `figure_alt` | Featured image alt text; social/Open Graph description for the hero diagram; must match in-body `alt` when the post has one primary figure. |
| `og_image` | Path relative to this pack root, e.g. `assets/svg/panel-walk-anatomy.svg`. Map to featured media on staging. Do not let plugins pick stock art. |

Keep `meta_description` as the **text** summary. Do not duplicate `figure_alt` into `meta_description` unless they serve different intents (text vs diagram).

## Inventory

See `GRAPHICS_INDEX.md` for article ↔ SVG mapping.

Verify before merge:

```bash
python3 tools/verify_graphics.py
python3 check_pack.py
```
