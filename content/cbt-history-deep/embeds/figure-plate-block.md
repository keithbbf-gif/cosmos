# Embed — figure typographic plate (template)

Use after the educational note for `type: figure` when `portrait_status` is `typographic` or `placeholder`.

Never embed a raster likeness unless the row is cleared in pack `RIGHTS.md` and `PORTRAIT_SOURCES.md`.

```html
<!-- figure-id: SLUG.lead-plate -->
<figure class="wow-figure wow-figure--portrait wow-figure--portrait-typographic">
  <img
    src="../plates/SLUG/plate.svg"
    alt="ALT_TEXT"
    width="360"
    height="440"
    loading="lazy"
  />
  <figcaption>
    <strong>FULL_NAME</strong> (DATES) — SEO_SENTENCE
    <em>Typographic plate — no likeness embedded.</em>
    <span class="figure-credit">See <code>plates/SLUG/RIGHTS.md</code>.</span>
  </figcaption>
</figure>
```
