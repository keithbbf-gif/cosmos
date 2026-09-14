# Embed — plate figure block (template)

Credit lines must match `plates/<slug>/RIGHTS.md` and `PLATE_SOURCES.md`.

```html
<!-- figure-id: SLUG.lead-plate -->
<figure class="bbf-figure bbf-figure--plate">
  <img
    src="../plates/SLUG/plate.jpg"
    alt="ALT_TEXT"
    width="720"
    height="480"
    loading="lazy"
  />
  <figcaption>
    <strong>OBJECT_LABEL</strong>, DATE — SEO_SENTENCE
    <span class="figure-credit">CREDIT_LINE</span>
  </figcaption>
</figure>
```
