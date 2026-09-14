# Image SEO — protein powder label literacy pack

Internal ops. Pair with `PHOTO_NOTES.md`, `RIGHTS.md`, and `GRAPHICS_INDEX.md`.

## `<figure>` contract (wired lessons)

Each wired `PSL-*.md` embeds:

```html
<figure class="blog-figure">
  <img src="../assets/…/file.svg" alt="…" width="720" height="…" loading="lazy" decoding="async" />
  <figcaption><strong>Figure.</strong> … <em>Original schematic; not a product label, clinical data, or a product claim.</em></figcaption>
</figure>
```

Rules:

1. **`alt`** — Describes the diagram for screen readers and image search. Name the document type (schematic, anatomy, sorting map). No disease-cure language. No “boost muscle” or “metabolic health” hype.
2. **`width` / `height`** — Match SVG `viewBox` to reduce layout shift.
3. **`loading="lazy"`** — Below-the-fold figures; lede figures may omit `lazy` if the publish theme tunes LCP on the first figure.
4. **`figcaption`** — One factual sentence plus the schematic disclaimer. Cite CFR parts when the figure teaches panel or claim rules (21 CFR 101.36, 101.54, 101.93).
5. **Keep `> **Photo:**` in the lesson body** — Wired lessons retain a one-line `> **Photo:**` block above the `<figure>` so `qa/verify_graphics.py` and editors still see a photo slot. The `<figure>` is the publish artifact.

## Front matter (wired set)

| YAML | Use |
| --- | --- |
| `featured_image` | Repo-relative path from pack root, e.g. `assets/supplement-facts-anatomy/facts-panel-anatomy.svg` |
| `figure_alt` | Duplicate of `img alt` for importers that do not parse HTML |

Do not auto-generate alt text from SEO plugins.

## Schema and OG

Use `Article` or `LearningResource` only. Do not attach `MedicalWebPage`, treatment, or indication schema to these lessons. Open Graph `og:image` should point at the same SVG or a PNG export — not unrelated stock gym photography.

## Banned visual SEO patterns

- Before/after bodies, swollen joints, glucose meters, or lab-number hero shots used as implied disease claims.
- Trademark seal collages (USP, NSF, Informed Sport) without a named enrolled lot and permission.
- Photorealistic tubs with invented brand names presented as real products.
- AI-generated faces, white-coat heroes, or “doctor formulated” stock.
- Schematics that quote disease treatment copy as if it were usable label text.
