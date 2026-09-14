# Image SEO — microbiome research literacy pack

Internal ops. Pair with `PHOTO_NOTES.md`, `RIGHTS.md`, and `GRAPHICS_INDEX.md`.

## `<figure>` contract (wired drafts)

Each wired draft embeds:

```html
<figure class="blog-figure">
  <img src="../assets/…/file.svg" alt="…" width="720" height="…" loading="lazy" decoding="async" />
  <figcaption><strong>Figure.</strong> … <em>Original schematic; not clinical data or a product claim.</em></figcaption>
</figure>
```

Rules:

1. **`alt`** — Describes the diagram for screen readers and image search. Name the document type (schematic, checklist, contrast). No disease cure language. No "boost gut health."
2. **`width` / `height`** — Match SVG `viewBox` to reduce layout shift.
3. **`loading="lazy"`** — Below-the-fold figures only; lede figures may omit lazy if WP theme requires LCP tuning.
4. **`figcaption`** — One factual sentence plus the schematic disclaimer. Cite the primary paper when the figure teaches nomenclature or guidelines (Zheng 2020; Su et al. 2020).
5. **Keep `**Photo:**` in YAML ops** — Wired drafts retain a one-line `> **Photo:**` block above the figure so `check_pack.py` still sees a photo slot. The `<figure>` is the publish artifact.

## Front matter (optional, wired set)

| YAML | Use |
| --- | --- |
| `featured_image` | Repo-relative path to SVG for WP featured media import |
| `figure_alt` | Duplicate of `img alt` for importers that do not parse HTML |

Do not auto-generate alt text from SEO plugins.

## Schema and OG

Use `Article` only. Do not attach `MedicalWebPage`, treatment, or indication schema to these posts. Open Graph `og:image` should point at the same SVG or a PNG export of it — not a unrelated stock photo.

## Banned visual SEO patterns

- AI-generated faces, white-coat heroes, glowing intestines.
- Trademark seal collages (USP, NSF) without a named enrolled lot.
- Rainbow diversity sunbursts presented as clinical truth.
- Unredacted third-party COAs or real customer microbiome dashboards.
