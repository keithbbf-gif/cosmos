# Embed — portrait figure block (template)

Use after the educational note in profile articles when `portrait_status: downloaded`.

Credit lines must match the sibling `assets/portraits/<portrait_id>.RIGHTS.md` and `PORTRAIT_SOURCES.md`.

```html
<!-- figure-id: SLUG.lead-portrait -->
<figure class="slpwow-figure slpwow-figure--portrait">
  <img
    src="../assets/portraits/PORTRAIT_ID.jpg"
    alt="ALT_TEXT"
    width="360"
    height="440"
    loading="lazy"
  />
  <figcaption>
    <strong>FULL_NAME</strong> (DATES). SEO_SENTENCE
    <span class="figure-credit">Photo: CREDIT_LINE</span>
  </figcaption>
</figure>
```

## Pending plate

When `portrait_status: placeholder`, use the verbatim placeholder block from `STYLE_GUIDE.md` — no `<figure>` until rights clear.
