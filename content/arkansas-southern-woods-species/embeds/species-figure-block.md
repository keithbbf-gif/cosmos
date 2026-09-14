# Embed — species `<figure>` blocks (Arkansas / Southern woods)

Paths are relative from `NN-slug.md` → `plates/<plate_id>/…`

## Cleared plate (botanical photograph or PD illustration)

```html
<figure class="asw-figure asw-figure--species">
  <img
    src="plates/PLATE_ID/plate.jpg"
    alt="ALT_TEXT"
    width="720"
    height="480"
    loading="lazy"
  />
  <figcaption>
    <strong>SPECIES_COMMON</strong> (<em>SPECIES_LATIN</em>) — SEO_SENTENCE
    <span class="figure-credit">CREDIT_LINE</span>
  </figcaption>
</figure>
```

Use `plate.png` when the on-disk file is PNG. Match `plates/<id>/RIGHTS.md`.

## Diagram plate

```html
<figure class="asw-figure asw-figure--diagram">
  <img
    src="assets/diagrams/DIAGRAM.svg"
    alt="ALT_TEXT"
    width="900"
    height="420"
    loading="lazy"
  />
  <figcaption>
    <strong>CAPTION_TITLE</strong> — SEO_SENTENCE
    <span class="figure-credit">Original diagram for the Arkansas / Southern woods series.</span>
  </figcaption>
</figure>
```

Caption must name the **species** or **shop fact** the image supports (hardness, shrink, sawing, tyloses). Do not use generic “wood image” alt text.
